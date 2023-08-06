"""Scrapy settings."""

import os


def get_env_variable(var_name, default=None):
    """ Get the environment variable or raise an exception.

    Args:
        var_name (str): the name of the environment variable.

    Keyword Args:
        default (str): the default value to use of the environment variable
            is not set.

    Returns:
        str: the value for the specified environment variable.

    Raises:
        a NotConfigured exception if there is no environment variable
        with the specified name and a default value was not given.
    """
    value = os.environ.get(var_name, default)
    if value is None:
        from scrapy.exceptions import NotConfigured
        raise NotConfigured("Set the %s environment variable" % var_name)
    return value


BOT_NAME = 'checklists'

SPIDER_MODULES = ['checklists_scrapers.spiders']

NEWSPIDER_MODULE = 'checklists_scrapers.spiders'


#
# Scrapy extensions
#

EXTENSIONS = {
    'checklists_scrapers.extensions.SpiderStatusReport': 600,
    'checklists_scrapers.extensions.ErrorLogger': 600,
}


#
# Logging
#

LOG_STDOUT = True
LOG_LEVEL = get_env_variable('LOG_LEVEL', 'INFO')
LOG_FILE = get_env_variable('LOG_FILE', 'checklists_scrapers.log')


#
# Mail server
#
# Settings for the SMTP server that is used to send out status reports.

MAIL_FROM = get_env_variable('MAIL_FROM', '')
MAIL_HOST = get_env_variable('MAIL_HOST', '')
MAIL_PORT = int(get_env_variable('MAIL_PORT', '25'))
MAIL_USER = get_env_variable('MAIL_USER', '')
MAIL_PASS = get_env_variable('MAIL_PASS', '')

#
# Status reports
#
# Each of the spiders generates a status report that list the checklists
# downloaded along with any errors or warnings that occurred. The setting
# REPORT_RECIPIENTS contains a comma separate list of the email addresses
# that will receive a status report each time the spiders are run. Be sure
# to also define the settings for the mail server used to send the report.

REPORT_RECIPIENTS = get_env_variable('REPORT_RECIPIENTS', '')


#
# General settings for the spiders
#

# Define a shared directory for scraper downloads. The scrapers use the name
# of the source in file names so checklists from different sources will not
# overwrite each other.
DOWNLOAD_DIR = get_env_variable('DOWNLOAD_DIR', '.')

# Download checklists from the last <n> days. A value of 7 (one week) offers
# a reasonable trade-off between only fetching recent data while still
# catching checklists that are added late.
DURATION = int(get_env_variable('DURATION', '7'))

# eBird redirects requests for the checklist web page to do some security
# checks so the redirect middleware needs to be enabled.
REDIRECT_ENABLED = True

# Cookies are required for sites where the spider needs a user account.
COOKIES_ENABLED = True

# The maximum number of simultaneous requests that will be performed by the
# Scrapy downloader.
#
# IMPORTANT: Do not change this value, otherwise the Requests and Responses
# when parsing the eBird checklist web pages get mixed up. Since each eBird
# spider processes the checklists for one region and the number of checklists
# to be downloaded is low (typically a few dozen) then this restriction does
# not adversely affect performance.
CONCURRENT_REQUESTS = 1


#
# Settings for the eBird spider.
#

# Whether the checklist web page is also parsed to extract data (True) or
# only the data from the API is used (False).
EBIRD_INCLUDE_HTML = bool(get_env_variable('EBIRD_INCLUDE_HTML', '1'))
