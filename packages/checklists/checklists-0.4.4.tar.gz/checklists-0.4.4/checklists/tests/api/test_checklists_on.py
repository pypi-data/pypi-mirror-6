from datetime import date, timedelta

from django.test import TestCase

from checklists.api import checklists_on

from checklists.tests.factories import ChecklistFactory


class ChecklistsOnTestCase(TestCase):
    """Tests for the API function, checklists_on."""

    def setUp(self):
        self.order = ('-date', 'location__name')

    def test_checklists_are_fetched(self):
        """All checklists for the specified date are fetched."""
        today = date.today()

        ChecklistFactory(date=today)
        ChecklistFactory(date=today)

        actual = checklists_on(today, order=self.order)

        self.assertEqual(2, len(actual))

    def test_checklists_for_date(self):
        """Only checklists for the specified date are fetched."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        ChecklistFactory(date=yesterday)
        expected = ChecklistFactory(date=today)

        actual = checklists_on(today, order=self.order)

        self.assertEqual(expected.id, actual[0].id)

    def test_only_included(self):
        """Only checklists marked as included are fetched."""
        today = date.today()

        ChecklistFactory(date=today, include=False)
        expected = ChecklistFactory(date=today, include=True)

        actual = checklists_on(today, order=self.order)

        self.assertEqual(expected.id, actual[0].id)

    def test_order_by_location_name(self):
        """Checklists for a given date are ordered by location name."""
        today = date.today()

        ChecklistFactory(date=today, location__name="C")
        ChecklistFactory(date=today, location__name="A")
        ChecklistFactory(date=today, location__name="B")

        expected = ['A', 'B', 'C']
        result = checklists_on(today, order=self.order)
        actual = [checklist.location.name for checklist in result]
        self.assertEqual(expected, actual)
