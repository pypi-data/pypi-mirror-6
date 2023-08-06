from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Plumage


class PlumageTestCase(TestCase):
    """Test for the Plumage model."""

    def test_required(self):
        """Verify the required args when creating a Plumage object."""
        Plumage(slug='BPH', name_en='Blue Phase').save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Plumage().save)

    def test_representation(self):
        """Verify the object can be displayed in a foreign key field."""
        obj = Plumage(slug='BPH', name_en='Blue Phase')
        obj.save()
        self.assertTrue(unicode(obj))

    def test_blank_slug(self):
        """Verify slug cannot be an empty string."""
        obj = Plumage(slug='', name_en='Blue Phase')
        self.assertRaises(ValidationError, obj.save)

    def test_null_slug(self):
        """Verify slug cannot be None."""
        obj = Plumage(slug=None, name_en='Blue Phase')
        self.assertRaises(ValidationError, obj.save)

    def test_unique_slug(self):
        """Verify slug must be unique."""
        Plumage.objects.create(slug='BPH', name_en='Blue Phase')
        with self.assertRaises(ValidationError):
            Plumage(slug='BPH', name_en='Blue Phase').save()

    def test_blank_name(self):
        """Verify name cannot be an empty string."""
        obj = Plumage(slug='BPH', name_en='')
        self.assertRaises(ValidationError, obj.save)

    def test_null_name(self):
        """Verify name cannot be None."""
        obj = Plumage(slug='BPH', name_en=None)
        self.assertRaises(ValidationError, obj.save)

    def test_update(self):
        """Verify the object attributes can be updated using a dict."""
        obj = Plumage()
        obj.__dict__.update({
            'slug': 'BPH',
            'name_en': 'Blue Phase',
        })
        obj.save()

    def test_name(self):
        """verify the localized name is set once the object is saved."""
        obj = Plumage(slug='BPH', name_en='Blue Phase')
        obj.save()
        self.assertEqual('Blue Phase', obj.name)
