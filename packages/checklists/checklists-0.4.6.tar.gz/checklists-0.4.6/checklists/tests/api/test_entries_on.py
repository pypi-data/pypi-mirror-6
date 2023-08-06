from datetime import timedelta

from django.db.models.query_utils import Q
from django.test import TestCase
from django.utils import timezone

from checklists.api import entries_on

from checklists.tests.factories import ChecklistFactory, EntryFactory, \
    SpeciesFactory


class EntriesOnTestCase(TestCase):
    """Tests for the API function, entries_on."""

    def test_entries_are_fetched(self):
        """All entries are fetched."""
        today = timezone.now().date()
        checklist = ChecklistFactory(date=today)

        EntryFactory(checklist=checklist)
        EntryFactory(checklist=checklist)

        actual = entries_on(today)

        self.assertEqual(2, len(actual))

    def test_entries_for_date(self):
        """Only entries for the specified date are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        EntryFactory(checklist=ChecklistFactory(date=yesterday))

        expected = EntryFactory(checklist=ChecklistFactory(date=today))

        actual = entries_on(today)

        self.assertEqual(expected.id, actual[0].id)

    def test_additional_filters(self):
        """Extra filters are used when fetching entries."""
        today = timezone.now().date()

        species = SpeciesFactory()
        EntryFactory(checklist=ChecklistFactory(date=today))
        EntryFactory(checklist=ChecklistFactory(date=today))
        expected = EntryFactory(checklist=ChecklistFactory(
            date=today), species=species)

        actual = entries_on(today, [Q(species=species)])

        self.assertEqual(expected.id, actual[0].id)
