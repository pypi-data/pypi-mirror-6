from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from checklists.api import checklists_added_on

from checklists.tests.factories import ChecklistFactory


class ChecklistsAddedOnTestCase(TestCase):
    """Tests for the API function, checklists_added_on."""

    def setUp(self):
        self.order = ('-date', 'location__name')

    def test_checklists_are_fetched(self):
        """All checklists added on a given date are fetched."""
        today = timezone.now().date()

        ChecklistFactory(added_on=today)
        ChecklistFactory(added_on=today)

        actual = checklists_added_on(today, order=self.order)

        self.assertEqual(2, len(actual))

    def test_checklists_added_on(self):
        """Only checklists added on a given date are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        ChecklistFactory(added_on=yesterday)
        expected = ChecklistFactory(added_on=today)

        actual = checklists_added_on(today, order=self.order)

        self.assertEqual(expected.id, actual[0].id)

    def test_only_included(self):
        """Only checklists marked as included are fetched."""
        today = timezone.now().date()

        ChecklistFactory(date=today, include=False)
        expected = ChecklistFactory(date=today, include=True)

        actual = checklists_added_on(today, order=self.order)

        self.assertEqual(expected.id, actual[0].id)

    def test_most_recent_are_first(self):
        """Checklists added on a given date are ordered by date."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        previous = today - timedelta(days=2)

        ChecklistFactory(added_on=today, date=today)
        ChecklistFactory(added_on=today, date=previous)
        ChecklistFactory(added_on=today, date=yesterday)

        actual = checklists_added_on(today, order=self.order)

        self.assertEqual([today, yesterday, previous],
                         [checklist.date for checklist in actual])

    def test_order_by_location(self):
        """Checklists added on a given date are ordered by location."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        ChecklistFactory(added_on=today, date=today, location__name='A')
        ChecklistFactory(added_on=today, date=yesterday, location__name='C')
        ChecklistFactory(added_on=today, date=yesterday, location__name='B')

        actual = list(checklists_added_on(today, order=self.order))

        self.assertEqual(['A', 'B', 'C'],
                         [checklist.location.name for checklist in actual])
