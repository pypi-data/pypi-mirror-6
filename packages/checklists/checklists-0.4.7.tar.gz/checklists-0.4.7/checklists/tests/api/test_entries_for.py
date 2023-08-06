from datetime import timedelta

from django.db.models.query_utils import Q
from django.test import TestCase
from django.utils import timezone

from checklists.api import entries_for
from checklists.tests.factories import ChecklistFactory, LocationFactory, \
    EntryFactory, SpeciesFactory


class EntriesForTestCase(TestCase):
    """Tests for the API function, entries_for."""

    def test_entries_are_fetched(self):
        """All entries are fetched."""
        today = timezone.now().date()
        location = LocationFactory(name="A")
        checklist = ChecklistFactory(date=today, location=location)

        EntryFactory(checklist=checklist)
        EntryFactory(checklist=checklist)

        actual = entries_for(today, location)

        self.assertEqual(2, len(actual))

    def test_entries_for_date(self):
        """Only entries for the specified date are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        location = LocationFactory(name="A")

        EntryFactory(checklist=ChecklistFactory(
            date=yesterday, location=location))

        expected = EntryFactory(checklist=ChecklistFactory(
            date=today, location=location))

        actual = entries_for(today, location)

        self.assertEqual(expected.id, actual[0].id)

    def test_entries_for_location(self):
        """Only entries for the specified date are fetched."""
        today = timezone.now().date()
        loca = LocationFactory(name="A")
        locb = LocationFactory(name="B")

        EntryFactory(checklist=ChecklistFactory(
            date=today, location=loca))

        expected = EntryFactory(checklist=ChecklistFactory(
            date=today, location=locb))

        actual = entries_for(today, locb)

        self.assertEqual(expected.id, actual[0].id)

    def test_additional_filters(self):
        """Extra filters are used when fetching entries."""
        today = timezone.now().date()
        loca = LocationFactory(name="A")
        locb = LocationFactory(name="B")

        species = SpeciesFactory()
        EntryFactory(checklist=ChecklistFactory(
            date=today, location=loca))

        expected = EntryFactory(checklist=ChecklistFactory(
            date=today, location=locb), species=species)

        actual = entries_for(today, locb, [Q(species=species)])

        self.assertEqual(expected.id, actual[0].id)
