"""Validate the source attributes in the downloaded checklists.

Validation Tests:

   Source:
       1. the checklist is a dict.

   SourceSubmittedBy:
       1. submitted_by is a string.
       2. submitted_by is set.
       3. submitted_by does not have leading/trailing whitespace.

   SourceName:
       1. source is a string.
       2. source is set.
       3. source does not have leading/trailing whitespace.
"""
from checklists_scrapers.tests.validation import checklists, ValidationTestCase


class Source(ValidationTestCase):
    """Validate the checklist."""

    def test_checklist_type(self):
        """Verify the checklist is a dict."""
        for checklist in checklists:
            self.assertIsInstance(checklist['source'], dict,
                                  msg=checklist['source'])


class SourceSubmittedBy(ValidationTestCase):
    """Validate the source submitter in the downloaded checklists."""

    def test_submitted_by_type(self):
        """Verify the checklist submitter is a unicode string."""
        for checklist in checklists:
            self.assertIsInstance(checklist['source']['submitted_by'], unicode,
                                  msg=checklist['source'])

    def test_submitted_by_set(self):
        """Verify the checklist submitter is set."""
        for checklist in checklists:
            self.assertTrue(checklist['source']['submitted_by'],
                            msg=checklist['source'])

    def test_submitted_by_stripped(self):
        """Verify the checklist submitter has no extra whitespace."""
        for checklist in checklists:
            self.assertStripped(checklist['source']['submitted_by'],
                                msg=checklist['source'])

    def test_submitted_by_is_an_observer(self):
        """Verify the checklist submitter is also listed as an observer."""
        for checklist in checklists:
            self.assertTrue(checklist['source']['submitted_by'] in
                            checklist['observers']['names'],
                            msg=checklist['source'])


class SourceName(ValidationTestCase):
    """Validate the checklist source name in the downloaded checklists."""

    def test_source_type(self):
        """Verify the checklist source is a unicode string."""
        for checklist in checklists:
            self.assertIsInstance(checklist['source']['name'], unicode,
                                  msg=checklist['source'])

    def test_source_set(self):
        """Verify the checklist submitter is set."""
        for checklist in checklists:
            self.assertTrue(checklist['source']['name'],
                            msg=checklist['source'])

    def test_source_stripped(self):
        """Verify the source has no extra whitespace."""
        for checklist in checklists:
            self.assertStripped(checklist['source']['name'],
                                msg=checklist['source'])
