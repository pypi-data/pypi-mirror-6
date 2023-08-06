from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Detail
from checklists.tests.factories import EntryFactory


class DetailTestCase(TestCase):
    """Test for the Detail model."""

    def test_minimum_required(self):
        """Verify the minimum number of args required to create an object."""
        Detail(entry=EntryFactory(), count=0).save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Detail().save)

    def test_entry_is_required(self):
        """Verify entry must be set."""
        obj = Detail(count=1)
        self.assertRaises(ValidationError, obj.save)

    def test_count_is_required(self):
        """Verify count must be set."""
        obj = Detail(entry=EntryFactory())
        self.assertRaises(ValidationError, obj.save)

    def test_default_latitude(self):
        """Verify that latitude defaults to an empty string."""
        obj = Detail(entry=EntryFactory(), count=0)
        obj.save()
        self.assertEqual('', obj.lat)

    def test_default_longitude(self):
        """Verify that longitude defaults to an empty string."""
        obj = Detail(entry=EntryFactory(), count=0)
        obj.save()
        self.assertEqual('', obj.lon)

    def test_age_is_optional(self):
        """Verify age can be left unset."""
        obj = Detail(entry=EntryFactory(), count=0)
        obj.save()
        self.assertIsNone(obj.age)

    def test_sex_is_optional(self):
        """Verify sex can be left unset."""
        obj = Detail(entry=EntryFactory(), count=0)
        obj.save()
        self.assertIsNone(obj.sex)

    def test_plumage_is_optional(self):
        """Verify plumage can be left unset."""
        obj = Detail(entry=EntryFactory(), count=0)
        obj.save()
        self.assertIsNone(obj.plumage)

    def test_direction_is_optional(self):
        """Verify direction can be left unset."""
        obj = Detail(entry=EntryFactory(), count=0)
        obj.save()
        self.assertIsNone(obj.direction)

    def test_representation(self):
        """Verify the object representation is not None or an empty string."""
        obj = Detail(entry=EntryFactory(), count=0)
        obj.save()
        self.assertTrue(unicode(obj))
