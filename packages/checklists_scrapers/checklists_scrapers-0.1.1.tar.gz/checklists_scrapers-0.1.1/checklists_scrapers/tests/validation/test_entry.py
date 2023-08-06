"""Validate each entry of the downloaded checklists.

Validation Tests:

   Entry:
       1. the entry is a dict.

   EntryCount:
       1. count is an integer.
       2. count is positive.

   EntryComment (optional):
       1. comment is a unicode string.

"""
from checklists_scrapers.tests.validation import checklists, ValidationTestCase


class Entry(ValidationTestCase):
    """Validate the entry in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.entries = []
        for checklist in checklists:
            self.entries.extend(checklist['entries'])

    def test_entry_type(self):
        """Verify the entry field contains a dict."""
        for entry in self.entries:
            self.assertIsInstance(entry, dict)


class EntryCount(ValidationTestCase):
    """Validate the entry count in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.entries = []
        for checklist in checklists:
            for entry in checklist['entries']:
                self.entries.append((entry['count'], checklist['source']))

    def test_count_type(self):
        """Verify the entry count is an integer."""
        for count, source in self.entries:
            self.assertIsInstance(count, int, msg=source)

    def test_count_positive(self):
        """Verify the entry count is a positive integer."""
        for count, source in self.entries:
            self.assertTrue(count >= 0, msg=source)


class EntryComment(ValidationTestCase):
    """Validate the entry comment in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.comments = []
        for checklist in checklists:
            for entry in checklist['entries']:
                self.comments.append((entry['comment'], checklist['source']))

    def test_comment_type(self):
        """Verify the entry count is a unicode string."""
        for comment, source in self.comments:
            self.assertIsInstance(comment, unicode, msg=source)

    def test_checklist_identifier_stripped(self):
        """Verify the entry comment has no extra whitespace."""
        for comment, source in self.comments:
            self.assertStripped(comment, msg=source)
