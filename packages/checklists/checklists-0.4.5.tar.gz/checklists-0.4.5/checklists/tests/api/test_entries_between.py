from datetime import timedelta

from django.db.models.query_utils import Q
from django.test import TestCase
from django.utils import timezone

from checklists.api import entries_between
from checklists.tests.factories import ChecklistFactory, EntryFactory, \
    SpeciesFactory


class EntriesBetweenTestCase(TestCase):
    """Tests for the API function, entries_between."""

    def test_entries_are_fetched(self):
        """All entries are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        earlier = today - timedelta(days=2)

        EntryFactory(checklist=ChecklistFactory(date=today))
        EntryFactory(checklist=ChecklistFactory(date=yesterday))
        EntryFactory(checklist=ChecklistFactory(date=earlier))

        actual = entries_between(earlier, today)

        self.assertEqual(3, len(actual))

    def test_entries_start_date(self):
        """Only entries added on or after the start date are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        earlier = today - timedelta(days=2)

        EntryFactory(checklist=ChecklistFactory(date=today))
        EntryFactory(checklist=ChecklistFactory(date=yesterday))
        EntryFactory(checklist=ChecklistFactory(date=earlier))

        actual = entries_between(yesterday, today)

        self.assertEqual(2, len(actual))

    def test_entries_end_date(self):
        """Only entries up to the end date are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        earlier = today - timedelta(days=2)

        EntryFactory(checklist=ChecklistFactory(date=today))
        EntryFactory(checklist=ChecklistFactory(date=yesterday))
        EntryFactory(checklist=ChecklistFactory(date=earlier))

        actual = entries_between(earlier, yesterday)

        self.assertEqual(2, len(actual))

    def test_additional_filters(self):
        """Extra filters are used when fetching entries."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        earlier = today - timedelta(days=2)

        species = SpeciesFactory()
        EntryFactory(checklist=ChecklistFactory(date=today))
        EntryFactory(checklist=ChecklistFactory(date=yesterday))
        expected = EntryFactory(
            checklist=ChecklistFactory(date=earlier), species=species)

        actual = entries_between(earlier, yesterday, [Q(species=species)])

        self.assertEqual(expected.id, actual[0].id)
