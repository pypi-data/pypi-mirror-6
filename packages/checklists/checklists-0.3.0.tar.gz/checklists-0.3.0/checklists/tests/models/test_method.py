from datetime import time

from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Method
from checklists.tests.factories import ProtocolFactory, ChecklistFactory


class MethodTestCase(TestCase):
    """Test for the Method model."""

    def test_minimum_required(self):
        """Verify the minimum number of args required to create an object."""
        Method(
            protocol=ProtocolFactory(),
            time=time(12, 0, 0),
        ).save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Method().save)

    def test_protocol_is_required(self):
        """Verify protocol type must be set."""
        obj = Method(
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
        )
        self.assertRaises(ValidationError, obj.save)

    def test_checklist_is_optional(self):
        """Verify checklist is optional."""
        Method(
            protocol=ProtocolFactory(),
            checklist=None,
            time=time(12, 0, 0),
        ).save()

    def test_default_duration_hours(self):
        """Verify that duration hours defaults to zero if not set."""
        obj = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
        )
        obj.save()
        self.assertEqual(0, obj.duration_hours)

    def test_negative_duration_hours(self):
        """Verify that duration hours cannot be negative."""
        obj = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
            duration_hours=-1,
        )
        self.assertRaises(ValidationError, obj.save)

    def test_default_duration_minutes(self):
        """Verify that duration minutes defaults to zero if not set."""
        obj = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
        )
        obj.save()
        self.assertEqual(0, obj.duration_minutes)

    def test_negative_duration_minutes(self):
        """Verify that duration minutes cannot be negative."""
        obj = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
            duration_minutes=-1,
        )
        self.assertRaises(ValidationError, obj.save)

    def test_default_distance(self):
        """Verify that distance defaults to zero if not set."""
        obj = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
        )
        obj.save()
        self.assertEqual(0, obj.distance)

    def test_negative_distance(self):
        """Verify that distance cannot be negative."""
        obj = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
            distance=-1,
        )
        self.assertRaises(ValidationError, obj.save)

    def test_default_area(self):
        """Verify that area defaults to zero if not set."""
        obj = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0)
        )
        obj.save()
        self.assertEqual(0, obj.area)

    def test_negative_area(self):
        """Verify that area cannot be negative."""
        obj = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
            area=-1,
        )
        self.assertRaises(ValidationError, obj.save)

    def test_representation(self):
        """Verify the object representation is not None or an empty string."""
        obj = Method.objects.create(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0)
        )
        self.assertTrue(unicode(obj))
