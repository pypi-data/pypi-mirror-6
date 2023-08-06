"""Tests for parsing the JSON output from the eBird API."""

from unittest import TestCase

from checklists_scrapers.spiders import CHECKLISTS_DOWNLOAD_FORMAT, \
    CHECKLISTS_DOWNLOAD_LANGUAGE
from checklists_scrapers.spiders.ebird_spider import JSONParser
from checklists_scrapers.tests.utils import response_for_data


class JSONParserTestCase(TestCase):
    """Verify the checklists extracted from the API JSON data."""

    def setUp(self):
        """Initialize the test."""
        self.data = [{
            'checklistID': 'CL00001',
            'comName': 'Common Name',
            'countryCode': 'CC',
            'countryName': 'Country',
            'firstName': 'Name',
            'howMany': 1,
            'lastName': 'Surname',
            'lat': 45.000001,
            'lng': -45.000001,
            'locID': 'L0000001',
            'locName': 'Location 1',
            'locationPrivate': True,
            'obsDt': '2013-03-27',
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
        }, {
            'checklistID': 'CL00002',
            'comName': 'Common Name',
            'countryCode': 'CC',
            'countryName': 'Country',
            'firstName': 'Name',
            'howMany': 2,
            'lastName': 'Surname',
            'lat': 50.000000,
            'lng': -50.000000,
            'locID': 'L0000002',
            'locName': 'Location 2',
            'locationPrivate': True,
            'obsDt': '2013-03-27 10:00',
            'obsID': 'OBS0000003',
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
        self.response = response_for_data(self.data)
        self.parser = JSONParser(self.response)

    def test_checklist_count(self):
        """Verify the number of checklists extracted."""
        checklists = self.parser.get_checklists()
        self.assertEqual(2, len(checklists))

    def test_checklist_ids(self):
        """Verify the ids of each checklist."""
        checklists = self.parser.get_checklists()
        self.assertEqual('S0000001', checklists[0]['identifier'])
        self.assertEqual('S0000002', checklists[1]['identifier'])

    def test_location_count(self):
        """Verify the number of locationss extracted from the data."""
        locations = self.parser.get_locations()
        self.assertEqual(2, len(locations))

    def test_location_ids(self):
        """Verify the ids of each location."""
        locations = self.parser.get_locations()
        self.assertEqual('L0000001', locations[0]['identifier'])
        self.assertEqual('L0000002', locations[1]['identifier'])

    def test_entry_counts(self):
        """Verify the number of checklists extracted from the data."""
        checklists = self.parser.get_checklists()
        self.assertEqual(1, len(checklists[0]['entries']))
        self.assertEqual(2, len(checklists[1]['entries']))

    def test_entry_ids(self):
        """Verify the ids of each checklist entry."""
        checklists = self.parser.get_checklists()
        self.assertEqual('OBS0000001',
                         checklists[0]['entries'][0]['identifier'])
        self.assertEqual('OBS0000002',
                         checklists[1]['entries'][0]['identifier'])
        self.assertEqual('OBS0000003',
                         checklists[1]['entries'][1]['identifier'])

    def test_get_checklist(self):
        """Verify the complete checklist is extracted from the record.

        Only the top-level fields are checked. The location and prootcol are
        removed as the fields are covered in the test_get_location and
        test_get_protocol tests respectively.
        """
        actual = self.parser.get_checklist(self.data[1])
        del actual['location']
        del actual['protocol']
        del actual['source']
        del actual['observers']

        expected = {
            'meta': {
                'version': CHECKLISTS_DOWNLOAD_FORMAT,
                'language': CHECKLISTS_DOWNLOAD_LANGUAGE,
            },
            'identifier': 'S0000002',
            'date': '2013-03-27',
        }
        self.assertEqual(expected, actual)

    def test_get_location(self):
        """Verify the location fields are extracted from the record."""
        actual = self.parser.get_location(self.data[0])
        expected = {
            'identifier': 'L0000001',
            'name': 'Location 1',
            'county': 'County',
            'region': 'Region',
            'country': 'Country',
            'lat': 45.000001,
            'lon': -45.000001,
        }
        self.assertEqual(expected, actual)

    def test_get_observers(self):
        """Verify the observer name is extracted from the record."""
        actual = self.parser.get_observers(self.data[0])
        expected = {
            'count': 1,
            'names': ['Name Surname'],
        }
        self.assertEqual(expected, actual)

    def test_get_source(self):
        """Verify the source fields are extracted from the record."""
        actual = self.parser.get_source(self.data[0])
        expected = {
            'submitted_by': 'Name Surname',
            'name': 'eBird',
        }
        self.assertEqual(expected, actual)

    def test_get_protocol(self):
        """Verify the protocol fields are extracted from the record."""
        actual = self.parser.get_protocol(self.data[1])
        expected = {
            'name': 'Incidental',
            'time': '10:00',
        }
        self.assertEqual(expected, actual)

    def test_protocol_not_set(self):
        """Verify protocol is not included if not time is given."""
        actual = self.parser.get_checklist(self.data[0])
        self.assertFalse('protocol' in actual)

    def test_get_species(self):
        """Verify the species fields are extracted from the record."""
        actual = self.parser.get_species(self.data[0])
        expected = {
            'name': 'Common Name',
            'scientific_name': 'Scientific Name',
        }
        self.assertEqual(expected, actual)

    def test_get_entry(self):
        """Verify the entry is extracted from the record."""
        actual = self.parser.get_entry(self.data[0])
        expected = {
            'identifier': 'OBS0000001',
            'species': {
                'name': 'Common Name',
                'scientific_name': 'Scientific Name',
            },
            'count': 1,
        }
        self.assertEqual(expected, actual)
