"""A scraper for downloading checklists from eBird.

This scraper creates checklists for recent observations for a given region
using the eBird API. Additional information for each checklist is also
scraped from the checklist web page.
"""

import json
import os
import re

from scrapy import log
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

from checklists_scrapers.spiders import CHECKLISTS_DOWNLOAD_FORMAT, \
    CHECKLISTS_DOWNLOAD_LANGUAGE
from checklists_scrapers.spiders.utils import remove_whitespace, select_keys, dedup, \
    save_json_data


class JSONParser(object):

    """Extract checklists from JSON data returned from the eBird API."""

    location_keys = [
        'locID',
        'locName',
        'subnational1Name',
        'subnational2Name',
        'countryName',
        'lat',
        'lng',
    ]

    checklist_keys = [
        'firstName',
        'lastName',
        'obsDt',
        'subID',
    ] + location_keys

    def __init__(self, response):
        """Initialize the parser with a JSON encoded response.

        Args:
            response (str): an encoded string containing the JSON data returned
                by a call to the eBird API.

        Returns:
            JSONParser: a JSONParser object with the records decided from
            the JSON data.
        """
        self.records = json.loads(response.body_as_unicode())

    def get_checklists(self):
        """Get the set of checklists from the observations."""
        filtered = dedup(select_keys(self.records, self.checklist_keys))
        checklists = [self.get_checklist(record) for record in filtered]
        for checklist in checklists:
            checklist['entries'] = [self.get_entry(r) for r in self.records
                                    if r['subID'] == checklist['identifier']]
        return checklists

    def get_checklist(self, record):
        """Get the fields for a checklist from an observation.

        Args:
            record (dict): the observation record.

        Returns:
            dict: a dictionary containing the checklist fields.
        """
        checklist = {
            'meta': {
                'version': CHECKLISTS_DOWNLOAD_FORMAT,
                'language': CHECKLISTS_DOWNLOAD_LANGUAGE,
            },
            'identifier': record['subID'].strip(),
            'date': record['obsDt'].strip().split(' ')[0],
            'location': self.get_location(record),
            'observers': self.get_observers(record),
            'source': self.get_source(record),
        }

        if ' ' in record['obsDt']:
            checklist['protocol'] = self.get_protocol(record)

        return checklist

    def get_protocol(self, record):
        """Get the information about the checklist protocol.

        Args:
            record (dict): the observation record.

        Returns:
            dict: a dictionary containing the protocol fields.

        A default protocol name of 'Incidental' is used since only the time
        of the observation is currently available.
        """
        return {
            'name': 'Incidental',
            'time': record['obsDt'].strip().split(' ')[1],
        }

    def get_observers(self, record):
        """Get the information about the checklist observers.

        Args:
            record (dict): the observation record.

        Returns:
            dict: a dictionary containing the list of observers names.
        """
        first_name = record['firstName'].strip()
        last_name = record['lastName'].strip()

        return {
            'count':  1,
            'names': [first_name + ' ' + last_name],
        }

    def get_source(self, record):
        """Get the information about the source of the checklist.

        Args:
            record (dict): the observation record.

        Returns:
            dict: a dictionary containing the source fields.
        """
        first_name = record['firstName'].strip()
        last_name = record['lastName'].strip()

        return {
            'name': 'eBird',
            'submitted_by': first_name + ' ' + last_name,
        }

    def get_locations(self):
        """Get the set of locations from the observations.

        Returns:
            list(dict): a list of dicts containing the fields for a location.
        """
        filtered = dedup(select_keys(self.records, self.location_keys))
        return [self.get_location(record) for record in filtered]

    def get_location(self, record):
        """Get the fields for a location from an observation.

        Returns:
            dict: a dictionary containing the fields for a location.

        If a given field is not present in the record then the value defaults
        to an empty string. This allows the method to process records that
        contain either the simple results fields or the full results fields.
        """
        return {
            'identifier': record['locID'],
            'name': record['locName'],
            'county': record.get('subnational2Name', ''),
            'region': record.get('subnational1Name', ''),
            'country': record.get('countryName', ''),
            'lat': record['lat'],
            'lon': record['lng'],
        }

    def get_entry(self, record):
        """Get the fields for an entry from an observation.

        Returns:
            dict: a dictionary containing the fields for a checklist entry.
        """
        return {
            'identifier': record['obsID'],
            'species': self.get_species(record),
            'count': record.get('howMany', 0),
        }

    def get_species(self, record):
        """Get the species fields for an entry from an observation.

        Args:
            record (dict); the observation record,

        Returns:
            dict: a dictionary containing the fields for a species.
        """
        return {
            'name': record['comName'],
            'scientific_name': record['sciName'],
        }


class HTMLParser(object):

    """Extract information from the checklist web page.

    Only the information not available through the API is extracted, with the
    exception of the counts for each species- which has the associated details
    dictionary which contains a breakdown of the count based on age and sex.
    """

    # eBird mixes up activities and protocols a bit so this table is used
    # to map protocol names onto an activity and alternative protocol.
    activities = {
        'Nocturnal Flight Call Count': (
            'Nocturnal Flight Call Count', 'Stationary'),
        'Heron Area Count': ('Heron Count', 'Area'),
        'Heron Stationary Count': ('Heron Count', 'Stationary'),
    }

    default_activity = 'Birding'

    def __init__(self, response):
        """Initialize the parser with an HTML encoded response.

        Args:
            response (str): the contents of the checklist web page.

        Returns:
            HTMLParser: an HTMLParser object containing the contents of the
                checklist web page and a dict containing the main checklist
                attributes.
        """
        self.docroot = HtmlXPathSelector(response)
        self.attributes = self.get_attributes(self.docroot)

    def get_attributes(self, node):
        """Get the checklist attributes.

        Args:
            node (HtmlXPathSelector): an XML node,

        Returns:
            dict: a dictionary containing the fields and values of a checklist.
        """
        keys = node.select('//dl/dt/text()').extract()
        keys = remove_whitespace(keys)
        values = node.select('//dl/dd/text()').extract()
        values = remove_whitespace(values)
        return dict(zip(keys, values))

    def get_checklist(self):
        """Get the checklist fields extracted ffrom the HTML response.

        Returns:
            dict: a checklist containing the fields extract from the HTML.

        Only the fields not available through the API are extracted from the
        HTML. The parser can be sub-classed to extract any more information.
        """
        return {
            'observers': self.get_observers(),
            'activity': self.get_activity(),
            'protocol': self.get_protocol(),
            'entries': self.get_entries(),
            'comment': self.attributes.get('Comments:', '')
        }

    def get_protocol(self):
        """Get the protocol used for the checklist.

        Returns:
            dict: a dictionary containing the fields describing the protocol
                used to count the birds recorded in the checklist.
        """
        protocol_name = self.attributes.get('Protocol:', None)

        if protocol_name in self.activities:
            protocol_name = self.activities[protocol_name][1]

        duration_str = self.attributes.get('Duration:', '')
        if 'hour' in duration_str:
            duration_hours = int(re.search(
                r'(\d+) h', duration_str).group(1))
        else:
            duration_hours = 0
        if 'min' in duration_str:
            duration_minutes = int(re.search(
                r'(\d+) m', duration_str).group(1))
        else:
            duration_minutes = 0

        distance_str = self.attributes.get('Distance:', '0 kilometer(s)')
        if 'kilometer' in distance_str:
            distance = int(float(re.search(
                r'([\.\d]+) k', distance_str).group(1)) * 1000)
        else:
            distance = int(float(re.search(
                r'([\.\d]+) m', distance_str).group(1)) * 1609)

        return {
            'name': protocol_name,
            'duration_hours': duration_hours,
            'duration_minutes': duration_minutes,
            'distance': distance,
            'area': 0,
        }

    def get_activity(self):
        """Get the activity used for the checklist.

        Returns:
            str: a name for the activity.

        Uses the activities table to separate out specific activities from
        the names eBird uses for protocols.
        """
        protocol_name = self.attributes.get('Protocol:', None)

        if protocol_name in self.activities:
            activity = self.activities[protocol_name][0]
        else:
            activity = self.default_activity

        return activity

    def get_observers(self):
        """Get the additional observers.

        Returns:
            list(str): the observers, excluding the person who submitted the
                checklist.
        """
        try:
            count = int(self.attributes.get('Party Size:', '0'))
        except ValueError:
            count = 0

        names = remove_whitespace(
            self.attributes.get('Observers:', '').split(','))

        return {
            'count': count,
            'names': names,
        }

    def get_entries(self):
        """Get the checklist entries with any additional details for the count.

        Returns:
            list(dict): a list of dicts contains the fields for a checklist
                entry. In turn each contains a list of dicts containing the
                fields describing the breakdown of the entry count by age and
                sex.
        """
        entries = []
        for selector in self.docroot.select('//tr[@class="spp-entry"]'):
            name = selector.select(
                './/h5[@class="se-name"]/text()').extract()[0].strip()
            count = selector.select(
                './/h5[@class="se-count"]/text()').extract()[0].strip()

            species = {
                'name': name,
            }

            try:
                count = int(count)
            except ValueError:
                count = 0

            entries.append({
                'species': species,
                'count': count,
                'details': self.get_entry_details(selector),
                'comment': self.get_entry_comment(selector),
            })
        return entries

    def get_entry_comment(self, node):
        """Get any comment for a checklist entry.

        Args:
            node (HtmlXPathSelector): the node in the tree from where to
                extract the comment.

        Returns:
            str: any comment associated with a checklist entry.
        """
        comment = ''
        selection = node.select('.//p[@class="obs-comments"]/text()')\
            .extract()
        if selection:
            comment = selection[0].strip()
        return comment

    def get_entry_details(self, node):
        """Get the details for each count.

        Args:
            node (HtmlXPathSelector): the node in the tree from where to
                extract the entry details.

        Returns:
            list(dict): a list of dicts containing the fields that describe
                the breakdown of the checklist entry count by age and sex.
        """
        details = []

        xpath = './/div[@class="sd-data-age-sex"]//tr'
        names = node.select(xpath).select('./th/text()').extract()

        for selector in node.select(xpath):
            ages = selector.select('./td')

            if not ages:
                continue

            sex = ages[0].select('./text()').extract()[0]

            for index, age in zip(range(1, 5), names):
                values = ages[index].select('./text()').extract()
                if values:
                    details.append({
                        'age': age,
                        'sex': sex,
                        'count': int(values[0])
                    })
        return details


class EBirdSpider(BaseSpider):
    """Extract checklists recently added to eBird.

    The spider starts by using the API to return the observations for the
    last <n> days for the selected region. The recent observations for a region
    only contain the simple results fields so additional requests are generated
    for the recent observations for each location which contain the full result
    fields. Not all the useful information for a checklist is available through
    the API so the checklist web page from eBird.org is also parsed to extract
    information such as the type of protocol used, breakdowns by age and sex of
    the counts for each species, etc. The completed checklist is then written
    in JSON format to a file.

    Details on the eBird API and the different sets of fields returned can be
    found at https://confluence.cornell.edu/display/CLOISAPI/eBird+API+1.1

    Three settings control the behaviour of the spider:

    DOWNLOAD_DIR: the directory where the downloaded checklists
    will be written in JSON format. The directory will be created if it does
    not exist.

    DURATION: the number of days to fetch observations for. The eBird
    API allows access to observations up to 30 days old.

    EBIRD_INCLUDE_HTML: include data from the checklist web page.

    The spider keeps a list of checklists downloaded and save along with any
    errors raised. These are used to create a status report by the extension,
    SpiderStatusReport which is emailed out when the spider finishes.
    """

    name = 'ebird'
    allowed_domains = ["ebird.org", "secure.birds.cornell.edu"]
    api_parser = JSONParser
    html_parser = HTMLParser

    region_url = "http://ebird.org/ws1.1/data/obs/region/recent?" \
                 "rtype=subnational1&r=%s&back=%d&fmt=json"
    location_url = "http://ebird.org/ws1.1/data/obs/loc/recent?" \
                   "r=%s&detail=full&back=%d&includeProvisional=true&fmt=json"
    checklist_url = "http://ebird.org/ebird/view/checklist?subID=%s"

    def __init__(self, region, **kwargs):
        """Initialize the spider.

        Args:
            region (str): the code identifying the eBird region to fetch
                observations for.

        Returns:
            EBirdSpider: a Scrapy crawler object.
        """
        super(EBirdSpider, self).__init__(**kwargs)
        if not region:
            raise ValueError("You must specify an eBird region")
        self.region = region
        self.log("Downloading checklists for region: %s" % self.region,
                 log.INFO)

        self.checklists = []
        self.errors = []
        self.warnings = []

    def start_requests(self):
        """Configure the spider and issue the first request to the eBird API.

        Returns:
            Request: yields a single request for the recent observations for
                an eBird region.
        """
        self.duration = int(self.settings['DURATION'])
        self.log("Fetching observations for the past %d days" % self.duration,
                 log.INFO)

        self.directory = self.settings['DOWNLOAD_DIR']
        if self.directory and not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.log("Writing checklists to %s" % self.directory, log.INFO)

        self.include_html = self.settings['EBIRD_INCLUDE_HTML']
        if self.include_html:
            self.log("Downloading checklists from API and web pages", log.INFO)
        else:
            self.log("Downloading checklists from API only", log.INFO)

        url = self.region_url % (self.region, self.duration)
        return [Request(url, callback=self.parse_region)]

    def parse_region(self, response):
        """Request the recent observations for each location.

        Args:
            response (Response): the result of calling the eBird API to get the
                recent observations for a region.

        Returns:
            Request: yields a series of requests to the eBird API to get the
                recent observations for each location extracted from the
                recent observations for the region.
        """
        for location in self.api_parser(response).get_locations():
            url = self.location_url % (location['identifier'], self.duration)
            yield Request(url, callback=self.parse_locations)

    def parse_locations(self, response):
        """Create the checklists from the observations.

        Args:
            response (Response): the result of calling the eBird API to get the
                recent observations for a location.

        Returns:
            Request: (when the attribute include_html is True) yields a series
                of requests to the eBird website to get web page used to
                display the details of a checklist.

        Even with the full results fields there is still useful information
        missing so additional requests are generated for the checklist web
        page. Whether the spider continues and processes the checklist web
        page is controlled by the EBIRD_INCLUDE_HTML setting.
        """
        checklists = self.api_parser(response).get_checklists()
        for checklist in checklists:
            checklist['source']['api'] = response.url
            if self.include_html:
                url = self.checklist_url % checklist['identifier']
                yield Request(url, callback=self.parse_checklist,
                              dont_filter=True, meta={'checklist': checklist})
            else:
                self.save_checklist(checklist)

    def parse_checklist(self, response):
        """Parse the missing checklist data from the web page.

        Args:
            response (str): the contents of the checklist web page.

        The checklist first extracted from the call the eBird API is passed
        through the parse_region() and parse_locations() methods using the
        metadata attribute on the Request and Response objects. It is then
        merged with the data has been extracted from the web page and written
        to a file in the directory specified when the spider was created.

        ISSUE: If the setting CONCURRENT_REQUEST != 1 then the checklist data
        in the response sometimes does not match the checklist in the request
        metadata. The problem appears to be intermittent, but for a given run
        of the spider it usually happens after the 4th or 5th response. The
        cause is not known. If the problem occurs then an error is logged and
        the checklist is discarded.
        """
        if not response.url.endswith(response.meta['checklist']['identifier']):
            self.log("Checklists in response and request don't match."
                     "Identifiers: %s != %s" % (
                         response.url[-9:],
                         response.meta['checklist']['identifier']
                     ), log.ERROR)
            return

        update = self.html_parser(response).get_checklist()
        original = response.meta['checklist']
        checklist = self.merge_checklists(original, update)
        checklist['source']['url'] = response.url
        self.save_checklist(checklist)

    def merge_checklists(self, original, update):
        """Merge two checklists together.

        Args:
           original (dict): the checklist extracted from the JSON data.
           update (dict): the checklist extracted from the web page.

        Returns:
           dict: an updated checklist containing values from the first
              (original) updated with values from the second (update).
        """

        entries, warnings = self.merge_entries(
            original['entries'], update['entries'])

        checklist = {
            'meta': {
                'version': original['meta']['version'],
                'language': original['meta']['language'],
            },
            'identifier': original['identifier'],
            'date': original['date'],
            'source': original['source'],
            'observers': self.merge_observers(original['observers'],
                                              update['observers']),
            'activity': update['activity'],
            'location': original['location'],
            'comment': update['comment'],
            'entries': entries,
        }

        if 'protocol' in original:
            protocol = original['protocol'].copy()
            protocol.update(update['protocol'])
        else:
            protocol = update['protocol'].copy()

        checklist['protocol'] = protocol

        if warnings:
            self.warnings.append((checklist, warnings))

        return checklist

    def merge_observers(self, originals, updates):
        """Merge the two lists of observers together.

        Args:
           originals (list): the observer extracted from the API JSON data.
           updates (list): the observers extracted from the web page.

        Returns:
           dict: a dictionary containing all the names reported as observers
           on the two checklists along with a total count of the number of
           observers present.
        """
        names = set(originals['names'])
        names.update(set(updates['names']))

        total = originals['count'] + updates['count']

        for name in originals['names']:
            if name in updates['names']:
                total -= 1

        return {
            'names': list(names),
            'count': total,
        }

    def merge_entries(self, originals, updates):
        """Merge two lists of entries together.

        Args:
           originals (list): the entries extracted from the API JSON data.
           updates (list): the entries extracted from the web page.

        Returns:
           tuple(list, list): a tuple containing the complete (deep) copy of
               the entries merged together and a list of any warnings generated
               when merging the lists together.

        IMPORTANT: The records from the API contain only the species name.
        The subspecies name is discarded. That means if there are two records
        for a species with the same count. It won't be possible to determine
        which record to update when the lists are merged. In this case the
        records will not be merged and only the records from the API will be
        included in the merged list.
        """

        merged = []
        warnings = []

        for entry in originals:
            merged.append({
                'identifier': entry['identifier'],
                'species': entry['species'].copy(),
                'count': entry['count'],
            })

        index = {}

        for entry in merged:
            key = entry['species']['name'].split('(')[0].strip()
            count = entry['count']
            if key in index:
                if count in index[key]:
                    index[key][count].append(entry)
                else:
                    index[key][count] = [entry]
            else:
                index[key] = {count: [entry]}

        for name, counts in index.items():
            for count, entries in counts.items():
                if len(entries) > 1:
                    message = "Could not update record from API. There are" \
                              " %s records that match: species=%s; count=%d." \
                              % (len(entries), name, count)
                    warnings.append(message)
                    self.log(message)

        for entry in updates:
            key = entry['species']['name'].split('(')[0].strip()
            count = entry['count']
            target = None
            added = False

            if key in index:
                if count in index[key]:
                    hits = len(index[key][count])
                else:
                    hits = 0

                if hits == 0:
                    target = {}
                    merged.append(target)
                    added = True
                elif hits == 1:
                    target = index[key][count][0]
            else:
                target = {}
                merged.append(target)
                added = True

            if target is not None:
                target['species'] = entry['species'].copy()
                target['count'] = entry['count']

                if 'comment' in entry:
                    target['comment'] = entry['comment']

                if 'details' in entry:
                    target['details'] = []
                    for detail in entry['details']:
                        target['details'].append(detail.copy())

            if added:
                message = "Web page contains record missing from API:" \
                          " species=%s; count=%d." \
                          % (entry['species']['name'], entry['count'])
                if self.settings['LOG_LEVEL'] == 'DEBUG':
                    warnings.append(message)
                self.log(message)

        return merged, warnings

    def save_checklist(self, checklist):
        """Save the checklist in JSON format.

        Args:
        checklist (dict); the checklist.

        The filename using the source, in this case 'ebird' and the checklist
        identifier so that the data is always written to the same file. The
        directory where the files are written is defined by the setting
        DOWNLOAD_DIR. If the directory attribute is set to None then the
        checklist is not saved (used for testing).

        The saved checklist is added to the list of checklists downloaded so
        far so it can be used to generate a status report once the spider has
        finished.
        """
        if self.directory:
            path = os.path.join(self.directory, "%s-%s.json" % (
                checklist['source']['name'], checklist['identifier']))
            save_json_data(path, checklist)
            self.checklists.append(checklist)

            self.log("Wrote %s: %s %s (%s)" % (
                path, checklist['date'], checklist['location']['name'],
                checklist['source']['submitted_by']), log.DEBUG)
