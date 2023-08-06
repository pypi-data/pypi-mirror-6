import mock

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from checklists.models import Location


class LocationTestCase(TestCase):
    """Test for the Location model."""

    def test_required(self):
        """Verify the required args when creating a Location object."""
        Location(
            name='Name',
            country='Country',
        ).save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Location().save)

    def test_default_include(self):
        """Verify that include defaults to True."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertFalse(obj.include)

    def test_name_none(self):
        """Verify that name cannot be None."""
        obj = Location(
            name=None,
            country='Country',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_name_blank(self):
        """Verify that name cannot be an empty string."""
        obj = Location(
            name='',
            country='Country',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_name_missing(self):
        """Verify that name must be set."""
        obj = Location(
            country='Country',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_county_none(self):
        """Verify that county cannot be set to None."""
        obj = Location(
            name='Name',
            county=None,
            country='Country',
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_country_none(self):
        """Verify that country cannot be set to None."""
        obj = Location(
            name='Name',
            country=None,
        )
        self.assertRaises(ValidationError, obj.save)

    def test_country_missing(self):
        """Verify that country must be set."""
        obj = Location(
            name='Name',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_country_blank(self):
        """Verify that country cannot be an empty string."""
        obj = Location(
            name='Name',
            country='',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_default_area(self):
        """Verify that area defaults to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertEqual('', obj.area)

    def test_area_blank(self):
        """Verify that area can be set to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
            area='',
        )
        obj.save()

    def test_area_none(self):
        """Verify that area cannot be set to None."""
        obj = Location(
            name='Name',
            country='Country',
            area=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_default_district(self):
        """Verify that district defaults to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertEqual('', obj.district)

    def test_district_blank(self):
        """Verify that district can be set to an empty string."""
        Location(
            name='Name',
            country='Country',
            district='',
        ).save()

    def test_district_none(self):
        """Verify that district cannot be set to None."""
        obj = Location(
            name='Name',
            country='Country',
            district=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_default_region(self):
        """Verify that region defaults to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertEqual('', obj.region)

    def test_region_blank(self):
        """Verify that region can be set to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
            region='',
        )
        obj.save()

    def test_region_none(self):
        """Verify that region cannot be set to None."""
        obj = Location(
            name='Name',
            country='Country',
            region=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_default_island(self):
        """Verify that island defaults to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertEqual('', obj.island)

    def test_island_blank(self):
        """Verify that island can be set to an empty string."""
        Location(
            name='Name',
            country='Country',
            island='',
        ).save()

    def test_island_none(self):
        """Verify that island cannot be set to None."""
        obj = Location(
            name='Name',
            country='Country',
            island=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_default_latitude(self):
        """Verify that latitude defaults to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertEqual('', obj.lat)

    def test_latitude_blank(self):
        """Verify that latitude can be set to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
            lat='',
        )
        obj.save()

    def test_latitude_none(self):
        """Verify that latitude cannot be set to None."""
        obj = Location(
            name='Name',
            country='Country',
            lat=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_default_longitude(self):
        """Verify that longitude defaults to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertEqual('', obj.lon)

    def test_longitude_blank(self):
        """Verify that longitude can be set to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
            lon='',
        )
        obj.save()

    def test_longitude_none(self):
        """Verify that longitude cannot be set to None."""
        obj = Location(
            name='Name',
            country='Country',
            lon=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_default_grid_refernece(self):
        """Verify that gridref defaults to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertEqual('', obj.gridref)

    def test_grid_reference_blank(self):
        """Verify that gridref can be set to an empty string."""
        obj = Location(
            name='Name',
            country='Country',
            gridref='',
        )
        obj.save()

    def tes_grid_reference_none(self):
        """Verify that gridref cannot be set to None."""
        obj = Location(
            name='Name',
            country='Country',
            gridref=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_representation(self):
        """Verify the object can be displayed in the admin."""
        obj = Location(
            name='Name',
            country='Country',
        )
        obj.save()
        self.assertTrue(unicode(obj))

    def test_monkey_patch_representation(self):
        """Verify changing the representation returned by __unicode__."""
        function = lambda self: "%s %s" % (self.name, self.region)
        with mock.patch.object(Location, '__unicode__', function):
            obj = Location(
                name='Name',
                region='Region',
                country='Country',
            )
            obj.save()
            self.assertEqual("Name Region", unicode(obj))
