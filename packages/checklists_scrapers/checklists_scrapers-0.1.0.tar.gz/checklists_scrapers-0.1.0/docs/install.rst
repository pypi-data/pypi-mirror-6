=======
Install
=======

Checklists_scrapers is available from PyPI so you can install it using pip::

    pip install checklists_scrapers

or easy_install::

    easy_install checklists_scrapers

Once installed the first step is to configure the runtime environment for
the scrapy engine and the scrapers. Rather than creating configuration files
or editing the package settings this is done using environment variables
which makes it easier to deploy the package and to customize the environment
each time the scrapers are run.

First tell the scrapy engine where to find the package settings, e.g. using
the bash shell::

    export SCRAPY_SETTINGS_MODULE=checklists_scrapers.settings

The settings file then in turn loads the values used to configure the scrapers
from the set of environment variables described here. (The settings for the
scrapy engine can also be defined in a config file which should be placed
the in the directory from where the scrapers are run. An example is included
in the project).

Next define the variables common to all the scrapers:

    CHECKLISTS_DOWNLOAD_DIR: the directory where the scrapers will download
    the checklists to. Filenames use the name of the source and the checklist
    identifier so running the scraper multiple times will overwrite any
    existing files but will not destroy any data. If this variable is not
    set then the checklists will be downloaded to the current directory when
    the scrapers are run.

    CHECKLISTS_DURATION: Download checklists for the previous <n> days. If
    this is not set then checklists will be downloaded for the previous 7 days.

    CHECKLISTS_REPORT_RECIPIENTS: When each scraper is run a status report
    is generated listing the checklists that were downloaded along with any
    errors or warnings encountered. This variable contains a comma-separated
    list of email addresses that the report will be sent to. If this is not
    set then the default value is an empty list and no reports will be sent.

    If the logging level is set to 'DEBUG' the status report is also written
    to the file, checklists_scrapers_status.txt in the CHECKLISTS_DOWNLOAD_DIR
    directory.

If status reports are being sent out then the following variables must also
be defined:

    CHECKLISTS_MAIL_HOST: the name of the SMTP server used to send the
    status reports.

    CHECKLISTS_MAIL_PORT: the port number for the SMTP server. If not set
    then the default port number is 25.

    CHECKLISTS_MAIL_USER: the username of the account on the mail server.

    CHECKLISTS_MAIL_PASS: the password for the account on the mail server.

    CHECKLISTS_MAIL_FROM: the from address used to indicate who sent the
    status report. If not defined then an empty string is used however it is
    likely that the SMTP server will require this to be set to either the
    accounts main email address or at least to a domain known to the server
    in order to avoid having the email classified as SPAM.

NOTE: You can configure the mail server settings using the same environment
variables used by the django-checklists project. This minimises the number
of variables that need to be defined when using both apps in the same project.

+----------------------+--------------------------------+
| checklists_scrapers  | django-checklists              |
+======================+================================+
| CHECKLISTS_MAIL_HOST | CHECKLISTS_EMAIL_HOST          |
+----------------------+--------------------------------+
| CHECKLISTS_MAIL_PORT | CHECKLISTS_EMAIL_PORT          |
+----------------------+--------------------------------+
| CHECKLISTS_MAIL_USER | CHECKLISTS_EMAIL_HOST_USER     |
+----------------------+--------------------------------+
| CHECKLISTS_MAIL_PASS | CHECKLISTS_EMAIL_HOST_PASSWORD |
+----------------------+--------------------------------+
| CHECKLISTS_MAIL_FROM | CHECKLISTS_SERVER_EMAIL        |
+----------------------+--------------------------------+


Logging is handled by:

    CHECKLISTS_LOG_LEVEL: The level at which messages are logged, either
    'CRITICAL', 'ERROR', 'WARNING', 'INFO' or 'DEBUG'. If the variable is not
    set then a default value of 'INFO' is used. The level can also be set on
    the command line when the scraper is run using the --loglevel or -L option.

    CHECKLISTS_LOG_FILE: The path to the file where the log messages are
    written. If the variable is not set a default path of
    'checklists_scrapers.log' is used and the file will be written to the
    directory from where the scrapers are run. This can also be set when the
    scraper is run using the --logfile command line option.

Next are the variables used to configure the individual scrapers. Currently
only the eBird scraper has a specific configuration parameter:

    EBIRD_INCLUDE_HTML: whether checklists downloaded from eBird should also
    scrape data from the checklist web page. The eBird API provides basic
    information for each observation however the checklist web page also has
    information on subspecies, the names of observers, any comments, etc.

Here is this script that is used to run the scrapers for Birding Lisboa from
cron::

    #!/bin/bash

    export SCRAPY_SETTINGS_MODULE=checklists_scrapers.settings

    export CHECKLISTS_LOG_LEVEL=INFO

    export CHECKLISTS_DOWNLOAD_DIR=/tmp/checklists_scrapers

    export CHECKLISTS_MAIL_FROM=scrapers@example.com
    export CHECKLISTS_MAIL_HOST=mail.example.com
    export CHECKLISTS_MAIL_USER=<user>
    export CHECKLISTS_MAIL_PASS=<password>

    export CHECKLISTS_REPORT_RECIPIENTS=admins@example.com

    source /home/project/venv/bin/activate
    cd /home/project

    scrapy crawl ebird -a region=PT-11
    scrapy crawl ebird -a region=PT-15

