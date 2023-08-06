from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from checklists.models import SpeciesGroup


class SpeciesGroupTestCase(TestCase):
    """Test for the SpeciesGroup model."""

    def test_required(self):
        """Verify the required args when creating a SpeciesGroup object."""
        SpeciesGroup(
            order='Order', family='Family', genus='Genus', name_en='Group'
        ).save()

    def test_representation(self):
        """Verify the object can be displayed in the admin."""
        obj = SpeciesGroup(
            order='Order', family='Family', genus='Genus', name_en='Group'
        )
        obj.save()
        self.assertEqual(obj.name, unicode(obj))

    def test_blank_order(self):
        """Verify order cannot be an empty string."""
        with self.assertRaises(ValidationError):
            SpeciesGroup(
                order='', family='Family', genus='Genus', name_en='Group'
            ).save()

    def test_null_order(self):
        """Verify order cannot be None."""
        with self.assertRaises(ValidationError):
            SpeciesGroup(
                order=None, family='Family', genus='Genus', name_en='Group'
            ).save()

    def test_blank_family(self):
        """Verify family can be an empty string."""
        SpeciesGroup(
            order='Order', family='', genus='Genus', name_en='Group'
        ).save()

    def test_null_family(self):
        """Verify family cannot be None."""
        with self.assertRaises(IntegrityError):
            SpeciesGroup(
                order='Order', family=None, genus='Genus', name_en='Group'
            ).save()

    def test_blank_genus(self):
        """Verify genus can be an empty string."""
        SpeciesGroup(
            order='Order', family='Family', genus='', name_en='Group'
        ).save()

    def test_null_genus(self):
        """Verify genus cannot be None."""
        with self.assertRaises(IntegrityError):
            SpeciesGroup(
                order='Order', family='Family', genus=None, name_en='Group'
            ).save()

    def test_blank_name(self):
        """Verify name cannot be an empty string."""
        with self.assertRaises(ValidationError):
            SpeciesGroup(
                order='Order', family='Family', genus='Genis', name_en=''
            ).save()

    def test_null_name(self):
        """Verify name cannot be None."""
        with self.assertRaises(ValidationError):
            SpeciesGroup(
                order='Order', family='Family', genus='Genus', name_en=None
            ).save()

    def test_update(self):
        """Verify the object attributes can be updated using a dict."""
        obj = SpeciesGroup()
        obj.__dict__.update({
            'order': 'Order',
            'family': 'Family',
            'genus': 'Genus',
            'name_en': 'Group',
        })
        obj.save()

    def test_name(self):
        """verify the localized name is set once the object is saved."""
        obj = SpeciesGroup(
            order='Order', family='Family', genus='Genus', name_en='Group'
        )
        obj.save()
        self.assertEqual('Group', obj.name)
