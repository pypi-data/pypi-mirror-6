"""Tests for parsing the WorldBirds page containing the list of visits."""

from datetime import datetime

from unittest import TestCase

from checklists_scrapers.spiders.worldbirds_spider import VisitParser
from checklists_scrapers.tests.utils import response_for_content


class VisitParserTestCase(TestCase):
    """Verify the spider can extract data from the list of visits."""

    def setUp(self):
        """Initialize the test."""
        self.response = response_for_content("""
        <table width="100%" border="0" cellspacing="0" class="StandardTable">
        <th align="left">&nbsp;</th>
        <th align="left">Location</th>
        <th align="left">Region</th>
        <th align="left">Date</th>
        <th align="left">Observer</th>
        <th align="center">Info</th>
        <tr id="HighlightRow">
        <td>1.</td>
        <td align="left">
        <a onclick="doLocation(1);" href="javascript:void(0);">Location A</a>
        </td>
        <td align="left">Region</td>
        <td align="left">23/05/2013</td>
        <td align="left">
        <a onclick="doObserver(2);" href="javascript:void(0);">username_a</a>
        </td>
        <td align="center">
        <a onclick="doHighlights(1, 3, 0, 0);" href="javascript:void(0);">
        <img src="images/theme_blue/more.gif">
        </a>
        </td>
        </tr>
        <tr>
        <td>2.</td>
        <td align="left">
        <a onclick="doLocation(5);" href="javascript:void(0);">Location B</a>
        </td>
        <td align="left">Region</td>
        <td align="left">22/05/2013</td>
        <td align="left">
        <a onclick="doObserver(6);" href="javascript:void(0);">username_b</a>
        </td>
        <td align="center">
        <a onclick="doHighlights(1, 4, 0, 0);" href="javascript:void(0);">
        <img src="images/theme_blue/more.gif">
        </a>
        </td>
        </tr>
        </table>
        """, 'utf-8')
        self.parser = VisitParser(self.response)

    def test_checklist_id_count(self):
        """Verify the number of checklist ids extracted."""
        self.assertEqual(2, len(self.parser.get_checklists()))

    def test_checklist_ids(self):
        """Verify checklist ids extracted."""
        self.assertEqual([3, 4], self.parser.get_checklists())

    def test_location_id_count(self):
        """Verify the number of location ids extracted."""
        self.assertEqual(2, len(self.parser.get_locations()))

    def test_checklist_ids(self):
        """Verify location ids extracted."""
        self.assertEqual([1, 5], self.parser.get_locations())

    def test_observer_id_count(self):
        """Verify the number of observer ids extracted."""
        self.assertEqual(2, len(self.parser.get_observers()))

    def test_observer_ids(self):
        """Verify observer ids extracted."""
        self.assertEqual([2, 6], self.parser.get_observers())

    def test_dates(self):
        """Verify dates extracted."""
        expected = [datetime(2013, 5, 23), datetime(2013, 5, 22)]
        self.assertEqual(expected, self.parser.get_dates())
