"""Tests for initializing and starting the WorldBirdsSpider."""

from unittest import TestCase

from checklists_scrapers.spiders import worldbirds_spider


class WorldBirdsSpiderTestCase(TestCase):
    """Verify the spider initialization."""

    def test_missing_username(self):
        """Verify an error is raised if the username is not set."""
        with self.assertRaises(ValueError):
            worldbirds_spider.WorldBirdsSpider('', '', '')

    def test_missing_password(self):
        """Verify an error is raised if the password is not set."""
        with self.assertRaises(ValueError):
            worldbirds_spider.WorldBirdsSpider('username', '', '')

    def test_missing_country(self):
        """Verify an error is raised if the country is not set."""
        with self.assertRaises(ValueError):
            worldbirds_spider.WorldBirdsSpider('username', 'password', '')

    def test_invalid_country(self):
        """Verify an error is raised if the country is not supported."""
        with self.assertRaises(ValueError):
            worldbirds_spider.WorldBirdsSpider('username', 'password', '++')
