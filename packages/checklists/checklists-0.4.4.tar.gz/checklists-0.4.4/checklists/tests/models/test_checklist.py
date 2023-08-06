from datetime import date, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Location, Checklist, Method

from checklists.tests.factories import LocationFactory, ChecklistFactory, \
    ProtocolFactory, ObserverFactory


class ChecklistTestCase(TestCase):
    """Test for the Checklist model."""

    def test_required(self):
        """Verify the args required to create an object."""
        Checklist(
            location=LocationFactory(),
            date=date.today(),
        ).save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Checklist().save)

    def test_default_include(self):
        """Verify that include defaults to False."""
        obj = Checklist(
            location=LocationFactory(),
            date=date.today(),
        )
        obj.save()
        self.assertFalse(obj.include)

    def test_default_identifier(self):
        """Verify that identifier defaults to an empty string."""
        obj = Checklist(
            location=LocationFactory(),
            date=date.today(),
        )
        obj.save()
        self.assertFalse(obj.identifier)

    def test_location_is_required(self):
        """Verify location must be specified when creating an object."""
        obj = Checklist(
            date=date.today(),
        )
        self.assertRaises(ValidationError, obj.save)

    def test_date_is_required(self):
        """Verify date must be specified when creating an object."""
        obj = Checklist(
            location=LocationFactory(),
        )
        self.assertRaises(ValidationError, obj.save)

    def test_method_is_optional(self):
        """Verify method is optional."""
        method = Method(
            protocol=ProtocolFactory(),
            checklist=ChecklistFactory(),
            time=time(12, 0, 0),
        )
        method.save()

        method.checklist.method.delete()
        method.checklist.save()

    def test_default_source(self):
        """Verify source defaults to an empty string."""
        obj = Checklist(
            location=LocationFactory(),
            date=date.today(),
        )
        obj.save()
        self.assertEqual('', obj.source)

    def test_default_url(self):
        """Verify url defaults to an empty string."""
        obj = Checklist(
            location=LocationFactory(),
            date=date.today(),
        )
        obj.save()
        self.assertEqual('', obj.url)

    def test_default_reporter(self):
        """Verify reporter is None."""
        obj = Checklist(
            location=LocationFactory(),
            date=date.today(),
        )
        obj.save()
        self.assertEqual(None, obj.reporter)

    def test_added_on_is_set(self):
        """Verify added_on is set for new objects."""
        location = Location.objects.create(name='Location')
        obj = Checklist(
            location=location,
            date=date.today(),
        )
        obj.save()
        self.assertEqual(date.today(), obj.added_on)

    def test_added_on_is_unchanged(self):
        """Verify added_on is not updated when existing objects are saved."""
        yesterday = date.today() - timedelta(days=1)
        checklist = ChecklistFactory()
        checklist.added_on = yesterday
        checklist.save()

        self.assertEqual(yesterday, checklist.added_on)

    def test_default_complete(self):
        """Verify complete defaults to False for new objects."""
        location = Location.objects.create(name='Location')
        obj = Checklist(
            location=location,
            date=date.today(),
        )
        obj.save()
        self.assertEqual(False, obj.complete)

    def test_default_observer_count(self):
        """Verify observer count is set from number of observers."""
        location = Location.objects.create(name='Location')
        obj = Checklist(
            location=location,
            date=date.today(),
        )
        obj.save()
        obj.observers.add(ObserverFactory(), ObserverFactory(),
                          ObserverFactory())
        obj.save()
        self.assertEqual(3, obj.observers_count)

    def test_default_url(self):
        """Verify url defaults to an empty string for new objects."""
        location = Location.objects.create(name='Location')
        obj = Checklist(
            location=location,
            date=date.today(),
        )
        obj.save()
        self.assertEqual('', obj.url)

    def test_default_comment(self):
        """Verify comment defaults to an empty string for new objects."""
        location = Location.objects.create(name='Location')
        obj = Checklist(
            location=location,
            date=date.today(),
        )
        obj.save()
        self.assertEqual('', obj.comment)
