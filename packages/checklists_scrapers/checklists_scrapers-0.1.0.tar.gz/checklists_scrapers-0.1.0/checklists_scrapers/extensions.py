"""Extensions for customizing scrapy."""

import datetime
import os

from unidecode import unidecode

from scrapy import log
from scrapy import signals
from scrapy.mail import MailSender


class SpiderStatusReport(object):
    """Email a status report when a spider finishes.

    The report contains a list of the checklists downloaded.

    Reports are sent to the list of email addresses in the setting
    REPORT_RECIPIENTS. Set this to an empty list (the default) in order to
    disable sending the reports.

    The report is is sent as a regular (ASCII) email message and not in MIME
    format. Accented characters are removed by converting them into their
    un-accented equivalents using unidecode.

    If the LOG_LEVEL is set to 'DEBUG' then the status report is also written
    to the directory where the checklists are downloaded to.
    """

    template = """Scraper: %(spider)s
Date: %(date)s
Time: %(time)s

-------------------------
  Checklists downloaded
-------------------------
%(checklists)s

----------
  Errors
----------
%(errors)s

------------
  Warnings
------------
%(warnings)s

"""

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls()
        crawler.signals.connect(extension.spider_closed,
                                signal=signals.spider_closed)
        return extension

    def spider_closed(self, spider):
        spider.log("Generating status report", log.INFO)

        now = datetime.datetime.today()

        context = {
            'spider': spider.name,
            'date': now.strftime("%d %b %Y"),
            'time': now.strftime("%H:%M"),
            'checklists': 'No checklists downloaded',
            'errors': 'No errors reported',
            'warnings': 'No warnings reported',
        }

        checklists = getattr(spider, 'checklists', [])
        spider.log("%d checklists downloaded" % len(checklists), log.INFO)

        if checklists:
            summary = []
            for checklist in checklists:
                if 'protocol' in checklist and 'time' in checklist['protocol']:
                    time = checklist['protocol']['time']
                else:
                    time = '--:--'
                summary.append("%s %s, %s (%s)" % (
                    checklist['date'],
                    time,
                    unidecode(checklist['location']['name']),
                    unidecode(checklist['source']['submitted_by'])
                ))
            context['checklists'] = '\n'.join(summary).encode('utf-8')

        errors = getattr(spider, 'errors', [])
        spider.log("%d errors reported" % len(errors), log.INFO)

        if errors:
            summary = []
            for url, failure in errors:
                summary.append("URL: %s\n%s\n\n" % (
                    url,
                    failure.getTraceback()
                ))
            context['errors'] = '\n'.join(summary).encode('utf-8')

        warnings = getattr(spider, 'warnings', [])
        spider.log("%d warnings reported" % len(warnings), log.INFO)

        if warnings:
            summary = []

            for checklist, messages in warnings:
                if 'protocol' in checklist and 'time' in checklist['protocol']:
                    time = checklist['protocol']['time']
                else:
                    time = '--:--'
                summary.append("%s %s, %s (%s)" % (
                    checklist['date'],
                    time,
                    unidecode(checklist['location']['name']),
                    unidecode(checklist['source']['submitted_by'])
                ))
                summary.append("API: %s" % checklist['source']['api'])
                summary.append("URL: %s" % checklist['source']['url'])
                summary.extend(messages)
                summary.append('')

            context['warnings'] = '\n'.join(summary).encode('utf-8')

        report = self.template % context

        if spider.settings['LOG_LEVEL'] == 'DEBUG':
            directory = spider.settings['DOWNLOAD_DIR']
            filename = os.path.join(directory, 'checklists_scrapers_status.txt')
            with open(filename, 'wb') as fp:
                fp.write(report)

        recipients = spider.settings['REPORT_RECIPIENTS'].strip()

        if recipients:
            mailer = MailSender.from_settings(spider.settings)
            addrs = [recipient.strip() for recipient in recipients.split(',')]
            mailer.send(
                to=addrs,
                subject="%s Status Report" % spider.name,
                body=report
            )
        else:
            spider.log("No recipients listed to receive status report",
                       log.INFO)




class ErrorLogger(object):

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls()
        crawler.signals.connect(extension.spider_error,
                                signal=signals.spider_error)
        return extension

    def spider_error(self, failure, response, spider):
        spider.errors.append((response.url, failure))
