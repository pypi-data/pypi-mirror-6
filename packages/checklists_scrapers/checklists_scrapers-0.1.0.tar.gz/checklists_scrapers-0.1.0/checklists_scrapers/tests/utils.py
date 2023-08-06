"""Utility functions for tests."""

import json

from multiprocessing import Process
from scrapy.crawler import CrawlerProcess

from scrapy.http import TextResponse, Request


def response_for_content(content, encoding, url='http://example.com',
                         metadata=None):
    """Create a Scrapy Response containing the content.

    This function is used for unit-testing to verify that spiders can
    parse the contents provided.

    Args:
        content (str): the contents of the response.
        encoding (str): the character encoding of the content, e.g. 'utf-8'.

    Kwargs:
        url (str): the URL from the request that created the response.
        metadata (dict): parameters to pass to the response.

    Returns:
        TextResponse. A scrapy response object.

    """
    request = Request(url=url, meta=metadata)
    return TextResponse(url=url, request=request, body=content,
                        encoding=encoding)


def response_for_data(data, url='http://example.com', metadata=None):
    """Create a Scrapy Response for the json encode-able data.

    This function is used for unit-testing to verify that spiders can
    parse the JSON encode-able data provided.

    Args:
        data (list): the contents of the response.

    Kwargs:
        url (str): the URL from the request that created the response.
        metadata (dict): parameters to pass to the response.

    Returns:
        TextResponse. A scrapy response object.

    """
    content = json.dumps(data)
    encoding = 'utf-8'
    return response_for_content(content, encoding, url=url, metadata=metadata)


class RunCrawler():
    """RunCrawler runs a crawler in a separate process.

    Useful sources:
    https://groups.google.com/forum/?fromgroups#!topic/scrapy-users/8zL8W3SdQBo
    http://stackoverflow.com/questions/13437402/how-to-run-scrapy-from-within-a-python-script
    """
    def __init__(self, settings):
        self.crawler = CrawlerProcess(settings)
        self.crawler.configure()

    def _crawl(self, spider):
        self.crawler.crawl(spider)
        self.crawler.start()
        self.crawler.stop()

    def crawl(self, spider):
        p = Process(target=self._crawl, args=(spider,))
        p.start()
        p.join()
