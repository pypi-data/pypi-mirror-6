"""
validate_ebird_scraper.py

This script is used to validate the scraper used to download checklists from
the eBird API and checklist web pages. Once the scraper has finished the suite
of tests in the module checklists_scrapers.tests.sites is executed to verify
that all the information is extracted correctly.

To run the tests on the checklists downloaded by the WorldBirds scraper run
the script as follows:

    python validate_ebird_scraper.py <region>

where,

    <region> is eBird region code for a given area, e.g. PT-11

"""

import json
import nose
import shutil
import sys
import tempfile

from scrapy.settings import CrawlerSettings

from checklists_scrapers import settings
from checklists_scrapers.spiders.ebird_spider import EBirdSpider
from checklists_scrapers.tests.utils import RunCrawler
from checklists_scrapers.utils import list_files

from checklists_scrapers.tests.validation import checklists


settings.DOWNLOAD_DIR = tempfile.mkdtemp()
settings.REPORT_RECIPIENTS = ''

region = sys.argv[1]

spider = EBirdSpider(region=region)
RunCrawler(CrawlerSettings(settings)).crawl(spider)

for path in list_files(settings.DOWNLOAD_DIR, 'json'):
    with open(path, 'rb') as fp:
        checklists.append(json.load(fp))

nose.run(argv=['checklists_scrapers.tests.validation'])

shutil.rmtree(settings.DOWNLOAD_DIR)
