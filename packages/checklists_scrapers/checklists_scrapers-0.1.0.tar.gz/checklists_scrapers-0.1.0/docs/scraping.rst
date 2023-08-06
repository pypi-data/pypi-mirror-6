========
Scraping
========

Downloading the checklists from a database is performed using the scrapy
crawl command::

    scrapy crawl ebird -a region=PT-11

The -a option is used to pass arguments to the scraper, in this case checklists
will be downloaded for eBird region PT-11 (Lisbon, Portugal).

All of the environment variables, used to configure the scrapers, may be
overridden on the command line when the scrapers are run using the -s option::

    scrapy crawl ebird -s DOWNLOAD_DIR=/path/to/dir

Note that the "CHECKLISTING" prefix from the environment variable name is
dropped.

See the docs for each scraper to get a list of the command line arguments.

If you have defined the settings for a mail server and the setting
CHECKLISTS_REPORT_RECIPIENTS then a status report will be sent out each time
the scrapers are run. The report contains a list of the checklist downloaded
along with an errors (complete with stack traces) and any warnings::

    Spider: ebird
    Date: 03 Jan 2014
    Time: 11:00

    ----------------birdinglisboa---------
      Checklists downloaded
    -------------------------
    2013-12-27 09:59, Jardim Botanico da Universidade de Lisboa
    2013-12-28 10:20, Baia Cascais
    2013-12-28 13:31, PN Sintra-Cascais--Cabo da Roca
    2013-12-29 07:45, RN Estuario do Tejo--Vala da Saragossa

    ----------
      Errors
    ----------
    URL: http://ebird.org/ebird/view/checklist?subID=S161101101
    Traceback (most recent call last):
      File "/home/birdinglisboa/venv/local/lib/python2.7/site-packages/twisted/internet/base.py", line 1201, in mainLoop
        self.runUntilCurrent()
      File "/home/birdinglisboa/venv/local/lib/python2.7/site-packages/twisted/internet/base.py", line 824, in runUntilCurrent
        call.func(*call.args, **call.kw)
      File "/home/birdinglisboa/venv/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 382, in callback
        self._startRunCallbacks(result)
      File "/home/birdinglisboa/venv/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 490, in _startRunCallbacks
        self._runCallbacks()
    --- <exception caught here> ---
      File "/home/birdinglisboa/venv/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 577, in _runCallbacks
        current.result = callback(current.result, *args, **kw)
      File "/home/birdinglisboa/venv/local/lib/python2.7/site-packages/checklists_scrapers/spiders/ebird_spider.py", line 585, in parse_checklist
        checklist = self.merge_checklists(original, update)
      File "/home/birdinglisboa/venv/local/lib/python2.7/site-packages/checklists_scrapers/spiders/ebird_spider.py", line 602, in merge_checklists
        original['entries'], update['entries'])
      File "/home/birdinglisboa/venv/local/lib/python2.7/site-packages/checklists_scrapers/spiders/ebird_spider.py", line 695, in merge_entries
        if count in key[index]:
    exceptions.TypeError: string indices must be integers

    ------------
      Warnings
    ------------
    2014-01-01 11:55, Parque da Paz
    API: http://ebird.org/ws1.1/data/obs/loc/recent?r=L1127099&detail=full&back=7&includeProvisional=true&fmt=json
    URL: http://ebird.org/ebird/view/checklist?subID=S16160707
    Could not update record from API. There are 2 records that match: species=White Wagtail; count=4.

Checklists downloaded also included the name of the observer, which was removed
here for obvious reasons. The stack traces in the Errors section is useful if
there is a bug but it is also a first indication that the format of the
information being scraped has changed. In either case the problem should be
reported as an issue.

Warnings are generally informative. Here a warning is generated because the
checklist contained two equal counts for White Wagtail in the API records -
only the species is reported information on subspecies is dropped. However
the subspecies is reported on the checklist web page. That means when the web
page was scraped it was not possible to distinguish between the two records.
The records should be edited to add any useful information such as comments,
which are only available from the web page.

Additional warnings also are generated when LOG_LEVEL is set to DEBUG::

    ------------
      Warnings
    ------------
    2014-01-01 09:40, Estuario do Tejo--Leziria Grande de Vila Franca de Xira
    API: http://ebird.org/ws1.1/data/obs/loc/recent?r=L927102&detail=full&back=7&includeProvisional=true&fmt=json
    URL: http://ebird.org/ebird/view/checklist?subID=S161633968
    Web page contains record missing from API: species=Graylag Goose; count=375.
    Web page contains record missing from API: species=Mallard; count=700.

Here the warning reports records that were on the checklist web page but were
not included in the call to the eBird API. This might be a problem with the
eBird API however it does not affect the contents of the downloaded checklists
so no action is required, hence the reason it is only displayed when debugging.

These two types of warning are the only ones supported right now. Additional
warnings will be added in the future.