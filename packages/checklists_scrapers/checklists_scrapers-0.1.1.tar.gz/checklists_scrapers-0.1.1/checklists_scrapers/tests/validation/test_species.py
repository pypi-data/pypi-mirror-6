"""Validate the species in each entry of the downloaded checklists.

Validation Tests:

   Species:
       1. the species is a dict.
       2. either the common name or scientific name is given.

   SpeciesName:
       1. common name is a string.
       2. common name is set.
       3. common name does not have leading/trailing whitespace.

   SpeciesScientificName:
       1. scientific name is a string.
       2. scientific name is set.
       3. scientific name does not have leading/trailing whitespace.
       4. scientific name has two or three words.
       5. the genus (first word) of the scientific name is capitalized.
       6. the species (second word) of the scientific name is lower case.
       7. the subspecies (third word) of the scientific name is lower case.

"""
from checklists_scrapers.tests.validation import checklists, ValidationTestCase


class Species(ValidationTestCase):
    """Validate the species in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.species = []
        for checklist in checklists:
            for entry in checklist['entries']:
                self.species.append((entry['species'], checklist['source']))

    def test_species_type(self):
        """Verify the species field contains a dict."""
        for species, source in self.species:
            self.assertIsInstance(species, dict, msg=source)

    def test_name_or_scientific_name(self):
        """Verify the either the name or scientific name is set."""
        for species, source in self.species:
            self.assertTrue('name' in species or 'scientific_name' in species,
                            msg=source)


class SpeciesName(ValidationTestCase):
    """Validate the species name in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.species = []
        for checklist in checklists:
            for entry in checklist['entries']:
                self.species.append((entry['species'], checklist['source']))

    def test_name_type(self):
        """Verify the species name is a unicode string."""
        for species, source in self.species:
            if 'name' in species:
                self.assertIsInstance(species['name'], unicode, msg=source)

    def test_name_set(self):
        """Verify the species name is set"""
        for species, source in self.species:
            if 'name' in species:
                self.assertTrue(species['name'], msg=source)

    def test_name_stripped(self):
        """Verify the species name has no extra whitespace."""
        for species, source in self.species:
            if 'name' in species:
                self.assertStripped(species['name'], msg=source)


class SpeciesScientificName(ValidationTestCase):
    """Validate the species scientific name in the downloaded checklists."""

    def setUp(self):
        """Initialize the test."""
        self.species = []
        for checklist in checklists:
            for entry in checklist['entries']:
                self.species.append((entry['species'], checklist['source']))

    def test_scientific_name_type(self):
        """Verify the scientific name is a unicode string."""
        for species, source in self.species:
            if 'name' in species:
                self.assertIsInstance(species['name'], unicode, msg=source)

    def test_scientific_name_set(self):
        """Verify the scientific name is set"""
        for species, source in self.species:
            if 'name' in species:
                self.assertTrue(species['name'], msg=source)

    def test_scientific_name_stripped(self):
        """Verify the scientific name has no extra whitespace."""
        for species, source in self.species:
            if 'name' in species:
                self.assertStripped(species['name'], msg=source)

    def test_scientific_name_items(self):
        """Verify the scientific name two or three components."""
        for species, source in self.species:
            if 'scientific_name' in species:
                items = len(species['scientific_name'].split())
                self.assertTrue(items > 1, msg=source)

    def test_scientific_name_genus(self):
        """Verify the genus of the scientific name."""
        for species, source in self.species:
            if 'scientific_name' in species:
                genus = species['scientific_name'].split()[0]
                self.assertRegexpMatches(genus, r'[A-Z][a-z]+', msg=source)

    def test_scientific_name_species(self):
        """Verify the species of the scientific name."""
        for species, source in self.species:
            if 'scientific_name' in species:
                genus = species['scientific_name'].split()[1]
                self.assertRegexpMatches(genus, r'[a-z]+', msg=source)

    def test_scientific_name_subspecies(self):
        """Verify the subspecies of the scientific name."""
        for species, source in self.species:
            if 'scientific_name' in species and \
                    len(species['scientific_name'].split()) == 3:
                genus = species['scientific_name'].split()[2]
                self.assertRegexpMatches(genus, r'[a-z]+', msg=source)
