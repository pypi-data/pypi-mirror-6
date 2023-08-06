from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from checklists.api import checklists_between

from checklists.tests.factories import ChecklistFactory


class ChecklistsBetweenTestCase(TestCase):
    """Tests for the API function, checklists_between."""

    def setUp(self):
        self.order = ('-date', 'location__name')

    def test_initial_order(self):
        """Checklists are ordered by date then location."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        ChecklistFactory(date=today, location__name="C")
        ChecklistFactory(date=yesterday, location__name="B")
        ChecklistFactory(date=yesterday, location__name="A")

        expected = ['C', 'A', 'B']
        result = checklists_between(yesterday, today, order=self.order)
        actual = [obj.location.name for obj in result]

        self.assertEqual(expected, actual)

    def test_start_date(self):
        """Only checklists on or after the start date are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        earlier = today - timedelta(days=2)

        ChecklistFactory(date=today)
        ChecklistFactory(date=yesterday)
        ChecklistFactory(date=earlier)

        expected = [today, yesterday]
        result = checklists_between(yesterday, today, order=self.order)
        actual = [obj.date for obj in result]

        self.assertEqual(expected, actual)

    def test_end_date(self):
        """Only checklists on or before the end date are fetched."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        earlier = today - timedelta(days=2)

        ChecklistFactory(date=today)
        ChecklistFactory(date=yesterday)
        ChecklistFactory(date=earlier)

        expected = [yesterday, earlier]
        result = checklists_between(earlier, yesterday, order=self.order)
        actual = [obj.date for obj in result]

        self.assertEqual(expected, actual)

    def test_only_included(self):
        """Only checklists marked as included are fetched"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        earlier = today - timedelta(days=2)

        ChecklistFactory(date=today, include=True)
        ChecklistFactory(date=yesterday, include=False)
        ChecklistFactory(date=earlier, include=True)

        expected = [today, earlier]
        result = checklists_between(earlier, today, order=self.order)
        actual = [checklist.date for checklist in result]

        self.assertEqual(expected, actual)
