from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Age


class AgeTestCase(TestCase):
    """Test for the Age model."""

    def test_required(self):
        """Verify the required args when creating a Age object."""
        Age(slug='JUV', name_en='Juvenile').save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Age().save)

    def test_representation(self):
        """Verify the object can be displayed in a foreign key field."""
        obj = Age(slug='JUV', name_en='Juvenile')
        obj.save()
        self.assertTrue(unicode(obj))

    def test_blank_slug(self):
        """Verify slug cannot be an empty string."""
        obj = Age(slug='', name_en='Juvenile')
        self.assertRaises(ValidationError, obj.save)

    def test_null_slug(self):
        """Verify slug cannot be None."""
        obj = Age(slug=None, name_en='Juvenile')
        self.assertRaises(ValidationError, obj.save)

    def test_blank_name(self):
        """Verify name cannot be an empty string."""
        obj = Age(slug='JUV', name_en='')
        self.assertRaises(ValidationError, obj.save)

    def test_null_name(self):
        """Verify name cannot be None."""
        obj = Age(slug='JUV', name_en=None)
        self.assertRaises(ValidationError, obj.save)

    def test_unique_name(self):
        """Verify slug must be unique."""
        Age.objects.create(slug='JUV', name_en='Juvenile')
        with self.assertRaises(ValidationError):
            Age(slug='JUV', name_en='Juvenile').save()

    def test_update(self):
        """Verify the object attributes can be updated using a dict."""
        obj = Age()
        obj.__dict__.update({
            'slug': 'JUV',
            'name_en': 'Juvenile',
        })
        obj.save()

    def test_name(self):
        """verify the localized name is set once the object is saved."""
        obj = Age(slug='JUV', name_en='Juvenile')
        obj.save()
        self.assertEqual('Juvenile', obj.name)
