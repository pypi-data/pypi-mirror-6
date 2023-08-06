import datetime

from django.test import TestCase

from checklists.models import Activity, set_current_user, get_current_user, \
    clear_current_user


class AuditTestCase(TestCase):
    """Test for the audit fields on the model.
    
    The Activity class is used here for the tests since it is simple to set
    up. Any class that inherits from the ChecklistsModel base class could be
    used.
    """

    def setUp(self):
        set_current_user('test')
        self.obj = Activity(slug='birding', name_en='Birding')

    def tearDown(self):
        clear_current_user()

    def test_creation_date_set(self):
        """The created_on field is set when an object is created."""
        now = datetime.datetime.now()
        self.obj.save()
        self.assertTrue(self.obj.created_on > now)

    def test_created_by_set(self):
        """The created_by field is set when an object is created."""
        self.obj.save()
        self.assertEqual(self.obj.created_by, get_current_user())

    def test_modified_on_set(self):
        """The modified_on field is set when an object is created."""
        now = datetime.datetime.now()
        self.obj.save()
        self.assertTrue(self.obj.modified_on > now)

    def test_modified_by_set(self):
        """The modified_by field is set when an object is created."""
        self.obj.save()
        self.assertEqual(self.obj.modified_by, get_current_user())

    def test_created_on_unchanged(self):
        """The created_on field is unchanged when an object is updated."""
        self.obj.save()
        now = datetime.datetime.now()
        self.obj.save()
        self.assertTrue(self.obj.created_on < now)

    def test_creation_by_unchanged(self):
        """The created_by field is unchanged when an object is updated."""
        user = get_current_user()
        self.obj.save()
        set_current_user('other')
        self.obj.save()
        self.assertEqual(self.obj.created_by, user)

    def test_modified_on_updated(self):
        """The modified_on field is updated when an object is saved."""
        self.obj.save()
        now = datetime.datetime.now()
        self.obj.save()
        self.assertTrue(self.obj.modified_on > now)

    def test_modified_by_updated(self):
        """The modified_on field is updated when an object is saved."""
        self.obj.save()
        set_current_user('other')
        self.obj.save()
        self.assertEqual(self.obj.modified_by, get_current_user())

