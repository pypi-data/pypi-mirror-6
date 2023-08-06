from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Entry
from checklists.tests.factories import ChecklistFactory, SpeciesFactory


class EntryTestCase(TestCase):
    """Test for the Entry model."""

    def test_minimum_required(self):
        """Verify the minimum number of args required to create an object."""
        Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory()
        ).save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Entry().save)

    def test_checklist_is_required(self):
        """Verify species must be set."""
        obj = Entry(species=SpeciesFactory())
        self.assertRaises(ValidationError, obj.save)

    def test_species_is_required(self):
        """Verify species must be set."""
        obj = Entry(checklist=ChecklistFactory())
        self.assertRaises(ValidationError, obj.save)

    def test_default_include(self):
        """Verify that include defaults to True if not set."""
        obj = Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory()
        )
        obj.save()
        self.assertTrue(obj.include)

    def test_default_count(self):
        """Verify that count defaults to zero if not set."""
        obj = Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory()
        )
        obj.save()
        self.assertEqual(0, obj.count)

    def test_default_identifier(self):
        """Verify that identifier defaults to an empty string if not set."""
        obj = Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory()
        )
        obj.save()
        self.assertEqual('', obj.identifier)

    def test_default_description(self):
        """Verify that description defaults to an empty string if not set."""
        obj = Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory()
        )
        obj.save()
        Entry.objects.create(
            checklist=obj.checklist,
            species=obj.species,
        )
        self.assertEqual('', obj.description)

    def test_none_description(self):
        """Verify that description defaults to an empty string if not set."""
        obj = Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory(),
            description=None
        )
        obj.save()
        self.assertEqual('', obj.description)

    def test_default_comment(self):
        """Verify that comment defaults to an empty string if not set."""
        obj = Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory()
        )
        obj.save()
        self.assertEqual('', obj.comment)

    def test_no_tags(self):
        """Verify new entry has no tags."""
        obj = Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory()
        )
        obj.save()
        self.assertEqual([], list(obj.tags.all()))

    def test_representation(self):
        """Verify the object representation is not None or an empty string."""
        obj = Entry(
            checklist=ChecklistFactory(),
            species=SpeciesFactory()
        )
        obj.save()
        self.assertTrue(unicode(obj))
