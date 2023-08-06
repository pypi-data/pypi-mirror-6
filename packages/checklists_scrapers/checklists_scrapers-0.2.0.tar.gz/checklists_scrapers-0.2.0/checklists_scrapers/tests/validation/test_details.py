"""Validate each entry of the downloaded checklists.

Validation Tests:

   Details:
       1. the details for an entry is a dict.

   EbirdAge:
       1. the age matches the values used on eBird, either: Adult, Immature,
          Juvenile or Age Unknown.

   EbirdSex:
       1. the sex matches the values used on eBird, either: Male, Female or
          Sex Unknown.

"""
from checklists_scrapers.tests.validation import checklists, ValidationTestCase


class Details(ValidationTestCase):
    """Validate the entry details in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.details = []
        for checklist in checklists:
            for entry in checklist['entries']:
                if 'details' in entry:
                    self.details.extend(entry['details'])

    def test_detail_type(self):
        """Verify the entry field contains a dict."""
        for detail in self.details:
            self.assertIsInstance(detail, dict)


class EbirdAge(ValidationTestCase):
    """Validate the detail age in the checklists downloaded from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.details = []
        for checklist in [checklist for checklist in checklists
                          if checklist['source'] == 'ebird']:
            for entry in checklist['entries']:
                if 'details' in entry:
                    self.details.extend(entry['details'])

    def test_age(self):
        """Verify the age matches the expected value."""
        ages = ['Adult', 'Immature', 'Juvenile', 'Age Unknown']
        for detail in [detail for detail in self.details if 'age' in detail]:
            self.assertTrue(detail['age'] in ages)


class EbirdSex(ValidationTestCase):
    """Validate the detail sex in the checklists downloaded from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.details = []
        for checklist in [checklist for checklist in checklists
                          if checklist['source'] == 'ebird']:
            for entry in checklist['entries']:
                if 'details' in entry:
                    self.details.extend(entry['details'])

    def test_age(self):
        """Verify the sex matches the expected value."""
        sexes = ['Male', 'Female', 'Sex Unknown']
        for detail in [detail for detail in self.details if 'sex' in detail]:
            self.assertTrue(detail['sex'] in sexes)
