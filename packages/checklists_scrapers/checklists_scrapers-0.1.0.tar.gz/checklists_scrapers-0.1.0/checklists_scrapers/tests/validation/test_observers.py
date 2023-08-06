"""Validate the checklist attributes in the downloaded checklists.

Validation Tests:

   Observers:
       1. the observers is a dict.

   ObserversCount:
       1. the count is an integer.
       2. the count is positive.
       3. the count is equal or greater than the number of names.

   ObserverNames:
       1. observer names is a list.
       2. each observer name is a string.
       3. each observer name does not have leading/trailing whitespace.
"""
from checklists_scrapers.tests.validation import checklists, ValidationTestCase


class Observers(ValidationTestCase):
    """Validate the checklist."""

    def test_checklist_type(self):
        """Verify the checklist is a dict."""
        for checklist in checklists:
            self.assertIsInstance(checklist['observers'], dict,
                                  msg=checklist['source'])


class ObserversCount(ValidationTestCase):
    """Validate the count of observers in the checklist."""

    def test_observers_count_type(self):
        """Verify the observers is an integer."""
        for checklist in checklists:
            self.assertIsInstance(checklist['observers']['count'], int,
                                  msg=checklist['source'])

    def test_observers_count_positive(self):
        """Verify the observers is a positive integer."""
        for checklist in checklists:
            self.assertTrue(checklist['observers']['count'] > 0,
                            msg=checklist['source'])

    def test_count_observers(self):
        """Verify the count is greater or equal to the number of names."""
        for checklist in checklists:
            self.assertTrue(checklist['observers']['count'] >=
                            len(checklist['observers']['names']),
                            msg=checklist['source'])


class ObserverNames(ValidationTestCase):
    """Validate the observer names in the downloaded checklists."""

    def test_observers_names_type(self):
        """Verify the observers is a list."""
        for checklist in checklists:
            self.assertIsInstance(checklist['observers']['names'], list,
                                  msg=checklist['source'])

    def test_observer_name_type(self):
        """Verify the names of the checklist observers."""
        for checklist in checklists:
            for observer in checklist['observers']['names']:
                self.assertIsInstance(observer, unicode,
                                      msg=checklist['source'])

    def test_observer_names_stripped(self):
        """Verify the observer names don't have extra whitespace."""
        for checklist in checklists:
            for observer in checklist['observers']['names']:
                self.assertStripped(observer, msg=checklist['source'])
