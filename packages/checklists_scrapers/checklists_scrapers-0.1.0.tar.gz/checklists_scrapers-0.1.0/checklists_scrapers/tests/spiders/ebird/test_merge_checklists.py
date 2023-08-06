"""Tests for merging the checklists parsed from JSON and HTML together."""

from unittest import TestCase

from scrapy.crawler import Crawler
from scrapy.settings import CrawlerSettings

from checklists_scrapers import settings
from checklists_scrapers.spiders import ebird_spider


class MergeChecklistsTestCase(TestCase):
    """Verify merging the JSON and HTML checklists together."""

    def setUp(self):
        """Initialize the test."""
        crawler = Crawler(CrawlerSettings(settings))
        crawler.configure()
        self.spider = ebird_spider.EBirdSpider('REG')
        self.spider.set_crawler(crawler)
        self.lista = {
            'meta': {
                'version': 1,
                'language': 'en',
            },
            'identifier': 'S0000001',
            'date': '2013-03-27',
            'protocol': {
                'time': '09:00',
            },
            'observers': {
                'names': ['Name Surname'],
                'count': 1,
            },
            'source': {
                'name': 'eBird',
                'submitted_by': 'Name Surname',
            },
            'location': {
                'identifier': 'L0000001',
                'name': 'Location 1',
                'county': 'County',
                'region': 'Region',
                'country': 'Country',
                'lat': 45.0,
                'lon': -45.0,
            },
            'entries': [
                {
                    'identifier': 'OBS0000001',
                    'species': {
                        'name': 'Common Name',
                    },
                    'count': 23
                }
            ]
        }
        self.listb = {
            'meta': {
                'version': 1,
                'language': 'en',
            },
            'source': 'ebird',
            'url': 'http://ebird.org/',
            'observers': {
                'names': ['Other Name'],
                'count': 1,
            },
            'activity': 'Birding',
            'protocol': {
                'name': 'Traveling',
                'duration_hours': 2,
                'duration_minutes': 35,
                'distance': 2000,
                'area': 0,
            },
            'comment': 'A comment',
            'entries': [
                {
                    'species': {
                        'name': 'Common Name',
                    },
                    'count': 23,
                    'details': [
                        {'age': 'AD', 'sex': 'M', 'count': 9},
                        {'age': 'AD', 'sex': 'F', 'count': 6},
                        {'age': 'JUV', 'sex': 'X', 'count': 8}
                    ]
                }
            ]
        }

        self.fixture = self.spider.merge_checklists(self.lista, self.listb)

    def test_activity(self):
        """Verify the activity is included in the merged checklist."""
        self.fixture = self.spider.merge_checklists(self.lista, self.listb)
        self.assertTrue('activity' in self.fixture)

    def test_protocol(self):
        """Verify the protocol is set."""
        self.fixture = self.spider.merge_checklists(self.lista, self.listb)
        expected = {
            'name': 'Traveling',
            'time': '09:00',
            'duration_hours': 2,
            'duration_minutes': 35,
            'distance': 2000,
            'area': 0,
        }
        self.assertEqual(expected, self.fixture['protocol'])

    def test_observers(self):
        """Verify the observers are merged."""
        self.fixture = self.spider.merge_checklists(self.lista, self.listb)
        expected = {
            'count': 2,
            'names': ['Name Surname', 'Other Name'],
        }
        self.assertEqual(expected, self.fixture['observers'])

    def test_details(self):
        """Verify the entry details are set."""
        self.fixture = self.spider.merge_checklists(self.lista, self.listb)
        expected = [
            {'age': 'AD', 'sex': 'M', 'count': 9},
            {'age': 'AD', 'sex': 'F', 'count': 6},
            {'age': 'JUV', 'sex': 'X', 'count': 8},
        ]
        self.assertEqual(expected, self.fixture['entries'][0]['details'])

    def test_entry_added(self):
        """Verify new entries in the second list are added."""
        self.listb['entries'].append({
            'species': {
                'name': 'New Name',
            },
            'count': 10,
            'details': []
        })
        self.fixture = self.spider.merge_checklists(self.lista, self.listb)
        self.assertEqual(2, len(self.fixture['entries']))


class MergeEntriesTestCase(TestCase):
    """Verify merging the entries from JSON and HTML checklists together."""

    def setUp(self):
        """Initialize the test."""
        settings.LOG_LEVEL = 'DEBUG'
        crawler = Crawler(CrawlerSettings(settings))
        crawler.configure()
        self.spider = ebird_spider.EBirdSpider('REG')
        self.spider.set_crawler(crawler)

    def test_species_updated(self):
        """Verify the species is updated when only a single record exists."""
        lista = [{
            'identifier': 'OBS1',
            'species': {
                'name': 'Barn Swallow',
            },
            'count': 1
        }]
        listb = [{
            'species': {
                'name': 'Barn Swallow (White-bellied)',
            },
            'count': 1,
        }]
        entries, warnings = self.spider.merge_entries(lista, listb)
        self.assertEqual('Barn Swallow (White-bellied)',
                         entries[0]['species']['name'])

    def test_species_updated_without_warnings(self):
        """Verify no warnings are generated when an entry is updated."""
        lista = [{
            'identifier': 'OBS1',
            'species': {
                'name': 'Barn Swallow',
            },
            'count': 1
        }]
        listb = [{
            'species': {
                'name': 'Barn Swallow (White-bellied)',
            },
            'count': 1,
        }]
        entries, warnings = self.spider.merge_entries(lista, listb)
        self.assertFalse(warnings)


    def test_species_not_updated(self):
        """Verify the species is not updated when multiple records exist."""
        lista = [{
            'identifier': 'OBS1',
            'species': {
                'name': 'Barn Swallow',
            },
            'count': 1
        }, {
            'identifier': 'OBS2',
            'species': {
                'name': 'Barn Swallow',
            },
            'count': 1
        }]
        listb = [{
            'species': {
                'name': 'Barn Swallow (White-bellied)',
            },
            'count': 1,
        }]

        entries, warnings = self.spider.merge_entries(lista, listb)
        actual = [entry['species']['name'] for entry in entries]
        expected = [entry['species']['name'] for entry in lista]
        self.assertEqual(expected, actual)

    def test_no_update_warning(self):
        """Verify a warning is updated when multiple entries match."""
        lista = [{
            'identifier': 'OBS1',
            'species': {
                'name': 'Barn Swallow',
            },
            'count': 1
        }, {
            'identifier': 'OBS2',
            'species': {
                'name': 'Barn Swallow',
            },
            'count': 1
        }]
        listb = [{
            'species': {
                'name': 'Barn Swallow (White-bellied)',
            },
            'count': 1,
        }]

        entries, warnings = self.spider.merge_entries(lista, listb)
        self.assertTrue("Could not update record from API." in warnings[0])

    def test_missing_record_added(self):
        """Verify records that exist only on the web page are added."""
        lista = [{
            'identifier': 'OBS1',
            'species': {
                'name': 'Barn Swallow',
            },
            'count': 1
        }]
        listb = [{
            'species': {
                'name': 'Barn Swallow (White-bellied)',
            },
            'count': 2,
        }]
        entries, warnings = self.spider.merge_entries(lista, listb)
        actual = [entry['species']['name'] for entry in entries]
        expected = ['Barn Swallow', 'Barn Swallow (White-bellied)']
        self.assertEqual(expected, actual)

    def test_added_record_warning(self):
        """Verify a warning is generated when a new entry is added."""
        lista = [{
            'identifier': 'OBS1',
            'species': {
                'name': 'Barn Swallow',
            },
            'count': 1
        }]
        listb = [{
            'species': {
                'name': 'Cliff Swallow',
            },
            'count': 2,
        }]
        entries, warnings = self.spider.merge_entries(lista, listb)
        self.assertTrue('Web page contains record missing from API'
                        in warnings[0])
