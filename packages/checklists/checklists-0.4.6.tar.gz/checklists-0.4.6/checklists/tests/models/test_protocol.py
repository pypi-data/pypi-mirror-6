from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Protocol


class protocolTestCase(TestCase):
    """Test for the protocol model."""

    def test_required(self):
        """Verify the required args when creating a protocol object."""
        Protocol(slug='protocol', name_en='protocol').save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Protocol().save)

    def test_representation(self):
        """Verify the object can be displayed in a foreign key field."""
        obj = Protocol(slug='protocol', name_en='protocol')
        obj.save()
        self.assertTrue(unicode(obj))

    def test_blank_slug(self):
        """Verify slug cannot be an empty string."""
        obj = Protocol(slug='', name_en='protocol')
        self.assertRaises(ValidationError, obj.save)

    def test_null_slug(self):
        """Verify slug cannot be None."""
        obj = Protocol(slug=None, name_en='protocol')
        self.assertRaises(ValidationError, obj.save)

    def test_unique_slug(self):
        """Verify slug must be unique."""
        Protocol.objects.create(slug='protocol', name_en='protocol')
        with self.assertRaises(ValidationError):
            Protocol(slug='protocol', name_en='Protocol').save()

    def test_blank_name(self):
        """Verify name cannot be an empty string."""
        obj = Protocol(slug='protocol', name_en='')
        self.assertRaises(ValidationError, obj.save)

    def test_null_name(self):
        """Verify name cannot be None."""
        obj = Protocol(slug='protocol', name_en=None)
        self.assertRaises(ValidationError, obj.save)

    def test_update(self):
        """Verify the object attributes can be updated using a dict."""
        obj = Protocol()
        obj.__dict__.update({
            'slug': 'protocol',
            'name_en': 'protocol',
        })
        obj.save()

    def test_name(self):
        """verify the localized name is set once the object is saved."""
        obj = Protocol(slug='protocol', name_en='protocol')
        obj.save()
        self.assertEqual('protocol', obj.name)
