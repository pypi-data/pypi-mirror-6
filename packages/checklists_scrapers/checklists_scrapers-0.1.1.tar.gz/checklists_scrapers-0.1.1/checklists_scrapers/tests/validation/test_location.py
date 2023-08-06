"""Validate the locations in the downloaded checklists.

Validation Tests:

   Location:
       1. the location is a dict.

   LocationIdentifier (optional):
       1. identifier is a string.
       2. identifier is set.
       3. identifier does not have leading/trailing whitespace.

   LocationName:
       1. name is a string.
       2. name is set.
       3. name does not have leading/trailing whitespace.

   LocationCounty (optional):
       1. county is a string.

   LocationRegion (optional):
       1. region is a string.

   LocationCountry:
       1. country is a string.

   LocationCoordinates
       1. latitude and longitude are floats.

"""
from checklists_scrapers.tests.validation import checklists, ValidationTestCase


class Location(ValidationTestCase):
    """Validate the locations in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.locations = [(checklist['location'], checklist['source'])
                          for checklist in checklists]

    def test_location_type(self):
        """Verify the locations field contains a dict."""
        for location, source in self.locations:
            self.assertIsInstance(location, dict, msg=source)


class LocationIdentifier(ValidationTestCase):
    """Validate the location identifier in the downloaded checklists.

    This field is optional.
    """

    def setUp(self):
        """Initialize the test."""
        self.identifiers = [
            (checklist['location']['identifier'], checklist['source'])
            for checklist in checklists
            if 'identifier' in checklist['location']
        ]

    def test_identifier_type(self):
        """Verify the location identifier is a unicode string."""
        for identifier, source in self.identifiers:
            self.assertIsInstance(identifier, unicode, msg=source)

    def test_identifier_set(self):
        """Verify the location identifier is set."""
        for identifier, source in self.identifiers:
            self.assertTrue(identifier, msg=source)

    def test_identifier_stripped(self):
        """Verify the location identifier has no extra whitespace."""
        for identifier, source in self.identifiers:
            self.assertStripped(identifier, msg=source)


class LocationName(ValidationTestCase):
    """Validate the location name in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.locations = [(checklist['location'], checklist['source'])
                          for checklist in checklists]

    def test_name_type(self):
        """Verify the location name is a unicode string."""
        for location, source in self.locations:
            self.assertIsInstance(location['name'], unicode, msg=source)

    def test_name_set(self):
        """Verify the location name is set."""
        for location, source in self.locations:
            self.assertTrue(location['name'], msg=source)

    def test_name_stripped(self):
        """Verify the location name has no extra whitespace."""
        for location, source in self.locations:
            self.assertStripped(location['name'], msg=source)


class LocationCounty(ValidationTestCase):
    """Validate the location county name in the downloaded checklists.

    This field is optional.
    """

    def setUp(self):
        """Initialize the test."""
        self.counties = [(checklist['location']['county'], checklist['source'])
                         for checklist in checklists
                         if 'county' in checklist['location']]

    def test_county_type(self):
        """Verify the location county is a unicode string."""
        for county, source in self.counties:
            self.assertIsInstance(county, unicode, msg=source)


class LocationRegion(ValidationTestCase):
    """Validate the location region name in the downloaded checklists.

    This field is optional.
    """

    def setUp(self):
        """Initialize the test."""
        self.regions = [(checklist['location']['region'], checklist['source'])
                        for checklist in checklists
                        if 'region' in checklist['location']]

    def test_region_type(self):
        """Verify the location county is a unicode string."""
        for region, source in self.regions:
            self.assertIsInstance(region, unicode, msg=source)


class LocationCountry(ValidationTestCase):
    """Validate the location country name in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.locations = [(checklist['location'], checklist['source'])
                          for checklist in checklists]

    def test_country_type(self):
        """Verify the location country is a unicode string."""
        for location, source in self.locations:
            self.assertIsInstance(location['country'], unicode, msg=source)


class LocationCoordinates(ValidationTestCase):
    """Validate the latitude and longitude fields."""

    def setUp(self):
        """Initialize the test."""
        self.locations = [(checklist['location'], checklist['source'])
                          for checklist in checklists]

    def test_latitude(self):
        """Verify the location latitude is a unicode string."""
        for location, source in self.locations:
            self.assertIsInstance(location['lat'], float, msg=source)

    def test_longitude(self):
        """Verify the location longitude is a unicode string."""
        for location, source in self.locations:
            self.assertIsInstance(location['lon'], float, msg=source)
