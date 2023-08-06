"""Scraper validation tests.

Verify that the format of the checklists downloaded by a given scraper matches
the checklist file format and so can consistently be loaded into a target
database with a minimum in variation.

The goal of these tests are both checking of the files that the scrapers
generate and notifying any breaking changes to the sites being crawled.

The tests are run by the scripts in checklists_scrapers/tests/scripts
which run the scrapers to download the checklists for a given database. The
(JSON format) checklists are then loaded and nose is called to run all of the
tests in this module.

"""
from unittest import TestCase


checklists = []


class ValidationTestCase(TestCase):
    """A class that provides extra assert methods for validating data."""

    def assertStripped(self, obj, msg=None):
        """Assert that a string does not have leading or trailing whitespace.

        Args:
            obj: The string to check.
            msg: Optional message to use on failure instead.
        """
        self.assertIsInstance(obj, basestring, 'Argument is not a string')

        if len(obj) != len(obj.strip()):
            standardMsg = '%s contains leading or trailing whitespace'
            self.fail(self._formatMessage(msg, standardMsg))
