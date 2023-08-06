"""Validate the checklist attributes in the downloaded checklists.

Validation Tests:

   Checklist:
       1. the checklist is a dict.

   ChecklistIdentifier:
       1. identifier is a string.
       2. identifier is set.
       3. identifier does not have leading/trailing whitespace.

   ChecklistDate:
       1. date is a string.
       2. date is in the format YYYY-MM-DD
"""
from checklists_scrapers.tests.validation import checklists, ValidationTestCase


class Checklist(ValidationTestCase):
    """Validate the checklist."""

    def test_checklist_type(self):
        """Verify the checklist is a dict."""
        for checklist in checklists:
            self.assertIsInstance(checklist, dict, msg=checklist['source'])


class ChecklistIdentifier(ValidationTestCase):
    """Validate the checklist identifier in the downloaded checklists."""

    def test_checklist_version(self):
        """Verify the checklist identifier is a unicode string."""
        for checklist in checklists:
            self.assertIsInstance(checklist['identifier'], unicode,
                                  msg=checklist['source'])

    def test_checklist_identifier(self):
        """Verify the checklist identifier is a unicode string."""
        for checklist in checklists:
            self.assertIsInstance(checklist['identifier'], unicode,
                                  msg=checklist['source'])

    def test_checklist_identifier_set(self):
        """Verify the checklist identifier is set."""
        for checklist in checklists:
            self.assertTrue(checklist['identifier'])

    def test_checklist_identifier_stripped(self):
        """Verify the checklist identifier has no extra whitespace."""
        for checklist in checklists:
            self.assertStripped(checklist['identifier'],
                                msg=checklist['source'])


class ChecklistDate(ValidationTestCase):
    """Validate the checklist date in the downloaded checklists."""

    def test_date_type(self):
        """Verify the checklist date is a unicode string."""
        for checklist in checklists:
            self.assertIsInstance(checklist['date'], unicode,
                                  msg=checklist['source'])

    def test_date_format(self):
        """Verify the checklist date is in the format YYYY-MM-DD."""
        date_format = r'(\d){4}-(\d){2}-(\d){2}'
        for checklist in checklists:
            self.assertRegexpMatches(checklist['date'], date_format,
                                     msg=checklist['source'])


class ChecklistComment(ValidationTestCase):
    """Validate the comment in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.comments = []
        for checklist in checklists:
            self.comments.append((checklist['comment'], checklist['source']))

    def test_comment_type(self):
        """Verify the entry count is a unicode string."""
        for comment, source in self.comments:
            self.assertIsInstance(comment, unicode, msg=source)

    def test_checklist_identifier_stripped(self):
        """Verify the entry comment has no extra whitespace."""
        for comment, source in self.comments:
            self.assertStripped(comment, msg=source)
