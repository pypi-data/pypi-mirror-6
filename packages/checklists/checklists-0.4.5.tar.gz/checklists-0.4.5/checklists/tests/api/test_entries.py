from datetime import timedelta

from django.db.models.query_utils import Q
from django.test import TestCase
from django.utils import timezone

from checklists.api import entries

from checklists.tests.factories import ChecklistFactory, EntryFactory, \
    SpeciesFactory


class EntriesTestCase(TestCase):
    """Tests for the API function, entries()."""

    def test_included_entries(self):
        """Only entries marked as included are fetched."""
        EntryFactory(include=False)
        expected = EntryFactory(include=True)

        actual = entries()

        self.assertEqual(expected.id, actual[0].id)

    def test_included_checklists(self):
        """Only entries from checklists marked as included are fetched."""
        today = timezone.now().date()

        EntryFactory(checklist=ChecklistFactory(include=False, date=today))
        expected = EntryFactory(checklist=ChecklistFactory(
            include=True, date=today))

        actual = entries()

        self.assertEqual(expected.id, actual[0].id)

    def test_ordering(self):
        """Entries can be ordered."""
        checklist = ChecklistFactory()
        EntryFactory(count=1, checklist=checklist,
                     species=SpeciesFactory(order=100))
        EntryFactory(count=1, checklist=checklist,
                     species=SpeciesFactory(order=99))

        actual = entries(order=('species__order',))

        self.assertEqual(99, actual[0].species.order)

    def test_filtering(self):
        """Entries can be filtered."""
        EntryFactory(count=1)
        expected = EntryFactory(count=10)

        actual = entries([Q(count__gte=10)])

        self.assertEqual(expected.id, actual[0].id)

    def test_reverse_ordering(self):
        """Order of results can be changed."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        EntryFactory(count=1, checklist=ChecklistFactory(
            date=today))
        expected = EntryFactory(count=10, checklist=ChecklistFactory(
            date=yesterday))

        actual = entries(order=('-count',))

        self.assertEqual(expected.id, actual[0].id)

    def test_filtering_and_ordering(self):
        """Both filtering and ordering can be changed."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        EntryFactory(count=1, checklist=ChecklistFactory(
            date=today, location__name="A"))
        EntryFactory(count=10, checklist=ChecklistFactory(
            date=yesterday, location__name="A"))
        EntryFactory(count=20, checklist=ChecklistFactory(
            date=yesterday, location__name="B"))

        actual = entries([Q(count__gte=10)], ('-count', 'species__order'))

        self.assertEqual(20, actual[0].count)
