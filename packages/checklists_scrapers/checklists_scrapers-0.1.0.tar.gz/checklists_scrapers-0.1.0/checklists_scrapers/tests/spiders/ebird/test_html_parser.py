"""Tests for parsing a checklist's web page."""

from unittest import TestCase

from checklists_scrapers.spiders.ebird_spider import HTMLParser
from checklists_scrapers.tests.utils import response_for_content


class ParseHTMLChecklistTestCase(TestCase):
    """Verify the spider can extract data from the checklist web page."""

    def setUp(self):
        """Initialize the test."""
        self.url = "http://ebird.org/ebird/view/checklist?subID=S0000001"
        self.content = """
        <div class="report-section">
            <div class="rs-body-spp">
                <div class="mod">
                    <div class="inner">
                        <div class="bd">
                            <div class="rs-action">
                            </div>
                            <h5 class="rep-obs-date">
                            <!-- date -->

                                Sun Mar 24, 2013

                            3:10 PM

                            </h5>
                            <dl class="def-list">
                                <dt>Protocol:</dt>
                                <dd>Traveling</dd>
                            </dl>
                            <dl class="def-list">
                                <dt>Party Size:</dt>
                                <dd>1</dd>
                            </dl>
                            <dl class="def-list">
                                <dt>Duration:</dt>
                                <dd>2 hour(s) 35 minute(s)</dd>
                            </dl>
                            <dl class="def-list">
                                <dt>Distance:</dt>
                                <dd>2.0 kilometer(s)</dd>
                            </dl>
                            <dl class="def-list">
                                <dt>Observers:</dt>
                                <dd>

                                    Stuart MacKay

                                </dd>
                            </dl>
                            <dl class="def-list">
                                <dt>Comments:</dt>
                                <dd>

                                    A comment.

                                </dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        self.response = response_for_content(self.content, 'utf-8',
                                             url=self.url)
        self.parser = HTMLParser(self.response)

    def test_get_attributes(self):
        """Verify all the attributes for a checklist can be extracted."""
        expected = {
            u'Protocol:': u'Traveling',
            u'Party Size:': u'1',
            u'Duration:': u'2 hour(s) 35 minute(s)',
            u'Distance:': u'2.0 kilometer(s)',
            u'Observers:': u'Stuart MacKay',
            u'Comments:': u'A comment.',
        }
        actual = self.parser.get_attributes(self.parser.docroot)
        self.assertEqual(expected, actual)

    def test_get_source(self):
        """Verify the observers names can be extracted from the page."""
        expected = {
            'count': 1,
            'names': ['Stuart MacKay'],
        }
        actual = self.parser.get_observers()
        self.assertEqual(expected, actual)

    def test_get_protocol(self):
        """Verify the protocol can be extracted from the page."""
        expected = {
            'name': 'Traveling',
            'duration_hours': 2,
            'duration_minutes': 35,
            'distance': 2000,
            'area': 0,
        }
        actual = self.parser.get_protocol()
        self.assertEqual(expected, actual)

    def test_get_default_activity(self):
        """Verify the activity is extracted from the page."""
        self.assertEqual(self.parser.default_activity,
                         self.parser.get_activity())

    def test_get_activity_from_protocl(self):
        """Verify the activity is extracted from the protocol name."""
        protocol = self.parser.activities.keys()[0]
        activity = self.parser.activities[protocol][0]
        self.content = self.content.replace('Traveling', protocol)
        self.response = response_for_content(self.content, 'utf-8',
                                             url=self.url)
        self.parser = HTMLParser(self.response)
        self.assertEqual(activity, self.parser.get_activity())


class ParseHTMLEntryTestCase(TestCase):
    """Verify the spider can extract information from checklist entries."""

    def setUp(self):
        """Initialize the test."""
        self.url = "http://ebird.org/ebird/view/checklist?subID=S0000001"
        self.content = """
        <tr class="spp-entry">
            <th><h5 class="se-count">23</h5></th>
            <td>
                <div class="se-hd">
                    <div class="inner bd">
                        <h5 class="se-name">Mallard</h5>
                        <div class="rs-action">
                        </div>
                    </div>
                </div><!-- .se-hd -->
                <div class="se-detail">
                    <div class="sd-head">
                        <h6>Age & Sex</h6>
                    </div>
                    <div class="sd-data-age-sex">
                        <table>
                            <tbody>
                                <tr>
                                    <th></th>
                                    <th>Juvenile</th>
                                    <th>Immature</th>
                                    <th>Adult</th>
                                    <th>Age Unknown</th>
                                </tr>
                                <tr>
                                    <td>Male</td>
                                    <td class="num"></td>
                                    <td class="num"></td>
                                    <td class="num">9</td>
                                    <td class="num"></td>
                                </tr>
                                <tr>
                                    <td>Female</td>
                                    <td class="num"></td>
                                    <td class="num"></td>
                                    <td class="num">6</td>
                                    <td class="num"></td>
                                </tr>
                                <tr>
                                    <td>Sex Unknown</td>
                                    <td class="num">8</td>
                                    <td class="num"></td>
                                    <td class="num"></td>
                                    <td class="num"></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="se-detail">
                    <div class="sd-head">
                        <h6>Breeding Code</h6>
                    </div>
                    <div class="sd-data">
                        FL Confirmed--Recently Fledged Young
                    </div>
                </div>
            </td>
        </tr>
        """
        self.content = response_for_content(self.content, 'utf-8',
                                            url=self.url)
        self.parser = HTMLParser(self.content)

    def test_extract_species(self):
        """Verify the common name is extracted."""
        expected = {
            'name': 'Mallard',
        }
        actual = self.parser.get_entries()[0]['species']
        self.assertEqual(expected, actual)

    def test_extract_detail(self):
        """Verify the age and sex can be extracted for an entry."""
        expected = [
            {'age': 'Adult', 'sex': 'Male', 'count': 9},
            {'age': 'Adult', 'sex': 'Female', 'count': 6},
            {'age': 'Juvenile', 'sex': 'Sex Unknown', 'count': 8},
        ]
        entry = self.parser.docroot.select('//tr[@class="spp-entry"]')
        actual = self.parser.get_entry_details(entry)
        self.assertEqual(expected, actual)
