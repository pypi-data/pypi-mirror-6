import mock

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from checklists.models import Species
from checklists.tests.factories import RankFactory, SpeciesGroupFactory


class SpeciesTestCase(TestCase):
    """Test for the Species model."""

    def test_required(self):
        """Verify the required args when creating a Species object."""
        Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        ).save()

    def test_validation(self):
        """Verify object is validated when saved."""
        self.assertRaises(ValidationError, Species().save)

    def test_default_include(self):
        """Verify that include defaults to True."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        )
        obj.save()
        self.assertTrue(obj.include)

    def test_rank_none(self):
        """Verify that species type can be None."""
        Species(
            rank=None,
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        ).save()

    def test_rank_missing(self):
        """Verify that rank can be omitted."""
        Species(
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        ).save()

    def test_group_none(self):
        """Verify that group can be set to None."""
        Species(
            rank=RankFactory(),
            group=None,
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        ).save()

    def test_standard_name_none(self):
        """Verify that iou name cannot be set to None."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name=None,
            scientific_name='Scientific Name',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_standard_name_missing(self):
        """Verify that iou name must be set."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            scientific_name='Scientific Name',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_standard_name_blank(self):
        """Verify that iou name cannot be an empty string."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='',
            scientific_name='Scientific Name',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_scientific_name_none(self):
        """Verify that scientific name cannot be set to None."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name=None,
        )
        self.assertRaises(ValidationError, obj.save)

    def test_scientific_name_missing(self):
        """Verify that scientific name must be set."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_scientific_name_blank(self):
        """Verify that scientific name cannot be an empty string."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='',
        )
        self.assertRaises(ValidationError, obj.save)

    def test_default_common_name(self):
        """Verify that common name defaults to an empty string."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        )
        obj.save()
        self.assertEqual('', obj.common_name)

    def test_common_name_none(self):
        """Verify that common name cannot be set to None."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
            common_name_en=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_default_plural_name(self):
        """Verify that plural name defaults to an empty string."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        )
        obj.save()
        self.assertEqual('', obj.plural_name)

    def test_plural_name_none(self):
        """Verify that plural name cannot be set to None."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
            plural_name_en=None,
        )
        self.assertRaises(IntegrityError, obj.save)

    def test_default_name_order(self):
        """Verify that name order defaults to zero."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        )
        obj.save()
        self.assertEqual(0, obj.order)

    def test_name_order_none(self):
        """Verify that name order cannot be set to None"""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
            order=None
        )
        self.assertRaises(ValidationError, obj.save)

    def test_name_order_negative(self):
        """Verify that name order cannot be a negative integer."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
            order=-1
        )
        self.assertRaises(ValidationError, obj.save)

    def test_no_status(self):
        """Verify new species has no status."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        )
        obj.save()
        self.assertEqual([], list(obj.status.all()))

    def test_representation(self):
        """Verify the object can be displayed in the admin."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
            common_name_en="Common Name"
        )
        obj.save()
        self.assertTrue(unicode(obj))

    def test_common_name_representation(self):
        """Verify representation uses the common name."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
            common_name_en="Common Name"
        )
        obj.save()
        self.assertEqual("Common Name", unicode(obj))

    def test_standard_name_representation(self):
        """Verify representation uses the iou name if common name not set."""
        obj = Species(
            rank=RankFactory(),
            group=SpeciesGroupFactory(),
            standard_name='Standard Name',
            scientific_name='Scientific Name',
        )
        obj.save()
        self.assertEqual("Standard Name", unicode(obj))

    def test_monkey_patch_representation(self):
        """Verify changing the representation returned by __unicode__."""
        function = lambda self: self.scientific_name
        with mock.patch.object(Species, '__unicode__', function):
            obj = Species(
                rank=RankFactory(),
                group=SpeciesGroupFactory(),
                standard_name='Standard Name',
                scientific_name='Scientific Name',
            )
            obj.save()
            self.assertEqual("Scientific Name", unicode(obj))
