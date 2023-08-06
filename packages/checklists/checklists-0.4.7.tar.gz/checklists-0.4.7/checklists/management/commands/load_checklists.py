import functools
import json
import logging
import os
import traceback
import sys

from optparse import make_option

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from checklists.models import Map, Filter, Location, Species, \
    Checklist, Activity, Protocol, Method, Entry, Detail, Age, Sex, Observer, \
    set_current_user, clear_current_user


logger = logging.getLogger(__name__)


def memoize(obj):
    """Decorator. Caches a function's return value each time it is called."""
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = unicode(args) + unicode(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


def find_in_map(model, name):
    """Get the entry in Map for a given model class.

    Args:
        model (Model): the Model class.
        name (unicode): the name used to look up the instance of the model.

    Returns:
        object: the instance that matches the name and Model.

    Raises:
        Map.DoesNotExist: if there is no entry matching the name and model.
        Map.MultipleObjectsReturned: if there are more than one entry in the
        map matching the name and model.
    """
    try:
        content_type = ContentType.objects.get_for_model(model)
        obj = Map.objects.get(
            content_type=content_type, name=name).content_object
    except Map.DoesNotExist:
        message = "There is no entry in Map for the %s with the name %s" % (
            model, name)
        info = sys.exc_info()
        raise info[0], message, info[2]
    except Map.MultipleObjectsReturned:
        message = "There is more than one entry in Map for the %s with the" \
                  " name '%s'" % (model, name)
        info = sys.exc_info()
        raise info[0], message, info[2]

    return obj


@memoize
def find_protocol(name):
    """Get the Protocol with the given name.

    Args:
        name (unicode): the name used to search the Protocol records in the
            Map table.

    Returns:
        Protocol: the Protocol that maps to the name, if one exists.
    """
    if not name:
        raise ValueError("The name used to find the protocol was not set")
    return find_in_map(Protocol, name)


@memoize
def find_activity(name):
    """Get the Activity with the given name.

    Args:
        name (unicode): the name used to search the Activity records in the
            Map table.

    Returns:
        Activity: the Activity that maps to the name, if one exists.
    """
    if not name:
        raise ValueError("The name used to find the activity was not set")
    return find_in_map(Activity, name)


@memoize
def find_age(name):
    """Get the Age with the given name.

    Args:
        name (unicode): the name used to search the Age records in the
            Map table.

    Returns:
        Age: the Age that maps to the name, if one exists.
    """
    if not name:
        raise ValueError("The name used to find the age was not set")
    return find_in_map(Age, name)


@memoize
def find_sex(name):
    """Get the Sex with the given name.

    Args:
        name (unicode): the name used to search the Sex records in the
            Map table.

    Returns:
        Sex: the Sex that maps to the name, if one exists.
    """
    if not name:
        raise ValueError("The name used to find the sex was not set")
    return find_in_map(Sex, name)


@memoize
def find_map_species(names):
    """Get the Species that matches any of the given names.

    Args:
        names (list(unicode)): a list of species names.

    Returns:
        Species: the first entry in the Map table with a name that matches
            one of the names given. Returns None if no match exists.
    """
    filterspec = Q()
    for name in names:
        filterspec |= Q(name=name)
    filterspec &= Q(content_type=ContentType.objects.get_for_model(Species))
    mappings = Map.objects.filter(filterspec)
    if mappings:
        species = mappings[0].content_object
    else:
        species = None
    return species


@memoize
def find_species(**kwargs):
    """Get the Species that matches all of the given names.

    When searching for the Species first any entry in Map matching one of the
    names is returned. However when searching for the Species only one record
    must match any or all of the names given. This is designed to catch
    duplicate entries as new species are added or the name of existing ones
    change.

    kwargs (dict): any of following:
        standard_name (unicode): the formal (standard) English language
            name as used by the International Ornithological Union.
        common_name_xx (unicode): the localized common name, for example,
            common_name_de, where last two letter are the ISO 3166,
            two-letter country code.
        scientific_name (unicode): the scientific (latin) name.

    Returns:
        Species: the Species object with a name that matches all of the
            arguments given.
    """
    species = find_map_species(kwargs.values())
    if not species:
        filterspec = Q()
        for key, value in kwargs.items():
            filterspec |= Q(**{key: value})
        try:
            species = Species.objects.get(filterspec)
        except Species.DoesNotExist:
            message = "There is no entry in Species for %s" % unicode(kwargs)
            info = sys.exc_info()
            raise info[0], message, info[2]
        except Species.MultipleObjectsReturned:
            message = "There are multiple entries in Species for %s" % \
                      unicode(kwargs)
            info = sys.exc_info()
            raise info[0], message, info[2]
    return species


@memoize
def find_map_location(name):
    """Get the Location that matches the name given.

    Args:
        name (unicode): the name of the location

    Returns:
        Location: the Location that maps to the name, if one exists.
    """
    mapping = Map.objects.filter(
        content_type=ContentType.objects.get_for_model(Location),
        name=name,
    )
    if mapping:
        location = mapping[0].content_object
    else:
        location = None
    return location


def observers_for_names(names):
    """Get the list of Observers for the given names.

    Args:
        names (list(unicode)): the list of names.

    Returns:
        list(Observer): the list of Observers for the given names. If there is
        no Observer for a name then one will be created.
    """
    observers = []
    for name in names:
        observer, created = observer_for_name(name)
        observers.append(observer)
    return observers


def observer_for_name(name):
    """Get the list of Observer for the given names.

    Args:
        name (unicode): The name of the Observer.

    Returns:
        Observer: the Observer for the given name. If one does not exist then
        it will be created.
    """
    if not name:
        raise ValueError()
    return Observer.objects.get_or_create(name=name)


def find_files(path, extension):
    """Recursively find all the files in a directory with a given extension.

    Args:
        path (str): the path to the directory.
        extension (str): the extension of the files to search for.

    Returns:
        list(str): a list of the files found, with the full (absolute) path.
    """
    found = []
    for path, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(extension):
                found.append(os.path.join(path, filename))
    return found


def load_json(path):
    """Load JSON encoded data from a file.

    Args:
        path (str): the path to the file to be loaded.

    Returns:
        object: the decoded data.
    """
    with open(path, 'rb') as fp:
        contents = json.load(fp)
    return contents


def load_filters():
    """Load the set of filters from the database.

    Returns:
        list(tuple): a list of tuples containing the path to the field to
           be checked and a list of values that the extracted value is
           compared against.
     """
    filters = {}
    for obj in Filter.objects.all():
        filters.setdefault(obj.key, []).append(obj.value.lower())
    return [item for item in filters.items()]


def matches_filter(checklist, filters):
    """Checks whether the checklist data matches an filter.

    Args:
        checklist (dict): the checklist data to be loaded into the database.
        filters (list): a list of tuples containing the path to the field
            in the checklist data using dot notation and the array of values
            to compare the field value against.

    Returns:
        tuple or None: if the value extracted from the checklist matches one
            of the filter values then a tuple containing the path and the
            matching value are returned. If the field value did not match any
            of the values then None is returned.

    The dot notation is used to traverse the checklist dict. For example the
    path "location.name" gets the dict containing the location data using the
    key 'location', which is then in turn used to extract the value using
    the key, 'name'.
    """
    for key, values in filters:
        value = checklist
        for item in key.split('.'):
            value = value[item]
        if value.lower() in values:
            return key, value
    return None


def update_or_create(model, params):
    """Create or update an existing model object.

    The params argument is passed directly to the QuerySet get_or_create()
    method. The keys are used to check whether a matching object existing in
    the database. THe key 'defaults' contains a dict with values that are
    used to update the object once it is created or fetched.

    Args:
        model (Class): a Django model class object.
        params (dict): the parameters passed to the QuerySet's
            get_or_create() method.

    Returns:
        tuple(Model, bool): a tuple containing the Model object and a boolean
            flag indication whether the object was created (True) or updated
            (False).
    """
    obj, created = model.objects.get_or_create(**params)
    if not created:
        for key, value in params['defaults'].items():
            setattr(obj, key, value)
        obj.save()
    return obj, created


class Command(BaseCommand):
    """Load a set of checklists into the database.

    Checklists are loaded from a directory, including all subdirectories.
    The directory is specified by using the --dir option. If that is not
    specified then the value from the CHECKLISTS_DOWNLOAD_DIR setting is used.

    Checklists must be in JSON format, matching the structure defined in the
    Checklisting project, https://www.github.com/StuartMacKay/checklisting/

    The command generates a status report which lists the checklists loaded,
    checklists that matched a filter and were not loaded and checklists that
    triggered an error and were not loaded.  The error section contains the
    name of the file and a full stack trace describing where the error
    occurred. The report is sent via email to all the addresses listed in the
    setting CHECKLISTS_DOWNLOAD_REPORT_RECIPIENTS. The from address for the
    email is defined using the main Django setting, SERVER_EMAIL.

    The command is designed to be run repeatedly (after a given interval) so
    the database can be updated with new checklists as they become available
    from the third-party sources. If the checklist has already been loaded
    then it will be updated, tracking any changes made at the source. The
    status report will contain a short description of any changes made such
    as entries being added or a count changed. When a checklist has been
    loaded successfully the file is deleted so the directory does not fill
    up with files.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--dir',
            action='store',
            type='string',
            dest='dir',
            default=None,
            help='Load checklists from a directory'
        ),
    )

    template = "management/commands/load_checklists_status.html"

    def handle(self, *args, **options):
        filtered = []
        passed = []
        failed = []

        directory = options['dir'] or settings.CHECKLISTS_DOWNLOAD_DIR
        paths = find_files(directory, 'json')

        filters = load_filters()
        set_current_user('load_checklists')

        for path in paths:
            try:
                values = load_json(path)
                match = matches_filter(values, filters)
                if match:
                    filtered.append((path, values, match))
                else:
                    messages = []
                    self.denormalize_values(values)
                    self.add_or_update_checklist(values, messages)
                    passed.append((path, values, messages))
                    os.remove(path)
            except:
                kind, value, trace = sys.exc_info()
                error = traceback.format_exception(kind, value, trace)
                failed.append((path, mark_safe(''.join(error))))

        report = render_to_string(self.template, {
            'filtered': filtered,
            'loaded': passed,
            'errors': failed,
        })

        clear_current_user()

        if settings.DEBUG:
            filename = os.path.join(directory, 'load_checklists_report.txt')
            with open(filename, 'wb') as fp:
                fp.write(report.encode('utf-8'))

        recipients = getattr(settings, 'CHECKLISTS_REPORT_RECIPIENTS', '')

        if recipients:
            sender = settings.SERVER_EMAIL
            addresses = [addr.strip() for addr in recipients.split(',')]
            subject = "Load Checklists Status Report"
            send_mail(subject, report, sender, addresses)

    def denormalize_values(self, values):
        language = settings.LANGUAGE_CODE[:2]
        if 'meta' in values and 'language' in values['meta']:
            translations = [language[0] for language in settings.LANGUAGES]
            if values['meta']['language'] in translations:
                language = values['meta']['language']

        values['language'] = language
        for entry in values['entries']:
            entry['language'] = language
            entry['species']['language'] = language

    def add_or_update_checklist(self, values, messages):
        location = find_map_location(values['location']['name'])
        if not location:
            location, created = self.add_or_update_location(values['location'])
            if created:
                messages.append("Added location: %s" % location.name)

        reporter = observers_for_names([values['source']['submitted_by']])[0]
        observers = observers_for_names(values['observers']['names'])

        if reporter not in observers:
            observers.append(reporter)

        count = values['observers'].get('count', None) or len(observers)

        params = {
            'source': values['source']['name'],
            'defaults': {
                'activity': find_activity(values.get('activity', None)),
                'url': values['source']['url'],
                'observers_count': count,
            }
        }

        if 'identifier' in values:
            params['identifier'] = values['identifier']
            params['defaults']['date'] = values['date']
            params['defaults']['location'] = location
            params['defaults']['reporter'] = reporter
        else:
            params['date'] = values['date']
            params['location'] = location
            params['reporter'] = reporter

            if 'time' in values['protocol']:
                params['method__time'] = values['protocol']['time']

        if 'language' in values and 'comment' in values:
            key = "comment_%s" % values['language']
            params['defaults'][key] = values['comment']

        checklist, created = update_or_create(Checklist, params)
        checklist.observers.add(*observers)
        checklist._created = created

        if created:
            messages.append("Added checklist: %s" % checklist)
        else:
            messages.append("Updated checklist: %s" % checklist)

        self.add_or_update_method(checklist, values.get('protocol', None))

        if checklist.entries.exists():
            if checklist.entries.count() != len(values['entries']):
                messages.append(
                    "The number of entries changed from %d to %d" %
                    (checklist.entries.count(), len(values['entries']))
                )

        for values in values['entries']:
            self.add_or_update_entry(checklist, values, messages)

    def add_or_update_location(self, values):
        params = {
            'name': values['name'],
            'defaults': {
                'county': values.get('county', ''),
                'region': values.get('region', ''),
                'island': values.get('island', ''),
                'country': values.get('country', ''),
                'lat': values.get('lat', 0),
                'lon': values.get('lon', 0),
            }
        }
        return update_or_create(Location, params)

    def add_or_update_method(self, checklist, values):
        if values is None:
            if hasattr(checklist, 'method'):
                checklist.method.delete()
            return None, False

        params = {
            'checklist': checklist,
            'defaults': {
                'protocol': find_protocol(values['name']),
                'time': values.get('time', None),
                'distance': values.get('distance', 0),
                'area': values.get('area', 0),
                'duration_hours': values.get('duration_hours', 0),
                'duration_minutes': values.get('duration_minutes', 0),
            }
        }
        return update_or_create(Method, params)

    def add_or_update_entry(self, checklist, values, messages):
        params = {}
        if 'name' in values['species'] and values['species']['name']:
            params['standard_name'] = values['species']['name']
        if 'scientific_name' in values['species'] and \
                values['species']['scientific_name']:
            params['scientific_name'] = values['species']['scientific_name']

        species = find_species(**params)
        identifier = values.get('identifier', '')

        if identifier:
            params = {
                'checklist': checklist,
                'identifier': identifier,
            }
            defaults = {
                'species': species,
                'count': values['count'],
            }
        else:
            if checklist.source == 'ebird':
                # ebird checklists only have one entry per species so we can
                # use the species_id to find the existing entry.
                params = {
                    'checklist': checklist,
                    'species_id': species.id,
                }
                defaults = {
                    'count': values['count'],
                }
            else:
                params = {
                    'checklist': checklist,
                    'species': species,
                    'count': values['count'],
                }
                defaults = {
                }

        if 'language' in values and 'comment' in values:
            key = "comment_%s" % values['language']
            defaults[key] = values['comment']

        # Check to see whether the checklist was edited. This might affect
        # whether an observation was news worthy, etc.

        qs = Entry.objects.filter(**params)

        if qs.exists():
            entry = qs[0]
            if entry.species != species:
                messages.append("Species for entry %s changed from %s to %s" %
                                (identifier, entry.species.standard_name,
                                 species.standard_name))
            if entry.count != values['count']:
                messages.append("Count for entry %s changed from %d to %d" %
                                (identifier, entry.count, values['count']))
        else:
            if not checklist._created:
                messages.append("A new entry, %s (%d), was added" % (
                    species.standard_name, values['count']))

        params['defaults'] = defaults

        entry, created = update_or_create(Entry, params)

        for details in values.get('details', []):
            self.add_or_update_details(entry, details)

        return entry, created

    def add_or_update_details(self, entry, values):
        if 'identifier' in values:
            params = {
                'entry': entry,
                'identifier': values['identifier'],
                'defaults': {
                    'age': find_age(values.get('age', None)),
                    'sex': find_sex(values.get('sex', None)),
                    'count': int(values['count'])
                }
            }
        else:
            params = {
                'entry': entry,
                'age': find_age(values.get('age', None)),
                'sex': find_sex(values.get('sex', None)),
                'count': int(values['count']),
                'defaults': {}
            }
        return update_or_create(Detail, params)
