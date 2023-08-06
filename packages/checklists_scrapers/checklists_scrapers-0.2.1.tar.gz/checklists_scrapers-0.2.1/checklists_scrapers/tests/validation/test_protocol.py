"""Validate the protocol in each downloaded checklist.

Validation Tests:

    Protocol:
        1. the protocol is a dict.

    ProtocolName:
        1. name is a string.
        2. name is set.
        3. name does not have leading/trailing whitespace.

    ProtocolTime:
        1. time is a string.
        2. time has the format 'dd:dd'

    ProtocolDuration
        1. duration hours is an int.
        2. duration minutes is an int

    ProtocolDistance
        1. distance is an int.

    ProtocolArea
        1. area is an int.

    EbirdProtocolName
        1. The protocol names matches the values used on ebird.

    WorldBirdsProtocolName
        1. The protocol names matches the a default value used for WorldBirds.
"""
from checklists_scrapers.tests.validation import checklists, ValidationTestCase


class Protocol(ValidationTestCase):
    """Validate the protocols in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists]

    def test_protocol_type(self):
        """Verify the protocols field contains a dict."""
        for protocol, source in self.protocols:
            self.assertIsInstance(protocol, dict, msg=source)


class ProtocolName(ValidationTestCase):
    """Validate the protocol name in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists]

    def test_name_type(self):
        """Verify the protocol name is a unicode string."""
        for protocol, source in self.protocols:
            self.assertIsInstance(protocol['name'], unicode, msg=source)

    def test_name_set(self):
        """Verify the protocol name is set."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['name'], msg=source)

    def test_name_stripped(self):
        """Verify the protocol name has no extra whitespace."""
        for protocol, source in self.protocols:
            self.assertStripped(protocol['name'], msg=source)


class ProtocolTime(ValidationTestCase):
    """Validate the protocol time in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists]

    def test_name_type(self):
        """Verify the protocol name is a unicode string."""
        for protocol, source in self.protocols:
            self.assertIsInstance(protocol['time'], unicode, msg=source)

    def test_name_format(self):
        """Verify the protocol name is set."""
        for protocol, source in self.protocols:
            self.assertRegexpMatches(protocol['time'], r'\d\d:\d\d', msg=source)


class ProtocolDuration(ValidationTestCase):
    """Validate the duration hours and minutes."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['protocol']['name'] == 'Traveling']

    def test_duration_hours(self):
        """Verify the protocol duration in hours is an int."""
        for protocol, source in self.protocols:
            self.assertIsInstance(protocol['duration_hours'], int, msg=source)

    def test_duration_minutes(self):
        """Verify the protocol duration in minutes is an int."""
        for protocol, source in self.protocols:
            self.assertIsInstance(protocol['duration_minutes'], int, msg=source)


class ProtocolDistance(ValidationTestCase):
    """Validate the distance covered."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['protocol']['name'] == 'Traveling']

    def test_distance(self):
        """Verify the protocol duration in hours is an int."""
        for protocol, source in self.protocols:
            self.assertIsInstance(protocol['distance'], int, msg=source)


class ProtocolArea(ValidationTestCase):
    """Validate the area covered."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['protocol']['name'] == 'Area']

    def test_area(self):
        """Verify the protocol duration in hours is an int."""
        for protocol, source in self.protocols:
            self.assertIsInstance(protocol['area'], int, msg=source)


class EbirdProtocolName(ValidationTestCase):
    """Validate the protocol names in the downloaded checklists from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['source'] == 'ebird']

    def test_expected_names(self):
        """Verify the protocol name is expected.

        This compares the protocol name against the list on ebird.org as of
        2013-06-25 and alerts to any changes.
        """
        expected = ['Traveling', 'Stationary', 'Incidental', 'Area', 'Random',
                    'Oiled Birds', 'Nocturnal Flight Call Count',
                    'Greater Gulf Refuge Waterbird Count',
                    'Heron Area Count', 'Heron Stationary Count']
        for protocol, source in self.protocols:
            self.assertTrue(protocol['name'] in expected, msg=source)


class EbirdTravelingProtocol(ValidationTestCase):
    """Validate the fields set in the Traveling protocol from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['source'] == 'ebird' and
                          checklist['protocol']['name'] == 'Traveling']

    def test_time_set(self):
        """Verify the time is set for the Traveling protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['time'], msg=source)

    def test_duration_set(self):
        """Verify the time is set for the Traveling protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['duration_hours'] or
                            protocol['duration_minutes'], msg=source)

    def test_distance_set(self):
        """Verify the distance is set for the Traveling protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['distance'], msg=source)

    def test_area_clear(self):
        """Verify the area is not set for the Traveling protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['area'], msg=source)


class EbirdStationaryProtocol(ValidationTestCase):
    """Validate the fields set in the Stationary protocol from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['source'] == 'ebird' and
                          checklist['protocol']['name'] == 'Stationary']

    def test_time_set(self):
        """Verify the time is set for the Traveling protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['time'], msg=source)

    def test_duration_set(self):
        """Verify the time is set for the Traveling protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['duration_hours'] or
                            protocol['duration_minutes'], msg=source)

    def test_distance_clear(self):
        """Verify the distance is not set for the Stationary protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['distance'], msg=source)

    def test_area_clear(self):
        """Verify the area is not set for the Stationary protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['area'], msg=source)


class EbirdAreaProtocol(ValidationTestCase):
    """Validate the fields set in the Area protocol from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['source'] == 'ebird' and
                          checklist['protocol']['name'] == 'Area']

    def test_time_set(self):
        """Verify the time is set for the Area protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['time'], msg=source)

    def test_duration_set(self):
        """Verify the time is set for the Area protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['duration_hours'] or
                            protocol['duration_minutes'], msg=source)

    def test_distance_clear(self):
        """Verify the distance is not set for the Area protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['distance'], msg=source)

    def test_area_set(self):
        """Verify the area is set for the Area protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['area'], msg=source)


class EbirdRandomProtocol(ValidationTestCase):
    """Validate the fields set in the Random protocol from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['source'] == 'ebird' and
                          checklist['protocol']['name'] == 'Random']

    def test_time_set(self):
        """Verify the time is set for the Random protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['time'], msg=source)

    def test_duration_set(self):
        """Verify the time is set for the Random protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['duration_hours'] or
                            protocol['duration_minutes'], msg=source)

    def test_distance_set(self):
        """Verify the distance is set for the Random protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['distance'], msg=source)

    def test_area_clear(self):
        """Verify the area is not set for the Random protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['area'], msg=source)


class EbirdIncidentalProtocol(ValidationTestCase):
    """Validate the fields set in the Incidental protocol from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['source'] == 'ebird' and
                          checklist['protocol']['name'] == 'Incidental']

    def test_time_set(self):
        """Verify the time is set for the Incidental protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['time'], msg=source)

    def test_duration_hours_clear(self):
        """Verify duration in hours is not set for the Incidental protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['duration_hours'], msg=source)

    def test_duration_minutes_clear(self):
        """Verify duration in minutesis not set for the Incidental protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['duration_minutes'], msg=source)

    def test_distance_clear(self):
        """Verify the distance is not set for the Incidental protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['distance'], msg=source)

    def test_area_clear(self):
        """Verify the area is not set for the Incidental protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['area'], msg=source)


class WorldBirdsProtocolName(ValidationTestCase):
    """Validate the protocol names in the downloaded checklists from ebird."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['source'] == 'worldbirds']

    def test_expected_names(self):
        """Verify the protocol name is expected.

        WorldBirds does not define a specific protocol. However start time
        and duration spent counting are defined so a default protocol name
        of "Timed visit" is used.
        """
        for protocol, source in self.protocols:
            self.assertEqual(protocol['name'], 'Timed visit', msg=source)


class WorldBirdsTimedVisitProtocol(ValidationTestCase):
    """Validate the fields set in the Time visits protocol from WorldBirds."""

    def setUp(self):
        """Initialize the test."""
        self.protocols = [(checklist['protocol'], checklist['source'])
                          for checklist in checklists
                          if checklist['source'] == 'worldbirds' and
                          checklist['protocol']['name'] == 'Timed visit']

    def test_time_set(self):
        """Verify the time is set for the Timed visit protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['time'], msg=source)

    def test_duration_set(self):
        """Verify the time is set for the Timed visit protocol."""
        for protocol, source in self.protocols:
            self.assertTrue(protocol['duration_hours'] or
                            protocol['duration_minutes'], msg=source)

    def test_distance_clear(self):
        """Verify the distance is not set for the Timed visit protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['distance'], msg=source)

    def test_area_clear(self):
        """Verify the area is not set for the Timed visit protocol."""
        for protocol, source in self.protocols:
            self.assertEqual(0, protocol['area'], msg=source)
