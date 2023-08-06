"""Tests for parsing the WorldBirds panel containing the observer details."""

from unittest import TestCase

from checklists_scrapers.spiders.worldbirds_spider import ObserverParser
from checklists_scrapers.tests.utils import response_for_content


class ObserverParserTestCase(TestCase):
    """Verify the spider can extract data from the observer details."""

    def setUp(self):
        """Initialize the test."""
        self.response = response_for_content(u"""
        <table class="PopupTable" cellspacing="0">
        <tr>
          <td><label>User name</label></td>
          <td>username</td>
        </tr>
        <tr>
          <td><label>Full name</label></td>
          <td>Full Name</td>
        </tr>
        <tr>
          <td><label>Email</label></td>
          <td>
            <a href="mailto:username@example.com">username@example.com</a>
          </td>
        </tr>
        </table>
        """, 'utf-8', metadata={'checklist': {}})
        self.parser = ObserverParser(self.response)
        self.checklist = self.parser.get_checklist()

    def test_submitted_by(self):
        """Verify the observer's name is extracted."""
        self.assertEqual('Full Name', self.checklist['source']['submitted_by'])
