from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Direction


class DirectionTestCase(TestCase):
    """Test for the Direction model."""

    def test_required(self):
        """Verify the required args when creating a Direction object."""
        Direction(slug='SE', name_en='Southeast').save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Direction().save)

    def test_representation(self):
        """Verify the object can be displayed in a foreign key field."""
        obj = Direction(slug='SE', name_en='Southeast')
        obj.save()
        self.assertTrue(unicode(obj))

    def test_blank_slug(self):
        """Verify slug cannot be an empty string."""
        obj = Direction(slug='', name_en='Southeast')
        self.assertRaises(ValidationError, obj.save)

    def test_null_slug(self):
        """Verify slug cannot be None."""
        obj = Direction(slug=None, name_en='Southeast')
        self.assertRaises(ValidationError, obj.save)

    def test_unique_slug(self):
        """Verify slug must be unique."""
        Direction.objects.create(slug='SE', name_en='Southeast')
        with self.assertRaises(ValidationError):
            Direction(slug='SE', name_en='Southeast').save()

    def test_blank_name(self):
        """Verify name cannot be an empty string."""
        obj = Direction(slug='SE', name_en='')
        self.assertRaises(ValidationError, obj.save)

    def test_null_name(self):
        """Verify name cannot be None."""
        obj = Direction(slug='SE', name_en=None)
        self.assertRaises(ValidationError, obj.save)

    def test_update(self):
        """Verify the object attributes can be updated using a dict."""
        obj = Direction()
        obj.__dict__.update({
            'slug': 'SE',
            'name_en': 'Southeast',
        })
        obj.save()

    def test_name(self):
        """verify the localized name is set once the object is saved."""
        obj = Direction(slug='SE', name_en='Southeast')
        obj.save()
        self.assertEqual('Southeast', obj.name)
