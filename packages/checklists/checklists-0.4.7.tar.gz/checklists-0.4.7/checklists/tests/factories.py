import datetime
import factory

from factory import fuzzy

from django.conf import settings
from django.utils import timezone

from checklists.models import Location, Checklist, Entry, Rank, \
    Species, SpeciesGroup, Map, Detail, Method, Protocol, Observer, \
    Age, Sex, Activity, EntryTag

ranks = {
    'species': 'Name for Species',
    'subspecies': 'Name for Subspecies',
    'genus': 'Name for Genus',
}

protocols = {
    'stationary': 'Name for Stationary',
    'traveling': 'Name for Travelling',
}

activities = {
    'birding': 'Name for Birding',
    'seawatching': 'Name for Seawatching',
    'night-flight-calls': 'Name for Night Flight Call Count',
}

observers = ['Observer %d' % i for i in range(10)]

ages = {
    'adult': 'Name for Adult',
    'juvenile': 'Name for Juvenile',
    'immature': 'Name for Immature',
    'unknown': 'Name for Unknown',
}

sexes = {
    'male': 'Name for Male',
    'female': 'Name for Female',
    'unknown': 'Name for Unknown'
}


class LanguageFieldMixin:

    @classmethod
    def _i18n_kwargs(cls, fields, **kwargs):
        for field in fields:
            for code, name in settings.LANGUAGES:
                i18n_field = "%s_%s" % (field, code)
                if kwargs[field]:
                    kwargs[i18n_field] = u"%s %s" % (name, kwargs[field])
                else:
                    kwargs[i18n_field] = kwargs[field]
            del kwargs[field]
        return kwargs


class LocationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Location

    name = factory.Sequence(lambda n: 'Location {0}'.format(n))
    county = fuzzy.FuzzyChoice(('County A', 'County B', 'County C'))
    region = fuzzy.FuzzyChoice(('Region A', 'Region B'))
    island = ''
    country = 'Country'
    lat = fuzzy.FuzzyChoice(('44', '45', '46'))
    lon = fuzzy.FuzzyChoice(('-1', '0', '1', '2', '3'))
    include = True


class MapFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Map


class SpeciesGroupFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = SpeciesGroup
    FACTORY_DJANGO_GET_OR_CREATE = ('order', 'family', 'genus',)

    order = factory.Sequence(lambda n: 'Order {0}'.format(n))
    family = factory.Sequence(lambda n: 'Family {0}'.format(n))
    genus = factory.Sequence(lambda n: 'Genus {0}'.format(n))
    name = factory.Sequence(lambda n: 'Name {0}'.format(n))

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('name',), **kwargs)


class RankFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = Rank
    FACTORY_DJANGO_GET_OR_CREATE = ('slug',)

    slug = 'species'
    name = factory.LazyAttribute(lambda obj: ranks[obj.slug])

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('name',), **kwargs)


class SpeciesFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = Species
    FACTORY_DJANGO_GET_OR_CREATE = ('standard_name',)

    include = True
    standard_name = factory.Sequence(
        lambda n: 'Standard Name {0}'.format(n))
    scientific_name = factory.Sequence(
        lambda n: 'Scientific Name {0}'.format(n))
    common_name = factory.Sequence(
        lambda n: 'Common Name {0}'.format(n))
    order = factory.Sequence(int)
    rank = factory.SubFactory(RankFactory)
    group = factory.SubFactory(SpeciesGroupFactory)

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('common_name',), **kwargs)


class ActivityFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = Activity
    FACTORY_DJANGO_GET_OR_CREATE = ('slug',)

    slug = fuzzy.FuzzyChoice(activities.keys())
    name = factory.LazyAttribute(lambda obj: activities[obj.slug])

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('name',), **kwargs)


class ProtocolFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = Protocol
    FACTORY_DJANGO_GET_OR_CREATE = ('slug',)

    slug = fuzzy.FuzzyChoice(protocols.keys())
    name = factory.LazyAttribute(lambda obj: protocols[obj.slug])

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('name',), **kwargs)


class MethodFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Method

    protocol = factory.SubFactory(ProtocolFactory)
    time = timezone.now()
    duration_hours = fuzzy.FuzzyInteger(0, 2)
    duration_minutes = fuzzy.FuzzyInteger(0, 59)
    distance = fuzzy.FuzzyInteger(0, 5000)
    area = 0


class ObserverFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Observer

    name = fuzzy.FuzzyChoice(observers)


class ChecklistFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = Checklist

    include = True
    date = timezone.now().date()
    added_on = timezone.now().date()
    location = factory.SubFactory(LocationFactory)
    activity = factory.SubFactory(ActivityFactory)
    comment = factory.Sequence(lambda n: 'Comment {0}'.format(n))
    method = factory.RelatedFactory(MethodFactory)

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('comment',), **kwargs)

    @factory.post_generation
    def observers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for observer in extracted:
                self.observers.add(ObserverFactory(name=observer))


class EntryTagFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = EntryTag
    FACTORY_DJANGO_GET_OR_CREATE = ('slug',)

    slug = factory.Sequence(lambda n: 'slug {0}'.format(n))
    name = factory.Sequence(lambda n: 'Name {0}'.format(n))

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('name',), **kwargs)


class EntryFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = Entry

    include = True
    checklist = factory.SubFactory(ChecklistFactory)
    species = factory.SubFactory(SpeciesFactory)
    count = fuzzy.FuzzyInteger(0, 100)
    description = factory.Sequence(lambda n: 'Description {0}'.format(n))
    comment = factory.Sequence(lambda n: 'Comment {0}'.format(n))

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('description', 'comment',), **kwargs)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of tags were passed in, use them
            for tag in extracted:
                self.tags.add(EntryTagFactory(slug=tag))


class AgeFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = Age
    FACTORY_DJANGO_GET_OR_CREATE = ('slug',)

    slug = fuzzy.FuzzyChoice(ages.keys())
    name = factory.LazyAttribute(lambda obj: ages[obj.slug])

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('name',), **kwargs)


class SexFactory(LanguageFieldMixin, factory.DjangoModelFactory):
    FACTORY_FOR = Sex
    FACTORY_DJANGO_GET_OR_CREATE = ('slug',)

    slug = fuzzy.FuzzyChoice(sexes.keys())
    name = factory.LazyAttribute(lambda obj: sexes[obj.slug])

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        return cls._i18n_kwargs(('name',), **kwargs)


class DetailFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Detail

    entry = factory.SubFactory(EntryFactory)
    count = fuzzy.FuzzyInteger(0, 50)
    age = factory.SubFactory(AgeFactory)
    sex = factory.SubFactory(SexFactory)
    plumage = None
    direction = None
