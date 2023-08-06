"""Tests for the load_checklists commands.

LoadTestCase:
    verify the basic operation of the load_checklists command.
ArgumentsTestCase:
    verify the command line arguments passed to the load_checklists command.
FilterTestCase
    verify the filtering of checklists during loading.
CreateChecklistTestCase
    verify the command loads all the data for a checklist.
StatusReportTestCase
    verify the status report generated when the command is run.
UpdateChecklistTestCase
    verify the command updates existing checklists.
AliasTestCase
    verify the alias tables for Location and Species are used.
ErrorOnLoadTestCase
    verify the handling of errors when loading checklists.

The reference (static) data used for the tests are created in the database
using the setUpModule() function when the module is first loaded. Conversely
the database is cleaned up when the tests complete using the tearDownModule()
function. This avoids repeated reloading data that does not change when each
test case is run.

Similarly the setup for each test case is done at the class level wherever
possible to avoid repeatedly performing the same setup steps for each test
and making the tests run a lot faster.

"""

import json
import mock
import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.management import call_command
from django.db.models.query_utils import Q
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from checklists.models import Location, Species, Checklist, Entry, \
    Observer, Protocol, Method, Map, Activity, Age, Sex, Detail, Filter


def setUpModule():
    Protocol.objects.create(slug='STA', name_en='Stationary')
    Protocol.objects.create(slug='TRV', name_en='Travelling')

    Activity.objects.create(slug='BIR', name_en='Birding')
    Activity.objects.create(slug='SEA', name_en='Seawatching')

    Species.objects.create(standard_name="Manx Shearwater",
                           common_name_en="Manx Shearwater",
                           scientific_name="Puffinus puffinus")

    Species.objects.create(standard_name="Northern Gannet",
                           common_name_en="Gannet",
                           scientific_name="Morus bassanus")

    Age.objects.create(slug='AD', name_en='Adult')
    Age.objects.create(slug='IMM', name_en='Immature')
    Sex.objects.create(slug='X', name_en='Sex not known')

    Map.objects.create(
        name='Stationary',
        content_type=ContentType.objects.get_for_model(Protocol),
        object_id=Protocol.objects.get(name_en='Stationary').id
    )
    Map.objects.create(
        name='Travelling',
        content_type=ContentType.objects.get_for_model(Protocol),
        object_id=Protocol.objects.get(name_en='Travelling').id
    )
    Map.objects.create(
        name='Birding',
        content_type=ContentType.objects.get_for_model(Activity),
        object_id=Activity.objects.get(name_en='Birding').id
    )
    Map.objects.create(
        name='Seawatching',
        content_type=ContentType.objects.get_for_model(Activity),
        object_id=Activity.objects.get(name_en='Seawatching').id
    )
    Map.objects.create(
        name='Adult',
        content_type=ContentType.objects.get_for_model(Age),
        object_id=Age.objects.get(name_en='Adult').id
    )
    Map.objects.create(
        name='Immature',
        content_type=ContentType.objects.get_for_model(Age),
        object_id=Age.objects.get(name_en='Immature').id
    )
    Map.objects.create(
        name='Sex Unknown',
        content_type=ContentType.objects.get_for_model(Sex),
        object_id=Sex.objects.get(name_en='Sex not known').id
    )


def tearDownModule():
    Protocol.objects.all().delete()
    Activity.objects.all().delete()
    Species.objects.all().delete()
    Age.objects.all().delete()
    Sex.objects.all().delete()
    Map.objects.all().delete()


def downloaded_checklist():
    """Generate a checklist with a comprehensive set of fields.

    Returns:
       A checklist, in the form of a nested dictionary, that contains data for
       all of the fields in the database.
    """
    return {
        "meta": {
            "version": 1,
            "language": "en",
        },
        "identifier": "S1234567",
        "date": "2013-07-05",
        "location": {
            "identifier": "L12345",
            "name": "Cape Clear",
            "county": "Cork",
            "region": "South-West",
            "country": "Eire",
            "lat": 51.433333,
            "lon": -9.5
        },
        "activity": "Seawatching",
        "protocol": {
            "name": "Stationary",
            "time": "07:00",
            "duration_hours": 3,
            "duration_minutes": 25,
            "area": 22,
            "distance": 2000,
        },
        "observers": {
            'count': 5,
            'names': [
                "Martin Swift",
                "Bob Roller",
                "June Finch"
            ]
        },
        "source": {
            "name": "ebird",
            "url": "http://http://ebird.org/ebird/view/checklist?subID=S12345",
            "submitted_by": "Martin Swift",
        },
        "comment": "Strong NW wind",
        "entries": [
            {
                "identifier": "OBS12345",
                "species": {
                    "name": "Manx Shearwater",
                    "scientific_name": "Puffinus puffinus"
                },
                "count": 22,
                "comment": "Single flock flying west"
            },
            {
                "identifier": "OBS12346",
                "species": {
                    "name": "Northern Gannet",
                },
                "count": 45,
                "comment": "Flying east",
                "details": [
                    {
                        "identifier": "1",
                        "age": "Adult",
                        "sex": "Sex Unknown",
                        "count": 26
                    },
                    {
                        "identifier": "2",
                        "age": "Immature",
                        "sex": "Sex Unknown",
                        "count": 19
                    }
                ]
            }
        ]
    }


def save_data(directory, filename, data):
    """Encode the data using JSON and write it to a file.

    Args:
        directory (str): the directory where the data will be written. The
            directory will be created if it does not exist.
        filename (str): the name of the file where the data will be written to.
        data (list or dict): the data structure that will be encoded to JSON
            and written to the file.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, filename)
    with open(path, 'wb') as fp:
        json.dump(data, fp)


class LoadTestCase(TestCase):

    """Basic tests for the load_checklists command."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_load_from_settings_directory(self):
        save_data(self.directory, "checklist.json", downloaded_checklist())
        with mock.patch.object(settings,
                               'CHECKLISTS_DOWNLOAD_DIR', self.directory):
            call_command('load_checklists')
        self.assertTrue(Checklist.objects.exists())

    def test_file_deleted(self):
        save_data(self.directory, "checklist.json", downloaded_checklist())
        with mock.patch.object(settings,
                               'CHECKLISTS_DOWNLOAD_DIR', self.directory):
            call_command('load_checklists')
        path = os.path.join(self.directory, "checklist.json")
        self.assertFalse(os.path.exists(path))

    def test_entry_without_identifier(self):
        checklist = downloaded_checklist()
        entry = checklist['entries'][0]
        del entry['identifier']
        save_data(self.directory, "checklist.json", checklist)
        call_command('load_checklists', dir=self.directory)
        filters = Q(species__standard_name=entry['species']['name']) & \
            Q(count=entry['count'])
        self.assertTrue(Entry.objects.filter(filters).exists())

    def test_detail_without_identifier(self):
        checklist = downloaded_checklist()
        entry = checklist['entries'][1]
        detail = entry['details'][0]
        del detail['identifier']
        save_data(self.directory, "checklist.json", checklist)
        call_command('load_checklists', dir=self.directory)
        filters = Q(species__standard_name=entry['species']['name']) & \
            Q(count=entry['count'])
        self.assertTrue(Entry.objects.filter(filters).exists())


class ArgumentsTestCase(TestCase):

    """Basic tests for the arguments passed to the load_checklists command."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_load_from_directory(self):
        save_data(self.directory, "checklist.json", downloaded_checklist())
        call_command('load_checklists', dir=self.directory)
        self.assertTrue(Checklist.objects.exists())

    def test_load_from_subdirectory(self):
        subdir = os.path.join(self.directory, 'nested')
        save_data(subdir, "checklist.json", downloaded_checklist())
        call_command('load_checklists', dir=self.directory)
        self.assertTrue(Checklist.objects.exists())



@mock.patch.object(settings, 'CHECKLISTS_REPORT_RECIPIENTS',
                   'admins@example.com')
class FilterChecklistTestCase(TestCase):

    """Tests for filtering the checklists to be loaded."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        save_data(self.directory, "checklist.json", downloaded_checklist())

    def tearDown(self):
        shutil.rmtree(self.directory)
        mail.outbox = []

    def test_filter_on_value(self):
        Filter.objects.create(key='location.name', value='Cape Clear')
        call_command('load_checklists', dir=self.directory)
        self.assertFalse(Checklist.objects.exists())

    def test_filter_is_case_insensitive(self):
        Filter.objects.create(key='location.name', value='cape clear')
        call_command('load_checklists', dir=self.directory)
        self.assertFalse(Checklist.objects.exists())

    def test_status_report_contains_filtered_checklist(self):
        Filter.objects.create(key='location.name', value='Cape Clear')
        call_command('load_checklists', dir=self.directory)
        sections = mail.outbox[0].body.split('+-')
        self.assertTrue('Checklists filtered' in sections[1])
        self.assertTrue('Cape Clear' in sections[2])

    def test_status_report_contains_filter_key(self):
        Filter.objects.create(key='location.name', value='Cape Clear')
        call_command('load_checklists', dir=self.directory)
        sections = mail.outbox[0].body.split('+-')
        self.assertTrue('Matching Filter: %s' % 'location.name' in sections[2])

    def test_status_report_contains_filter_value(self):
        Filter.objects.create(key='location.name', value='Cape Clear')
        call_command('load_checklists', dir=self.directory)
        sections = mail.outbox[0].body.split('+-')
        self.assertTrue('Matching Value: "%s"' % 'Cape Clear' in sections[2])


class CreateChecklistTestCase(TestCase):

    """Tests for creating checklists with the load_checklists command."""

    directory = tempfile.mkdtemp()
    data = downloaded_checklist()

    @classmethod
    def setUpClass(cls):
        save_data(cls.directory, "checklist.json", cls.data)
        call_command('load_checklists', dir=cls.directory)

    @classmethod
    def tearDownClass(cls):
        Checklist.objects.all().delete()
        Location.objects.all().delete()
        Observer.objects.all().delete()
        shutil.rmtree(cls.directory)

    def test_checklist_added(self):
        self.assertEqual(1, Checklist.objects.all().count())

    def test_checklist_date(self):
        checklist = Checklist.objects.all()[0]
        self.assertEqual(self.data['date'],
                         checklist.date.strftime("%Y-%m-%d"))

    def test_checklist_comment(self):
        checklist = Checklist.objects.all()[0]
        self.assertEqual(self.data['comment'], checklist.comment)

    def test_location_added(self):
        self.assertEqual(1, Location.objects.all().count())

    def test_location_set(self):
        checklist = Checklist.objects.all()[0]
        location = Location.objects.all()[0]
        self.assertEqual(location.id, checklist.location.id)

    def test_location_name(self):
        expected = self.data['location']['name']
        checklist = Checklist.objects.all()[0]
        self.assertEqual(expected, checklist.location.name)

    def test_location_county(self):
        expected = self.data['location']['county']
        checklist = Checklist.objects.all()[0]
        self.assertEqual(expected, checklist.location.county)

    def test_location_region(self):
        expected = self.data['location']['region']
        checklist = Checklist.objects.all()[0]
        self.assertEqual(expected, checklist.location.region)

    def test_location_country(self):
        expected = self.data['location']['country']
        checklist = Checklist.objects.all()[0]
        self.assertEqual(expected, checklist.location.country)

    def test_location_lat(self):
        expected = str(self.data['location']['lat'])
        checklist = Checklist.objects.all()[0]
        self.assertEqual(expected, checklist.location.lat)

    def test_location_long(self):
        expected = str(self.data['location']['lon'])
        checklist = Checklist.objects.all()[0]
        self.assertEqual(expected, checklist.location.lon)

    def test_method_added(self):
        self.assertEqual(1, Method.objects.all().count())

    def test_method_protocol(self):
        protocol = Protocol.objects.all()[0]
        checklist = Checklist.objects.all()[0]
        self.assertEqual(protocol.id, checklist.method.protocol.id)

    def test_method_time(self):
        checklist = Checklist.objects.all()[0]
        self.assertEqual(self.data['protocol']['time'],
                         checklist.method.time.strftime("%H:%M"))

    def test_method_duration_hours(self):
        obj = Checklist.objects.all()[0]
        self.assertEqual(self.data['protocol']['duration_hours'],
                         obj.method.duration_hours)

    def test_method_duration_minutes(self):
        obj = Checklist.objects.all()[0]
        self.assertEqual(self.data['protocol']['duration_minutes'],
                         obj.method.duration_minutes)

    def test_method_distance(self):
        obj = Checklist.objects.all()[0]
        self.assertEqual(self.data['protocol']['distance'],
                         obj.method.distance)

    def test_method_area(self):
        obj = Checklist.objects.all()[0]
        self.assertEqual(self.data['protocol']['area'],
                         obj.method.area)

    def test_checklist_reporter(self):
        checklist = Checklist.objects.all()[0]
        self.assertEqual(self.data['source']['submitted_by'],
                         checklist.reporter.name)

    def test_observers_added(self):
        self.assertEqual(3, Observer.objects.all().count())

    def test_checklist_observers_count(self):
        checklist = Checklist.objects.all()[0]
        self.assertEqual(5, checklist.observers_count)

    def test_observers_names(self):
        expected = sorted(self.data['observers']['names'])
        observers = Checklist.objects.all()[0].observers
        actual = observers.values_list('name', flat=True).order_by('name')
        self.assertEqual(expected, list(actual))

    def test_checklist_source(self):
        checklist = Checklist.objects.all()[0]
        self.assertEqual(self.data['source']['name'], checklist.source)

    def test_checklist_url(self):
        checklist = Checklist.objects.all()[0]
        self.assertEqual(self.data['source']['url'], checklist.url)

    def test_entries_added(self):
        self.assertEqual(2, Entry.objects.all().count())

    def test_entry_species(self):
        expected = Species.objects.values_list('id', flat=True)
        entries = Checklist.objects.all()[0].entries
        actual = entries.values_list('species__id', flat=True)
        self.assertEqual(list(expected), list(actual))

    def test_entry_count(self):
        expected = Entry.objects.values_list('count', flat=True)
        entries = Checklist.objects.all()[0].entries
        actual = entries.values_list('count', flat=True)
        self.assertEqual(list(expected), list(actual))

    def test_details_age(self):
        expected = ['AD', 'IMM']
        actual = Detail.objects.values_list('age__slug', flat=True)
        self.assertEqual(expected, list(actual))

    def test_details_sex(self):
        expected = ['X', 'X']
        actual = Detail.objects.values_list('sex__slug', flat=True)
        self.assertEqual(expected, list(actual))

    def test_details_count(self):
        expected = [26, 19]
        actual = Detail.objects.values_list('count', flat=True)
        self.assertEqual(expected, list(actual))


class StatusReportTestCase(SimpleTestCase):

    """Tests on the status report generated by the load_checklists command."""

    @classmethod
    def setUpClass(cls):
        mail.outbox = []
        cls.directory = tempfile.mkdtemp()
        save_data(cls.directory, "checklist.json", downloaded_checklist())
        with mock.patch.object(
                settings, 'CHECKLISTS_REPORT_RECIPIENTS', 'admins@example.com'):
            cls.recipients = getattr(settings, 'CHECKLISTS_REPORT_RECIPIENTS')
            call_command('load_checklists', dir=cls.directory)

    @classmethod
    def tearDownClass(cls):
        Checklist.objects.all().delete()
        shutil.rmtree(cls.directory)
        mail.outbox = []

    def test_status_report_sent(self):
        self.assertEquals(len(mail.outbox), 1)

    def test_status_report_subject(self):
        email = mail.outbox[0]
        self.assertEquals(email.subject, "Load Checklists Status Report")

    def test_status_report_from_address(self):
        email = mail.outbox[0]
        expected = getattr(settings, 'SERVER_EMAIL')
        self.assertEquals(expected, email.from_email)

    def test_status_report_recipients(self):
        email = mail.outbox[0]
        expected = [address for address in self.recipients.split(',')]
        self.assertEquals(list(expected), email.to)

    def test_status_report_date(self):
        contents = mail.outbox[0].body
        expected = "Date: %s" % timezone.now().date().strftime("%d-%m-%Y")
        self.assertTrue(expected in contents)

    def test_status_report_time(self):
        contents = mail.outbox[0].body
        expected = "Time: %s" % timezone.now().strftime("%H:%M")
        self.assertTrue(expected in contents)

    def test_status_report_loaded_section(self):
        contents = mail.outbox[0].body
        self.assertTrue("Checklists loaded" in contents)

    def test_status_report_contains_checklist(self):
        contents = mail.outbox[0].body
        self.assertTrue('Cape Clear' in contents)

    def test_no_checklists_were_filtered(self):
        contents = mail.outbox[0].body
        self.assertFalse('Checklists filtered' in contents)

    def test_no_errors_in_status_report(self):
        contents = mail.outbox[0].body
        self.assertFalse('Errors' in contents)


@mock.patch.object(settings, 'CHECKLISTS_REPORT_RECIPIENTS',
                   'admins@example.com')
class UpdateChecklistTestCase(TestCase):

    """Tests to verify all changes to checklists are tracked."""

    def shortDescription(self):
        return None

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.data = downloaded_checklist()
        save_data(self.directory, "checklist.json", self.data)
        call_command('load_checklists', dir=self.directory)
        mail.outbox = []

    def tearDown(self):
        shutil.rmtree(self.directory)
        mail.outbox = []

    def test_update_checklist_without_identifier(self):
        """Verify checklists can be updated if the identifier is not available.

        If there is no identifier for a checklist then the location name,
        date, the reporter name and optionally the time are used to check
        whether a checklist already exists in the database.
        """
        data = downloaded_checklist()
        del data['identifier']
        data['location']['lon'] = data['location']['lon'] - 0.1
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        checklist = Checklist.objects.all()[0]
        expected = str(data['location']['lon'])
        self.assertEqual(expected, checklist.location.lon)

    def test_location_updated(self):
        data = downloaded_checklist()
        data['location']['lon'] = data['location']['lon'] - 0.1
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        checklist = Checklist.objects.all()[0]
        expected = str(data['location']['lon'])
        self.assertEqual(expected, checklist.location.lon)

    def test_location_replaced(self):
        data = downloaded_checklist()
        data['location'] = {
            "name": "Flamborough Head",
            "county": "Yorkshire",
            "country": "England",
            "lat": 54.115989,
            "lon": 0.08305
        }
        location = Location.objects.create(**data['location'])
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        checklist = Checklist.objects.all()[0]
        self.assertEqual(location, checklist.location)

    def test_method_updated(self):
        data = downloaded_checklist()
        data['protocol']['name'] = 'Travelling'
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        checklist = Checklist.objects.all()[0]
        expected = Protocol.objects.get(slug='TRV')
        self.assertEqual(expected, checklist.method.protocol)

    def test_method_deleted(self):
        data = downloaded_checklist()
        del data['protocol']
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        checklist = Checklist.objects.all()[0]
        self.assertFalse(hasattr(checklist, 'method'))
        self.assertEqual(0, Method.objects.count())

    def test_activity_updated(self):
        data = downloaded_checklist()
        data['activity'] = 'Birding'
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        checklist = Checklist.objects.all()[0]
        expected = Activity.objects.get(slug='BIR')
        self.assertEqual(expected, checklist.activity)

    def test_observers_updated(self):
        data = downloaded_checklist()
        data['observers']['names'].append('Dave Diver')
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        expected = sorted(data['observers']['names'])
        observers = Checklist.objects.all()[0].observers
        actual = observers.values_list('name', flat=True).order_by('name')
        self.assertEqual(expected, list(actual))

    def test_entry_updated(self):
        data = downloaded_checklist()
        data['entries'][0]['count'] = data['entries'][0]['count'] + 10
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        entry = Checklist.objects.all()[0].entries.all()[0]
        self.assertEqual(data['entries'][0]['count'], entry.count)

    def test_entry_species_replaced(self):
        expected = Species.objects.get(common_name_en='Gannet')
        entry = Checklist.objects.all()[0].entries.all()[0]
        self.assertNotEquals(expected, entry.species)

        data = downloaded_checklist()
        data['entries'][0]['species'] = {
            'name': expected.standard_name
        }
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        entry = Checklist.objects.all()[0].entries.all()[0]
        self.assertEqual(expected, entry.species)

    def test_more_entries_are_reported(self):
        data = downloaded_checklist()
        data['entries'].append({
            "identifier": "OBS12347",
            "species": {
                "name": "Manx Shearwater",
                "scientific_name": "Puffinus puffinus"
            },
            "count": 2,
        })
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        self.assertTrue("The number of entries changed from 2 to 3"
                        in mail.outbox[0].body)

    def test_fewer_entries_are_reported(self):
        data = downloaded_checklist()
        data['entries'].pop()
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        self.assertTrue("The number of entries changed from 2 to 1"
                        in mail.outbox[0].body)

    def test_new_entry_is_reported(self):
        data = downloaded_checklist()
        data['entries'].append({
            "identifier": "OBS12347",
            "species": {
                "name": "Manx Shearwater",
                "scientific_name": "Puffinus puffinus"
            },
            "count": 2,
        })
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        self.assertTrue("A new entry, Manx Shearwater (2), was added"
                        in mail.outbox[0].body)

    def test_species_changes_are_reported(self):
        data = downloaded_checklist()
        data['entries'][0] = {
            "identifier": "OBS12345",
            "species": {
                "name": "Northern Gannet",
            },
            "count": 22,
        }
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        self.assertTrue("Species for entry OBS12345 changed from Manx "
                        "Shearwater to Northern Gannet" in mail.outbox[0].body)

    def test_changes_in_counts_are_reported(self):
        data = downloaded_checklist()
        data['entries'][0] = {
            "identifier": "OBS12345",
            "species": {
                "name": "Manx Shearwater",
            },
            "count": 32,
        }
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        self.assertTrue("Count for entry OBS12345 changed from 22 to 32"
                        in mail.outbox[0].body)


class AliasTestCase(TestCase):

    """Tests for verifying that the alias tables are used."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_species_alias_is_used(self):

        alias = Map.objects.create(
            name='Solen Goose',
            content_type=ContentType.objects.get_for_model(Species),
            object_id=Species.objects.get(standard_name='Northern Gannet').id
        )

        data = downloaded_checklist()
        data['entries'][1]['species']['name'] = "Solen Goose"
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)
        entry = Entry.objects.filter(species=alias.content_object)
        self.assertTrue(entry.exists())


@mock.patch.object(settings, 'CHECKLISTS_REPORT_RECIPIENTS',
                   'admins@example.com')
class ErrorOnLoadTestCase(TestCase):

    """Tests for errors that occur when loading checklists."""

    def shortDescription(self):
        return None

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.directory)
        mail.outbox = []

    def test_objects_not_added(self):
        """Verify no objects are added to the database if an error occurs.

        A Location is the first object to be created when loading a checklist
        So this test verifies all database changes are rolled back if an error
        occurs.
        """
        data = {
            "location": {
                "identifier": "L12345",
                "name": "Cape Clear",
                "county": "Cork",
                "region": "South-West",
                "country": "Eire",
                "lat": 51.433333,
                "lon": -9.5
            }
        }
        save_data(self.directory, "checklist.json", data)
        call_command('load_checklists', dir=self.directory)

        self.assertFalse(Location.objects.exists())

    def test_missing_species(self):
        """Verify an error is raised if a species is not in the database."""
        checklist = downloaded_checklist()
        checklist['entries'][0]['species']['name'] = 'unknown'
        checklist['entries'][0]['species']['scientific_name'] = 'unknown'
        save_data(self.directory, "checklist.json", checklist)

        call_command('load_checklists', dir=self.directory)

        self.assertTrue("There is no entry in Species"
                        in mail.outbox[0].body)

    def test_status_report_contains_error(self):

        data = {
            "location": {
                "identifier": "L12345",
                "name": "Cape Clear",
                "county": "Cork",
                "region": "South-West",
                "country": "Eire",
                "lat": 51.433333,
                "lon": -9.5
            }
        }
        save_data(self.directory, "checklist.json", data)

        with mock.patch.object(
                settings, 'CHECKLISTS_REPORT_RECIPIENTS', 'admins@example.com'):
            call_command('load_checklists', dir=self.directory)

        self.assertTrue("Errors" in mail.outbox[0].body)

    def test_status_report_error_contains_filename(self):
        data = {
            "location": {
                "identifier": "L12345",
                "name": "Cape Clear",
                "county": "Cork",
                "region": "South-West",
                "country": "Eire",
                "lat": 51.433333,
                "lon": -9.5
            }
        }
        save_data(self.directory, "checklist.json", data)

        with mock.patch.object(
                settings, 'CHECKLISTS_REPORT_RECIPIENTS', 'admins@example.com'):
            call_command('load_checklists', dir=self.directory)

        sections = mail.outbox[0].body.split('+-')
        path = os.path.join(self.directory, "checklist.json")
        self.assertTrue("File: %s" % path in sections[-1])

    def test_status_report_error_contains_traceback(self):
        data = {
            "location": {
                "identifier": "L12345",
                "name": "Cape Clear",
                "county": "Cork",
                "region": "South-West",
                "country": "Eire",
                "lat": 51.433333,
                "lon": -9.5
            }
        }
        save_data(self.directory, "checklist.json", data)

        call_command('load_checklists', dir=self.directory)

        sections = mail.outbox[0].body.split('+-')
        self.assertTrue("Traceback (most recent call last)" in sections[-1])

    def test_file_not_deleted(self):

        data = {
            "location": {
                "identifier": "L12345",
                "name": "Cape Clear",
                "county": "Cork",
                "region": "South-West",
                "country": "Eire",
                "lat": 51.433333,
                "lon": -9.5
            }
        }
        save_data(self.directory, "checklist.json", data)

        with mock.patch.object(
                settings, 'CHECKLISTS_REPORT_RECIPIENTS', 'admins@example.com'):
            call_command('load_checklists', dir=self.directory)

        path = os.path.join(self.directory, "checklist.json")
        self.assertTrue(os.path.exists(path))
