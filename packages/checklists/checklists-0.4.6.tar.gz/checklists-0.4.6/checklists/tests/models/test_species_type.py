from django.core.exceptions import ValidationError
from django.test import TestCase

from checklists.models import Rank


class RankTestCase(TestCase):
    """Test for the Rank model."""

    def test_required(self):
        """Verify the required args when creating a Rank object."""
        Rank(slug='SPE', name_en='Species').save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Rank().save)

    def test_representation(self):
        """Verify the object can be displayed in a foreign key field."""
        obj = Rank(slug='SPE', name_en='Species')
        obj.save()
        self.assertTrue(unicode(obj))

    def test_blank_slug(self):
        """Verify slug cannot be an empty string."""
        obj = Rank(slug='', name_en='Species')
        self.assertRaises(ValidationError, obj.save)

    def test_null_slug(self):
        """Verify slug cannot be None."""
        obj = Rank(slug=None, name_en='Species')
        self.assertRaises(ValidationError, obj.save)

    def test_slug_unique(self):
        """Verify slug must be unique."""
        Rank.objects.create(slug='SPE', name_en='Species')
        with self.assertRaises(ValidationError):
            Rank(slug='SPE', name_en='Species').save()

    def test_blank_name(self):
        """Verify name cannot be an empty string."""
        obj = Rank(slug='SPE', name_en='')
        self.assertRaises(ValidationError, obj.save)

    def test_null_name(self):
        """Verify name cannot be None."""
        obj = Rank(slug='SPE', name_en=None)
        self.assertRaises(ValidationError, obj.save)

    def test_update(self):
        """Verify the object attributes can be updated using a dict."""
        obj = Rank()
        obj.__dict__.update({
            'slug': 'SPE',
            'name_en': 'Species',
        })
        obj.save()

    def test_name(self):
        """verify the localized name is set once the object is saved."""
        obj = Rank(slug='SPE', name_en='Species')
        obj.save()
        self.assertEqual('Species', obj.name)
