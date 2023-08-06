"""Tests for parsing the WorldBirds page containing the checklist."""
from datetime import datetime
from unittest import TestCase

from checklists_scrapers.spiders import CHECKLISTS_DOWNLOAD_FORMAT, \
    CHECKLISTS_DOWNLOAD_LANGUAGE
from checklists_scrapers.spiders.worldbirds_spider import ChecklistParser
from checklists_scrapers.tests.utils import response_for_content


class ChecklistParserTestCase(TestCase):
    """Verify the spider can extract data from the checklist page."""

    def setUp(self):
        """Initialize the test."""
        self.response = response_for_content("""
        <div id="popupwrapper" style="width: 600px; height: 370px; top: 160px; left: 533.5px;">
        <div id="popupheader" style="width: 600px;">
            <a href="javascript:doShowInfo(false,%200,%200,%200);">
                <div id="ico_close"></div>
            </a>
        </div>
        <div id="popupscroll" style="width: 600px; height: 350px;">
        <div id="popupbody" style="width: 560px;"><p></p>
        <div id="popupcontent"><br>
        <table cellspacing="0" class="PopupTable">
        <tr>
          <td width="60%"><label>Location</label></td>
          <td width="40%">Location A</td></tr>
        <tr>
          <td><label>Region</label></td>
          <td>Region A</td>
        </tr>
        <tr>
          <td><label>Start date</label></td>
          <td>23-05-2013</td>
        </tr>
        <tr>
          <td><label>Time</label></td>
          <td>11:00 - 12:05</td>
        </tr>
        <tr>
          <td><label>Time spent birding</label></td>
          <td>1 Hrs 5 Mins</td>
        </tr>
        <tr>
          <td><label>Observers</label></td>
          <td>1</td>
        </tr>
        <tr>
          <td><label>Were all birds seen recorded?</label></td>
          <td><img src="images/theme_blue/tick.gif"></td>
        </tr>
        <tr>
          <td><label>Were no birds seen?</label></td>
          <td><img src="images/theme_blue/cross.gif"></td>
        </tr>
        <tr>
          <td><label>Did weather, visibility, disturbance etc affect your counts?</label></td>
          <td><img src="images/theme_blue/cross.gif"></td>
        </tr>
        <tr>
          <td><label>Purpose</label></td>
          <td>Birdwatching, with no specific purpose</td><td></td>
        </tr>
        <tr valign="top">
          <td><label>Other notes for the visit</label></td>
          <td></td>
          <td></td>
        </tr>
        <tr valign="top">
          <td><label>Observers</label></td>
          <td>Observer A, Observer B</td><td></td>
        </tr>
        <tr>
          <td><label>Total species observed during visit</label></td>
          <td>3 <a ;="" onclick="doHighlights(1, 00001, 0, 0)" href="javascript:void(0);">Hide list</a></td>
        </tr>
        </table>
        <br><br>
        <b>Confidential entries are hidden from the list displayed below.</b><br><br>
        <table cellspacing="0" class="TableThin">
        <tr>
          <th width="30%" align="left">Species</th>
          <th width="10%">Count</th>
          <th width="20%">Activity</th>
          <th width="35%" align="left">Notes</th>
          <th width="5%">Status</th>
        </tr>
        <tr>
          <td>Species A</td>
          <td align="center">10</td>
          <td>activity</td>
          <td>notes</td>
          <td>status</td>
        </tr>
        <tr>
          <td>Species B</td>
          <td align="center">2</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td>Species C</td>
          <td align="center"><img src="images/theme_blue/tick.gif"></td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
        </tr>
        </table><br>
        </div><p></p>
        </div>
        </div>
        </div>
        """, 'utf-8', metadata={'identifiers': (1, 2, 3), 'country': 'pt'})
        self.parser = ChecklistParser(self.response)

    def test_checklist_version(self):
        """Verify the version number for the checklist format is defined."""
        self.assertEqual(CHECKLISTS_DOWNLOAD_FORMAT,
                         self.parser.get_checklist()['meta']['version'])

    def test_checklist_language(self):
        """Verify the language used for the checklist format is defined."""
        self.assertEqual(CHECKLISTS_DOWNLOAD_LANGUAGE,
                         self.parser.get_checklist()['meta']['language'])

    def test_checklist_identifier(self):
        """Verify the checklist identifier is extracted."""
        self.assertEqual('PT1', self.parser.get_checklist()['identifier'])

    def test_source_name(self):
        """Verify the name of the source is extracted."""
        actual = self.parser.get_checklist()['source']['name']
        self.assertEqual('WorldBirds', actual)

    def test_source_url(self):
        """Verify the checklist url is extracted."""
        actual = self.parser.get_checklist()['source']['url']
        self.assertEqual('http://example.com', actual)

    def test_checklist_date(self):
        """Verify the checklist date is extracted."""
        self.assertEqual('2013-05-23', self.parser.get_checklist()['date'])

    def test_checklist_time(self):
        """Verify the checklist time is extracted."""
        actual = self.parser.get_checklist()['protocol']['time']
        self.assertEqual('11:00', actual)

    def test_observer_names(self):
        """Verify the list of observers is extracted."""
        self.assertEqual(['Observer A', 'Observer B'],
                         self.parser.get_checklist()['observers']['names'])

    def test_observers_count(self):
        """Verify the number of observers is extracted."""
        self.assertEqual(2, self.parser.get_checklist()['observers']['count'])

    def test_activity(self):
        """Verify the activity is extracted."""
        self.assertEqual('Birdwatching, with no specific purpose',
                         self.parser.get_checklist()['activity'])

    def test_location_name(self):
        """Verify the location name is extracted."""
        self.assertEqual('Location A', self.parser.get_location()['name'])

    def test_protocol_type(self):
        """Verify the protocol name is extracted."""
        self.assertEqual('Timed visit', self.parser.get_protocol()['name'])

    def test_protocol_duration_hours(self):
        """Verify the duration hours of the visit is extracted."""
        self.assertEqual(1, self.parser.get_protocol()['duration_hours'])

    def test_protocol_duration_minutes(self):
        """Verify the duration minutes of the visit is extracted."""
        self.assertEqual(5, self.parser.get_protocol()['duration_minutes'])

    def test_entry_count(self):
        """Verify the number of entries."""
        self.assertEqual(3, len(self.parser.get_entries()))

    def test_entries(self):
        """Verify the entries."""
        expected = [{
            'identifier': 'PT1000',
            'species': {'name': 'Species A'},
            'count': 10,
            'comment': 'notes',
        }, {
            'identifier': 'PT1001',
            'species': {'name': 'Species B'},
            'count': 2,
            'comment': '',
        }, {
            'identifier': 'PT1002',
            'species': {'name': 'Species C'},
            'count': 0,
            'comment': '',
        }]
        self.assertEqual(expected, self.parser.get_entries())
