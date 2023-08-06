from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Sex


class SexTestCase(TestCase):
    """Test for the Sex model."""

    def test_required(self):
        """Verify the required args when creating a Sex object."""
        Sex(slug='F', name_en='Female').save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Sex().save)

    def test_representation(self):
        """Verify the object can be displayed in a foreign key field."""
        obj = Sex(slug='F', name_en='Female')
        obj.save()
        self.assertTrue(unicode(obj))

    def test_blank_slug(self):
        """Verify slug cannot be an empty string."""
        obj = Sex(slug='', name_en='Female')
        self.assertRaises(ValidationError, obj.save)

    def test_null_slug(self):
        """Verify slug cannot be None."""
        obj = Sex(slug=None, name_en='Female')
        self.assertRaises(ValidationError, obj.save)

    def test_unique_name(self):
        """Verify slug must be unique."""
        Sex.objects.create(slug='F', name_en='Female')
        with self.assertRaises(ValidationError):
            Sex(slug='F', name_en='Female').save()

    def test_blank_name(self):
        """Verify name cannot be an empty string."""
        obj = Sex(slug='F', name_en='')
        self.assertRaises(ValidationError, obj.save)

    def test_null_name(self):
        """Verify name cannot be None."""
        obj = Sex(slug='F', name_en=None)
        self.assertRaises(ValidationError, obj.save)

    def test_update(self):
        """Verify the object attributes can be updated using a dict."""
        obj = Sex()
        obj.__dict__.update({
            'slug': 'F',
            'name_en': 'Female',
        })
        obj.save()

    def test_name(self):
        """verify the localized name is set once the object is saved."""
        obj = Sex(slug='F', name_en='Female')
        obj.save()
        self.assertEqual('Female', obj.name)
