from datetime import timedelta

from django.db.models.query_utils import Q
from django.test import TestCase
from django.utils import timezone

from checklists.api import entries_added_on
from checklists.tests.factories import ChecklistFactory, EntryFactory, \
    SpeciesFactory


class EntriesAddedOnTestCase(TestCase):
    """Tests for the API function, entries_added_on."""

    def test_entries_are_fetched(self):
        """All entries are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        EntryFactory(checklist=ChecklistFactory(
            added_on=today, date=today))
        EntryFactory(checklist=ChecklistFactory(
            added_on=today, date=yesterday))

        actual = entries_added_on(today)

        self.assertEqual(2, len(actual))

    def test_entries_for_date(self):
        """Only entries added on the specified date are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        EntryFactory(checklist=ChecklistFactory(
            added_on=yesterday, date=yesterday))
        expected = EntryFactory(checklist=ChecklistFactory(
            added_on=today, date=yesterday))

        actual = entries_added_on(today)

        self.assertEqual(expected.id, actual[0].id)

    def test_additional_filters(self):
        """Extra filters are used when fetching entries."""
        today = timezone.now().date()

        species = SpeciesFactory()
        EntryFactory(checklist=ChecklistFactory(added_on=today))
        EntryFactory(checklist=ChecklistFactory(added_on=today))
        expected = EntryFactory(checklist=ChecklistFactory(
            added_on=today), species=species)

        actual = entries_added_on(today, [Q(species=species)])

        self.assertEqual(expected.id, actual[0].id)
