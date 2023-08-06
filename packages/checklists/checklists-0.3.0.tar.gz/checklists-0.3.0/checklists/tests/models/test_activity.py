from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Activity


class ActivityTestCase(TestCase):
    """Test for the Activity model."""

    def test_required(self):
        """Verify the required args when creating an Activity object."""
        Activity(slug='birding', name_en='Birding').save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Activity().save)

    def test_representation(self):
        """Verify the object can be displayed in a foreign key field."""
        obj = Activity(slug='birding', name_en='Birding')
        obj.save()
        self.assertEqual(obj.name, unicode(obj))

    def test_blank_slug(self):
        """Verify slug cannot be an empty string."""
        obj = Activity(slug='', name_en='Birding')
        self.assertRaises(ValidationError, obj.save)

    def test_null_slug(self):
        """Verify slug cannot be None."""
        obj = Activity(slug=None, name_en='Birding')
        self.assertRaises(ValidationError, obj.save)

    def test_unique_slug(self):
        """Verify slug must be unique."""
        Activity.objects.create(slug='birding', name_en='Birding')
        with self.assertRaises(ValidationError):
            Activity(slug='birding', name_en='Birding').save()

    def test_blank_name(self):
        """Verify name cannot be an empty string."""
        obj = Activity(slug='birding', name_en='')
        self.assertRaises(ValidationError, obj.save)

    def test_null_name(self):
        """Verify name cannot be None."""
        obj = Activity(slug='birding', name_en=None)
        self.assertRaises(ValidationError, obj.save)

    def test_update(self):
        """Verify the object attributes can be updated using a dict."""
        obj = Activity()
        obj.__dict__.update({
            'slug': 'birding',
            'name_en': 'Birding',
        })
        obj.save()

    def test_name(self):
        """verify the localized name is set once the object is saved."""
        obj = Activity(slug='birding', name_en='Birding')
        obj.save()
        self.assertEqual('Birding', obj.name)
