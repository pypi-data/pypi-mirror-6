"""Tests for parsing the observations for a region from the eBird API."""

from unittest import TestCase

from scrapy.crawler import Crawler
from scrapy.settings import CrawlerSettings

from checklists_scrapers import settings
from checklists_scrapers.spiders import ebird_spider
from checklists_scrapers.tests.utils import response_for_data


class ParseRegionTestCase(TestCase):
    """Verify the requests generated when parsing the region records."""

    def setUp(self):
        """Initialize the test."""
        crawler = Crawler(CrawlerSettings(settings))
        crawler.configure()
        self.spider = ebird_spider.EBirdSpider('REG')
        self.spider.set_crawler(crawler)
        self.spider.start_requests()

    def test_request_count(self):
        """Verify one request is generated for each location."""
        response = response_for_data([
            {
                'locID': 'L0000001',
                'locName': 'Location1',
                'lat': '',
                'lng': '',
            },
            {
                'locID': 'L0000002',
                'locName': 'Location2',
                'lat': '',
                'lng': '',
            },
        ])
        results = self.spider.parse_region(response)
        self.assertEqual(2, sum(1 for _ in results))

    def test_request_url(self):
        """Verify the URL contains the ID for each location."""
        response = response_for_data([
            {
                'locID': 'L0000001',
                'locName': 'Location1',
                'lat': '',
                'lng': '',
            },
        ])
        results = self.spider.parse_region(response)
        expected = self.spider.location_url % ('L00000001', 7)
        self.assertTrue(results.next().url, expected)

    def test_request_callbacks(self):
        """Verify the callbacks for parsing the location observations."""
        response = response_for_data([
            {
                'locID': 'L0000001',
                'locName': 'Location1',
                'lat': '',
                'lng': '',
            },
        ])
        results = self.spider.parse_region(response)
        self.assertEqual(results.next().callback, self.spider.parse_locations)

    def test_unique_locations(self):
        """Verify one request is generated for each unique location."""
        response = response_for_data([
            {
                'locID': 'L0000001',
                'locName': 'Location1',
                'lat': '',
                'lng': '',
            },
            {
                'locID': 'L0000001',
                'locName': 'Location1',
                'lat': '',
                'lng': '',
            },
        ])
        results = self.spider.parse_region(response)
        self.assertEqual(1, sum(1 for _ in results))
