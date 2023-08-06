
===================
Checklists_scrapers
===================
Checklists__scrapers is a set of web scrapers for downloading records from
on-line databases of observations of birds. Scrapers are available for:

:ebird:
    a database hosted by the Laboratory for Ornithology at Cornell University,
    covering the Americas, Oceania and an increasing number of records for
    European countries.

:worldbirds:
    a network of databases hosted by WorldBirds (BirdLife International),
    with good coverage of countries around the Mediterranean and Africa.

The eBird API only provider checklist records for up to the past 30 days so
the scrapers must be run on a regular basis. They are intended to provide a
continuous update of records and so are ideal for mirroring subsets of the
records available (for a given region for example) so you don't have to
repeatedly run reports or submit requests for data from the database hosts.

So, what is this for?
---------------------
Checklists_scrapers was written to aggregate records from different databases
for loading into a
`django-checklists <http://github.com/StuartMacKay/django-checklists>`_
database. However, since the downloaded checklists are in JSON format the file
may be used with any similar database.

The scrapers (and django-checklists) are current used by the
`Birding Lisboa <http://www.birdinglisoa.com/>`_ news service which covers the
area around the Tejo estuary, Portugal. All the downloaded checklists are
loaded into a database which is used to publish the latest news as well as
generate annual reports.

A similar database could be used for any purpose - analysing observations
for conservation, environmental management or education. Aggregating the
observations from multiple databases with the scrapers makes this task a
lot easier.

Installing & Configuring
------------------------
Checklists_scrapers is available from PyPI. You can install it with pip or
easy_install::

    pip install checklists_scrapers

The scrapers are built using the scrapy engine which uses settings, in the same
way as Django, for configuration and runtime values. The settings file is
configured to initialize its values from environment variables. That makes it
easy to configure the scrapers, particularly for the most common use-case,
running them from a scheduler such as cron.

The only required setting is to tell scrapy (the engine used by the scrapers)
the path to the settings module::

    export SCRAPY_SETTINGS_MODULE=checklists_scrapers.settings

The remaining settings have sensible defaults so only those that are
installation dependent, such as the mail server used for sending out status
reports. Here is this script that is used to run the scrapers for Birding
Lisboa from cron::

    #!/bin/bash

    export SCRAPY_SETTINGS_MODULE=checklists_scrapers.settings

    export CHECKLISTS_LOG_LEVEL=INFO

    export CHECKLISTS_DOWNLOAD_DIR=/tmp/checklists_scrapers

    export CHECKLISTS_MAIL_HOST=mail.example.com
    export CHECKLISTS_MAIL_PORT=25
    export CHECKLISTS_MAIL_USER=<user>
    export CHECKLISTS_MAIL_PASS=<password>
    export CHECKLISTS_MAIL_FROM=scrapers@example.com

    export CHECKLISTS_REPORT_RECIPIENTS=admins@example.com

    source /home/project/venv/bin/activate
    cd /home/project

    scrapy crawl ebird -a region=PT-11
    scrapy crawl ebird -a region=PT-15

The settings can also be defined when the scrapers are run using the -S
option::

    scrapy crawl ebird -a region=PT-15 -s LOG_LEVEL=DEBUG

However this obvious becomes a little cumbersome if more than one or two
settings are involved.

NOTE: the environment variables use a prefix "CHECKLISTS" as a namespace
to avoid interfering with any other variables. When the setting is defined
using the -s option when running the scrapers, this prefix must be dropped.

NOTE: CHECKLISTS_REPORT_RECIPIENTS is a comma-separated list of one or more
email addresses. The default value is an empty string so no status reports
will be mailed out. However if the LOG_LEVEL is set to 'DEBUG' the status
report will be written to the file checklists_scrapers_status.txt in the
CHECKLISTS_DOWNLOAD_DIR directory.

NOTE: You can configure the mail server settings using the same environment
variables used by the django-checklists project. This minimises the number
of variables that need to be defined when using both apps in the same project.
See the settings file for the names of the variables to use.

Everything is now ready to run.

Scraping
--------
The arguments passed to the scrapers on the command line specify value such as
which region to download observations from and login details for scrapers
that need an account to access the data::

    scrapy crawl ebird -a region=PT-11

    scrapy crawl worldbirds -a username=<user> -a password=<pass> -a country=uk

See the docs for each spider to get a list of the command line arguments and
settings.

If you have defined the settings for a mail server and the setting
CHECKLISTS_REPORT_RECIPIENTS then a status report will be sent out each time
the scrapers are run. If the LOG_LEVEL is set to 'DEBUG' the report is also
written to the directory where the checklists are downloaded to. The report
contains a list of the checklist downloaded along with an errors (complete with
stack traces) and any warnings::

    Scraper: ebird
    Date: 03 Jan 2014
    Time: 11:00

    -------------------------
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
information being scraped has changed. In either case report it as an issue and
it will get fixed.

Warnings are generally informative. Here a warning is generated because the
checklist contained two equal counts for White Wagtail in the API records -
only the species is reported information on subspecies is dropped. However
the subspecies is reported on the checklist web page. That means when the web
page was scraped it was not possible to distinguish between the two records.
The records should be edited to add any useful information such as comments,
which are only available from the web page.
