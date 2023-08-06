from datetime import timedelta
from django.db.models.query_utils import Q

from django.test import TestCase
from django.utils import timezone

from checklists.api import checklists

from checklists.tests.factories import ChecklistFactory, LocationFactory


class ChecklistsTestCase(TestCase):
    """Tests for the API function, checklist()."""

    def setUp(self):
        self.order = ('-date', 'location__name')

    def test_included(self):
        """Only checklist marked as included are fetched."""
        ChecklistFactory(include=False)
        ChecklistFactory(include=True)
        self.assertEqual(1, len(checklists()))

    def test_ordering(self):
        """Verify checklists can be ordered."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        ChecklistFactory(date=today, location=LocationFactory(name='C'))
        ChecklistFactory(date=today, location=LocationFactory(name='A'))
        ChecklistFactory(date=yesterday, location=LocationFactory(name='B'))

        expected = ['A', 'C', 'B']
        actual = [checklist.location.name for checklist
                  in checklists(order=self.order)]
        self.assertEqual(expected, actual)

    def test_filtering(self):
        """Verify checklists can be filtered."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        ChecklistFactory(date=today, location=LocationFactory(name='C'))
        ChecklistFactory(date=today, location=LocationFactory(name='A'))
        ChecklistFactory(date=yesterday, location=LocationFactory(name='B'))
        result = checklists([Q(location__name='A')], self.order)
        self.assertEqual(1, len(result))
