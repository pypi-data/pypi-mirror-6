"""Tests for parsing the observations for a location from the eBird API."""

from unittest import TestCase

from scrapy.crawler import Crawler
from scrapy.settings import CrawlerSettings

from checklists_scrapers import settings
from checklists_scrapers.spiders import ebird_spider
from checklists_scrapers.tests.utils import response_for_data


class ParseLocationsTestCase(TestCase):
    """Verify the requests generated when parsing the location records."""

    def setUp(self):
        """Initialize the test."""
        crawler = Crawler(CrawlerSettings(settings))
        crawler.configure()
        self.spider = ebird_spider.EBirdSpider('REG')
        self.spider.set_crawler(crawler)
        self.spider.start_requests()
        self.records = [{
            'checklistID': 'CL00001',
            'comName': 'Common Name',
            'countryCode': 'CC',
            'countryName': 'Country',
            'firstName': 'Name',
            'howMany': 1,
            'lastName': 'Surname',
            'lat': 45.000000,
            'lng': -45.000000,
            'locID': 'L0000001',
            'locName': 'Location 1',
            'locationPrivate': True,
            'obsDt': '2013-03-27 09:00',
            'obsID': 'OBS0000001',
            'obsReviewed': False,
            'obsValid': True,
            'presenceNoted': False,
            'sciName': 'Scientific Name',
            'subID': 'S0000001',
            'subnational1Code': 'SN-01',
            'subnational1Name': 'Region',
            'subnational2Code': 'SN-02',
            'subnational2Name': 'County',
        }, {
            'checklistID': 'CL00002',
            'comName': 'Common Name',
            'countryCode': 'CC',
            'countryName': 'Country',
            'firstName': 'Name',
            'howMany': 1,
            'lastName': 'Surname',
            'lat': 50.000000,
            'lng': -50.000000,
            'locID': 'L0000002',
            'locName': 'Location 2',
            'locationPrivate': True,
            'obsDt': '2013-03-27 10:00',
            'obsID': 'OBS0000002',
            'obsReviewed': False,
            'obsValid': True,
            'presenceNoted': False,
            'sciName': 'Scientific Name',
            'subID': 'S0000002',
            'subnational1Code': 'SN-01',
            'subnational1Name': 'Region',
            'subnational2Code': 'SN-02',
            'subnational2Name': 'County',
        }]

    def test_request_count(self):
        """Verify a request is generated for each checklist."""
        response = response_for_data(self.records)
        results = self.spider.parse_locations(response)
        self.assertEqual(2, sum(1 for _ in results))

    def test_request_unique(self):
        """Verify only one request is generated for each checklist."""
        records = [self.records[0], self.records[0]]
        records[1]['obsID'] = 'OBS0000002'
        response = response_for_data(records)
        results = self.spider.parse_locations(response)
        self.assertEqual(1, sum(1 for _ in results))

    def test_request_url(self):
        """Verify the URL contains the ID for each checklist."""
        response = response_for_data([self.records[0]])
        results = self.spider.parse_locations(response)
        expected = self.spider.checklist_url % 'S00000001'
        self.assertTrue(results.next().url, expected)

    def test_request_callbacks(self):
        """Verify the callbacks for parsing the HTML pages."""
        response = response_for_data([self.records[0]])
        results = self.spider.parse_locations(response)
        expected = self.spider.parse_checklist
        self.assertEqual(results.next().callback, expected)

    def test_request_checklist(self):
        """Verify the metadata for the request contains the checklist."""
        response = response_for_data([self.records[0]])
        results = self.spider.parse_locations(response)
        self.assertTrue(results.next().meta['checklist'])


class IncludeHTMLTestCase(TestCase):
    """Verify include_html attribute controls web page requests."""

    def setUp(self):
        """Initialize the test."""
        self.records = [{
            'checklistID': 'CL00001',
            'comName': 'Common Name',
            'countryCode': 'CC',
            'countryName': 'Country',
            'firstName': 'Name',
            'howMany': 1,
            'lastName': 'Surname',
            'lat': 45.000000,
            'lng': -45.000000,
            'locID': 'L0000001',
            'locName': 'Location 1',
            'locationPrivate': True,
            'obsDt': '2013-03-27 09:00',
            'obsID': 'OBS0000001',
            'obsReviewed': False,
            'obsValid': True,
            'presenceNoted': False,
            'sciName': 'Scientific Name',
            'subID': 'S0000001',
            'subnational1Code': 'SN-01',
            'subnational1Name': 'Region',
            'subnational2Code': 'SN-02',
            'subnational2Name': 'County',
        }, {
            'checklistID': 'CL00002',
            'comName': 'Common Name',
            'countryCode': 'CC',
            'countryName': 'Country',
            'firstName': 'Name',
            'howMany': 1,
            'lastName': 'Surname',
            'lat': 50.000000,
            'lng': -50.000000,
            'locID': 'L0000002',
            'locName': 'Location 2',
            'locationPrivate': True,
            'obsDt': '2013-03-27 10:00',
            'obsID': 'OBS0000002',
            'obsReviewed': False,
            'obsValid': True,
            'presenceNoted': False,
            'sciName': 'Scientific Name',
            'subID': 'S0000002',
            'subnational1Code': 'SN-01',
            'subnational1Name': 'Region',
            'subnational2Code': 'SN-02',
            'subnational2Name': 'County',
        }]

    def test_skip_parsing_webpages(self):
        """Verify no web requests are made if include_html is False."""
        crawler = Crawler(CrawlerSettings(settings))
        crawler.configure()
        spider = ebird_spider.EBirdSpider('REG')
        spider.set_crawler(crawler)
        spider.start_requests()
        spider.include_html = False

        response = response_for_data(self.records)
        results = spider.parse_locations(response)
        self.assertEqual(0, sum(1 for _ in results))
