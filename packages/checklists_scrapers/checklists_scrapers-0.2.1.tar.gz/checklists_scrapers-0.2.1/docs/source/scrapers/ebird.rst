=====
eBird
=====
eBird has an API which provides access to records submitted to the database for
up to the past 30 days. The records published through the API also include the
checklist identifier which is used to scrape additional data, such as the
protocol used, from the checklist web page.

The scraper is run using the crawl command-line tool::

    scrapy crawl ebird -a region=PT-11

The -a option is used by scrapy to pass key-value pairs to the scraper. The
eBird API and websites are public so only the region code, e.g. PT-11 needs to
be passed to the scraper. See the Resources section for links to a full list
of the available region codes.

Resources
---------

Find out more about eBird at http://ebird.org/content/ebird/

API documentation can be found at https://confluence.cornell.edu/display/CLOISAPI/eBird+API+1.1

An typical checklist web page can be found at http://ebird.org/ebird/view/checklist?subID=S13500933

eBird publishes a full list of region codes in PDF format and as an Excel spreadsheet:

* `State_Country_Codes_10_Nov_2011.pdf <http://help.ebird.org/customer/portal/kb_article_attachments/14685/original.pdf>`_
* `State_Country_Codes_10_Nov_2011.xls <http://help.ebird.org/customer/portal/kb_article_attachments/14684/original.xls>`_
