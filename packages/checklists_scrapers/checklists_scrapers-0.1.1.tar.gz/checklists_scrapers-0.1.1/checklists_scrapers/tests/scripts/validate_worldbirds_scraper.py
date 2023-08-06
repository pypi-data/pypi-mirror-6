"""
validate_worldbirds_scraper.py

This script used to validate the scraper used to download checklists from a
WorldBirds server. Once the scraper has completed the suite of tests in the
module checklists_scrapers.tests.sites is executed to verify that all the
information is extracted correctly from the site.

To run the tests on the checklists downloaded by the WorldBirds scraper run
the script as follows:

    python validate_worldbirds_scraper.py <username> <password> <country>

where,

    <username> is the username for the account on the server.
    <password> is the password for the account on the server.
    <country> is the country code that identifies the server to access.

"""
import json
import nose
import shutil
import sys
import tempfile

from scrapy.settings import CrawlerSettings

from checklists_scrapers import settings
from checklists_scrapers.spiders.worldbirds_spider import WorldBirdsSpider
from checklists_scrapers.tests.utils import RunCrawler
from checklists_scrapers.utils import list_files

from checklists_scrapers.tests.validation import checklists


settings.DOWNLOAD_DIR = tempfile.mkdtemp()
settings.REPORT_RECIPIENTS = ''

username = sys.argv[1]
password = sys.argv[2]
country = sys.argv[3]

spider = WorldBirdsSpider(username=username, password=password, country=country)
RunCrawler(CrawlerSettings(settings)).crawl(spider)

for path in list_files(settings.DOWNLOAD_DIR, 'json'):
    with open(path, 'rb') as fp:
        checklists.append(json.load(fp))

nose.run(argv=['checklists_scrapers.tests.validation'])

shutil.rmtree(settings.DOWNLOAD_DIR)
