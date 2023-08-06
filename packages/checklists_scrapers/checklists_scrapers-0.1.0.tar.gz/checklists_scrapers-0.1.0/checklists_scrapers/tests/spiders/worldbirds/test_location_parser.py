"""Tests for parsing the WorldBirds panel containing the location details."""

from unittest import TestCase

from checklists_scrapers.spiders.worldbirds_spider import LocationParser
from checklists_scrapers.tests.utils import response_for_content


class LocationParserTestCase(TestCase):
    """Verify the spider can extract data from the location details."""

    def setUp(self):
        """Initialize the test."""
        data = {
            'location': {
                'name': 'Location A',
            }
        }
        self.response = response_for_content(u"""
        <table cellspacing="0" class="PopupTable">
        <tr>
          <td colspan="2"><label>Location name</label></td>
          <td>Location A</td>
        </tr>
        <tr>
          <td colspan="2"><label>Region</label></td>
          <td>Country</td>
        </tr>
        <tr>
          <td colspan="2"><label>Central co-ordinates</label></td>
          <td>45.0000, -45.0000</td>
        </tr>
        <tr>
          <td colspan="2"><label>Area</label></td>
          <td>0ha</td></tr>
        <tr>
          <td colspan="2"><label>Altitude</label></td>
          <td>0m - 0m</td>
        </tr>
        <tr>
          <td colspan="2"><label>Notes</label></td>
          <td></td>
        </tr>
        <tr>
          <td colspan="2"><br><a target="_parent" href="locationreport.php?id=1&amp;so=3">Run Location Report</a></td>
        </tr>
        <tr>
          <td width="5%"><br>
            <a onclick="doGoogleLocation(1)" href="#">
              <img src="images/theme_blue/map.gif">
            </a>
          </td>
          <td><br><a onclick="doGoogleLocation(1)" href="#">Google</a></td>
          <td>&nbsp;</td>
        </tr>
        </table>
        """, 'utf-8', metadata={'checklist': data, 'identifiers': (1, 2, 3),
                                'country': 'pt'})
        self.parser = LocationParser(self.response)
        self.checklist = self.parser.get_checklist()
        self.location = self.checklist['location']

    def test_location_identifier(self):
        """Verify the latitude is extracted."""
        self.assertEqual('PT2', self.location['identifier'])

    def test_location_country(self):
        """Verify the latitude is extracted."""
        self.assertEqual('Country', self.location['country'])

    def test_location_latitude(self):
        """Verify the latitude is extracted."""
        self.assertEqual(45.0, self.location['lat'])

    def test_location_latitude(self):
        """Verify the longitude is extracted."""
        self.assertEqual(-45.0, self.location['lon'])
