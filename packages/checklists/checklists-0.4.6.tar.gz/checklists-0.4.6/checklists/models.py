# -*- coding: utf-8 -*-

"""Checklists are used to record the birds seen on a visit to a given location.

A checklist is created for each visit to a location on a given date and
time by one or more observers. Each checklist has a list of entries which
gives the total number of birds for each species seen. For each entry, the
details of the count, which include the age and sex of the birds seen and
information on the direction the birds were flying, can also be recorded.
If a specific methodology was used to survey the location then the details
are described in a protocol associated with the checklist.

The model is also designed to allow easy importing of checklists from other
databases with alias tables to ensure that differences in location names and
species always map to the same object. Unique identifiers for checklists and
entries allow checklists to be imported multiple times in case the original
records were updated and the database will remain consistent.

"""

from datetime import date

from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core.validators import MinValueValidator
from django.db.models import Model, BooleanField, IntegerField, \
    CharField, TextField, DateField, TimeField, DateTimeField, \
    ForeignKey, OneToOneField, ManyToManyField, PROTECT, SET_NULL, \
    PositiveIntegerField
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from transmeta import TransMeta

from threading import local


_thread_locals = local()


def set_current_user(user):
    _thread_locals.user = user


def get_current_user():
    return getattr(_thread_locals, 'user', '')


def clear_current_user():
    if hasattr(_thread_locals, 'user'):
        del _thread_locals.user


class ChecklistsModel(Model):
    """Base class for the Checklists model."""

    class Meta:
        abstract = True

    created_by = CharField(max_length=50, blank=True)
    created_on = DateTimeField(auto_now_add=True)
    modified_by = CharField(max_length=50, blank=True)
    modified_on = DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, **kwargs):
        """Validate a model object on save."""
        if not (force_insert or force_update):
            self.full_clean()

        self.modified_by = get_current_user()
        if not self.pk:
            self.created_by = self.modified_by

        super(ChecklistsModel, self)\
            .save(force_insert, force_update, **kwargs)


class Filter(ChecklistsModel):

    """Filters for the checklists that will be loaded into the database.

    When loading checklists from an automatic feed it is useful to be able to
    skip checklists that are outside the immediate area of interest (WorldBirds
    typically defines a region as an entire country); from an observer who has
    not given permission for their observations to be used, etc. The checklists
    could be deleted once loaded but that is particularly time-consuming and
    annoying if checklists are repeatedly loaded.

    The filters are applied by loading the records from the table and creating
    an array of tuples (key, set). The key uses a dot notation to specify
    the path to traverse in the checklist (dictionary). The value extracted is
    then compared with the set of values from the filter records. If there is
    a match then the checklist is not loaded.

    """

    class Meta:
        verbose_name = _('filter')
        verbose_name_plural = _('filters')

    key = CharField(max_length=50)
    value = CharField(max_length=100)

    key.verbose_name = _('filter key')
    value.verbose_name = _('filter value')

    key.help_text = _('The path to the checklist field (using dot notation).')
    value.help_text = _('The value to compare with the checklist value.')

    def __unicode__(self):
        return "%s -> %s" % (self.key, self.value)


class Map(ChecklistsModel):

    """Map is a lookup table for mapping names to objects.

    Map is used to lookup any type of object when a checklist is loaded into
    the database. For example, when loading checklists into the database the
    table is used to lookup the Age object that represents the name 'Adult'.

    """

    class Meta:
        verbose_name = _('map')
        verbose_name_plural = _('maps')

    name = CharField(max_length=40)
    content_type = ForeignKey(ContentType, editable=False)
    object_id = PositiveIntegerField(editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    name.verbose_name = _('name')
    content_object.verbose_name = _('content_object')

    name.help_text = _('The name used in lookups.')
    content_object.help_text = _('The object the representing the name.')

    def __unicode__(self):
        return "%s -> %s" % (self.name, self.content_object)


class SpeciesGroup(ChecklistsModel):

    """Group related species together.

    Groups can include closely related Species such as plovers or more
    generally related species such as birds of prey. Typical uses of this
    table is for generating reports for a subset of species or for creating
    a two-level hierarchy of species, e.g. grouping species by genus rather
    than presenting a flat list of species which may be several hundred
    entries in length.

    The order, family and genus fields can be used to present information
    about a species taxonomy however these may be left blank so species can
    be grouped on any basis using the name field.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('species group')
        verbose_name_plural = _('species groups')
        translate = ('name',)

    order = CharField(max_length=30)
    family = CharField(max_length=30, blank=True)
    genus = CharField(max_length=30, blank=True)
    name = CharField(max_length=60)

    order.verbose_name = _('order')
    family.verbose_name = _('family')
    genus.verbose_name = _('genus')
    name.verbose_name = _('name')

    order.help_text = _('The taxonomic order for the group.')
    family.help_text = _('The taxonomic family for the group.')
    genus.help_text = _('The taxonomic genus for the group.')
    name.help_text = _('The translated name of the group.')

    def __unicode__(self):
        return "%s" % (self.name or self.genus)


class Rank(ChecklistsModel):

    """Classify a Species according to its taxonomic rank.

    Assigning a taxonomic rank to a species allows Checklists to contain
    entries where the identification is imprecise. This may include closely
    related species which sometimes can be difficult to separate in the
    field e.g. European Starling (Sturnus vulgaris) and Spotless Starling
    (Sturnus unicolor) or general counts involving a large number or birds
    where it is simply not possible to identify each individual, e.g. Gulls
    sp. (Larus sp.).

    A typical set of slugs for Rank objects would include:
    * sub - subspecies, the exact subspecies can be identified.
    * spe - species
    * gen - genus, where the identification was imprecise.
    * fam - family, where several genera are involved.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('rank')
        verbose_name_plural = _('ranks')
        translate = ('name',)

    slug = CharField(max_length=40, unique=True)
    name = CharField(max_length=40)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifies the taxonomic rank.')
    name.help_text = _('The translated name for the taxonomic rank.')

    def __unicode__(self):
        return "%s" % self.name


class SpeciesStatus(ChecklistsModel):

    """Define the status for a species.

    SpeciesStatus is used to record information about the occurrence of a
    species in a given geographical area. For example, regular autumn migrant,
    scarce in spring, rare, vagrant, etc.
    """

    __metaclass__ = TransMeta

    class Meta:
        db_table = u'checklists_speciesstatus'
        verbose_name = _('species status')
        verbose_name_plural = _('species status')
        translate = ('name',)

    slug = CharField(max_length=50, unique=True)
    name = CharField(max_length=50)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifies the status.')
    name.help_text = _('The translated name for the status.')

    def __unicode__(self):
        return self.name


class Species(ChecklistsModel):

    """Describes each bird species.

    There are two reference names for each species. The stadardized name, for
    example, names defined by the International Ornithological Union) and the
    formal scientific name. The scientific name is definitive but it is often
    easier to work with the standardized name, particularly in conjunction
    with the Map table which can map all the different national or regional
    names for species onto one of the reference names.

    The common name can be used for displaying more familiar names rather than
    using the standardized name or scientific name. Typical examples are
    Ruddy Turnstone (Arenaria interpres) which is more commonly known in the
    United Kingdom as simply Turnstone and Great Skua (Stercorarius Skua)
    which is commonly known by it's Shetland name, Bonxie, in the northern
    parts of the UK. Plural name is intended for the plural of the common name.

    Include (default True) allows certain species to be excluded when
    processing the set of species. Cornell University's eBird distinguishes
    between wild and domestic forms of the sam species, e.g. Greylag Goose
    and Greylag Goose (Domestic type). You could simply add an entry to the
    Map table so there was only one species used but it is preferable to set
    include to False so all records of domestic geese are still recorded but
    are excluded from an annual report for example, would would normally only
    include records of wild birds.

    Name order is used to defined the taxonomic order for the set of species
    and may use any formal or informal order, e.g. IOU or Clements (Cornell
    University).

    Status is used to describe the occurrence of a species in a geographical
    area.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('species')
        verbose_name_plural = _('species')
        translate = ('common_name', 'plural_name')

    include = BooleanField(default=True)
    rank = ForeignKey(Rank, on_delete=SET_NULL, null=True, blank=True)
    group = ForeignKey(SpeciesGroup, on_delete=SET_NULL, null=True, blank=True)
    standard_name = CharField(max_length=40)
    scientific_name = CharField(max_length=40)
    common_name = CharField(max_length=40, blank=True)
    plural_name = CharField(max_length=40, blank=True)
    order = IntegerField(default=0, validators=[MinValueValidator(0)])
    status = ManyToManyField(SpeciesStatus, blank=True, null=True)

    include.verbose_name = _('include')
    rank.verbose_name = _('rank')
    group.verbose_name = _('group')
    standard_name.verbose_name = _('standard name')
    scientific_name.verbose_name = _('scientific name')
    common_name.verbose_name = _('common name')
    plural_name.verbose_name = _('plural name')
    order.verbose_name = _('taxonomic sequence')
    status.verbose_name = _('status')

    include.help_text = _('Include when creating a full list of species.')
    rank.help_text = _('A level in the biological classification hierarchy.')
    group.help_text = _('The taxonomic group that a species belongs to.')
    standard_name.help_text = _('The standardized international name.')
    scientific_name.help_text = _('The scientific (latin) name.')
    common_name.help_text = _('The local name.')
    plural_name.help_text = _('The plural of the local name.')
    order.help_text = _('The order in which Species are displayed.')
    status.help_text = _('Keywords describing the species status')

    def __unicode__(self):
        return "%s" % (self.common_name or self.standard_name)


class Location(ChecklistsModel):

    """Location contains the geographical information for a Checklist.

    For a given location only the name, county and country fields are
    required. The area, district, island and region fields are optional and
    can be completed as required.

    The coordinates for a location maybe either latitude/longitude or a
    grid reference from a national mapping system. The fields store text
    rather than numbers which allows either decimal or degrees, minutes and
    seconds to be stored. The value of this may be limited since most uses of
    the information will be to generate maps through third party systems
    such as OpenStreetMap or Google Maps.

    Include (default False) allows certain locations to be excluded when
    processing the set of locations. This is most useful when importing
    records from databases such as eBird which return all the locations for
    a given region when only a subset might be of interest.

    """

    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    include = BooleanField(default=False)
    name = CharField(max_length=100, db_index=True)
    area = CharField(max_length=50, blank=True)
    county = CharField(max_length=50, blank=True)
    district = CharField(max_length=50, blank=True)
    region = CharField(max_length=50, blank=True)
    island = CharField(max_length=50, blank=True)
    country = CharField(max_length=50)
    lat = CharField(max_length=12, blank=True)
    lon = CharField(max_length=12, blank=True)
    gridref = CharField(max_length=10, blank=True)

    include.verbose_name = _('include')
    name.verbose_name = _('name')
    area.verbose_name = _('area')
    county.verbose_name = _('county')
    district.verbose_name = _('district')
    region.verbose_name = _('region')
    island.verbose_name = _('island')
    country.verbose_name = _('country')
    lat.verbose_name = _('latitude')
    lon.verbose_name = _('longitude')
    gridref.verbose_name = _('grid reference')

    include.help_text = _('Include when creating a full list of locations.')
    name.help_text = _('The name of the location.')
    area.help_text = _('The name of the area (covering several locations).')
    county.help_text = _('The name of the county.')
    district.help_text = _('The name of the district.')
    region.help_text = _('The name of the region.')
    island.help_text = _('The name of the island.')
    country.help_text = _('The name of the country.')
    lat.help_text = _('The latitude of the location.')
    lon.help_text = _('The longitude of the location.')
    gridref.help_text = _('The grid reference of the location.')

    def __unicode__(self):
        return "%s, %s" % (self.name, self.county)


class Activity(ChecklistsModel):

    """Define an activity when the birds were counted.

    There are several standard methodologies for counting birds so that the
    level of effort can be assessed and so the total number of birds likely
    to be present at a given location can be inferred.

    Example of slugs for activities are:
    * SEA - sea-watching where the count is divided into regular intervals.
    * NFC - nocturnal flight calls, birds heard flying overhead at night.
    * BBS - beached bird survey, birds found dead along the high tide line.
    * PEL - pelagic trip to count seabirds offshore

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        translate = ('name',)

    slug = CharField(max_length=40, unique=True)
    name = CharField(max_length=40)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifies the activity.')
    name.help_text = _('The translated name for the activity.')

    def __unicode__(self):
        return self.name


class Checklist(ChecklistsModel):

    """Checklist contains the list of birds when visiting a location.

    Added on is used to record the date a checklist was added to the database.
    This is particularly useful when reporting updates to the database since
    Checklists for a given date may be submitted over several days.

    Multiple checklists may be submitted for a given date, time and location
    from different observers. This is likely when information is aggregated
    from different databases. The source field can be used to distinguish
    between different databases however the identifier field and the url
    field (where available) are preferred since they provide a way of
    uniquely identifying each checklist.

    Include (default False) is used to exclude a complete set of observations
    from any report generated from the database. The reasons may be many and
    varied for example the observers have not yet given their permission to
    use the records (if the checklist was imported from a database with a
    public API  such as eBird) or perhaps the species reported are sufficiently
    unusual that the veracity of the observations are in doubt. A Checklist
    may also be excluded as it is outside the geographical area of interest
    again as it was imported with other checklists covering an entire region.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('checklist')
        verbose_name_plural = _('checklists')
        translate = ('comment',)

    include = BooleanField(default=False)
    complete = BooleanField(default=False)
    added_on = DateField(db_index=True, default=timezone.now().date)
    location = ForeignKey(Location, on_delete=PROTECT)
    date = DateField(db_index=True)
    activity = ForeignKey(Activity, blank=True, null=True)
    reporter = ForeignKey('Observer', blank=True, null=True,
                          related_name='reporter')
    observers = ManyToManyField('Observer', blank=True, null=True)
    observers_count = IntegerField(default=0, blank=True)
    source = CharField(max_length=40, blank=True)
    identifier = CharField(max_length=20, blank=True)
    url = CharField(max_length=255, blank=True)
    comment = TextField(blank=True, default='')

    include.verbose_name = _('include')
    complete.verbose_name = _('complete')
    added_on.verbose_name = _('added on')
    location.verbose_name = _('location')
    date.verbose_name = _('date')
    reporter.verbose_name = _('reporter')
    observers.verbose_name = _('observers')
    observers_count.verbose_name = _('observer count')
    source.verbose_name = _('source')
    identifier.verbose_name = _('identifier')
    url.verbose_name = _('source URL')
    comment.verbose_name = _('comment')

    include.help_text = _('Include when retrieving a set of checklists.')
    complete.help_text = _('Does the checklist contain every species seen.')
    added_on.help_text = _('Date the checklist was added.')
    location.help_text = _('The location where birds were seen.')
    date.help_text = _('Date the checklist was made.')
    reporter.help_text = _('Who submitted the checklist.')
    observers.help_text = _('The list of observers who participated.')
    observers_count.help_text = _('The total number of observers.')
    source.help_text = _('Where was the checklist imported from.')
    identifier.help_text = _('A unique identifier for the checklist.')
    url.help_text = _('URL where the original checklist can be viewed.')
    comment.help_text = _('Any useful information about the observations.')

    def __unicode__(self):
        return "%s, %s" % (
            str(self.date), self.location.name
        )

    def clean(self):
        if not self.observers_count and hasattr(self, 'observers'):
            self.observers_count = self.observers.count()


class Observer(ChecklistsModel):

    """The names of observers submitting records.

    An Observer is not necessarily a User so the relationship to auth.User
    is optional.
    """

    user = OneToOneField(User, null=True, blank=True)
    name = CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Protocol(ChecklistsModel):

    """Define a specific technique used to count birds.

    There are several standard methodologies for counting birds so that the
    level of effort can be assessed and so the total number of birds likely
    to be present at a given location can be inferred.

    A typical set of slugs would include:
    * STA - stationary, all birds were recorded from a fixed location.
    * TRA - travelling, all birds recorded while walking a transect.
    * ARE - area, all birds found in a specific area were counted.
    * CAS - casual, birds were counted without using a specific method.

    Additional types can be used for specific activities:
    * SEA - sea-watching where the count is divided into regular intervals.
    * NFC - nocturnal flight calls, birds heard flying overhead at night.
    * BBS - beached bird survey, birds found dead along the high tide line.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('protocol')
        verbose_name_plural = _('protocols')
        translate = ('name',)

    slug = CharField(max_length=40, unique=True)
    name = CharField(max_length=40)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifies the protocol.')
    name.help_text = _('The translated name for the protocol.')

    def __unicode__(self):
        return self.name


class Method(ChecklistsModel):

    """Describe the methodology used to count the birds on a checklist."""

    class Meta:
        verbose_name = _('method')
        verbose_name_plural = _('methods')

    protocol = ForeignKey(Protocol, on_delete=PROTECT)
    checklist = OneToOneField(Checklist, blank=True, null=True)
    time = TimeField(blank=True, null=True)
    duration_hours = IntegerField(
        default=0, validators=[MinValueValidator(0)])
    duration_minutes = IntegerField(
        default=0, validators=[MinValueValidator(0)])
    distance = IntegerField(default=0, validators=[MinValueValidator(0)])
    area = IntegerField(default=0, validators=[MinValueValidator(0)])

    protocol.verbose_name = _('protocol')
    checklist.verbose_name = _('checklist')
    time.verbose_name = _('time')
    duration_hours.verbose_name = _('duration (hours)')
    duration_minutes.verbose_name = _('duration (minutes)')
    distance.verbose_name = _('distance')
    area.verbose_name = _('area')

    protocol.help_text = _('The protocol used,')
    checklist.help_text = _('The checklist the protocol was used for.')
    time.help_text = _('The time the checklist was started.')
    duration_hours.help_text = _('The number of hours spent counting.')
    duration_minutes.help_text = _('The number of minutes spent counting.')
    distance.help_text = _('The distance covered while travelling.')
    area.help_text = _('The area covered during the count.')

    def __unicode__(self):
        return "%s" % self.protocol


class EntryTag(ChecklistsModel):

    """Tags describing the significance an entry.

    EntryTag is used to record information that describes the significance
    of an entry: whether it is for a rare species, a high count, first spring
    arrival, etc.
    """

    __metaclass__ = TransMeta

    class Meta:
        db_table = u'checklists_entrytag'
        verbose_name = _('entry tag')
        verbose_name_plural = _('entry tag')
        translate = ('name',)

    slug = CharField(max_length=50, unique=True)
    name = CharField(max_length=50)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifies the tag.')
    name.help_text = _('The translated name for the tag.')

    def __unicode__(self):
        return self.name


class Entry(ChecklistsModel):

    """Entry contains the counts for each species in the checklist.

    Include (default True) can be used to exclude specific records, for
    example if the identification is uncertain and should be excluded from
    any reports.

    Identifier is a unique key for the entry and is used when importing
    records from a third-party database. This ensures that if the record
    is changed in the source database that it can be re-imported and the
    correct record will be updated.

    The description field is used to display a human readable version of the
    count. For example if the count was greater than 100 then the count would
    be 100 but the description set to 100+. The description field can also be
    used to show more information about age and sex, e.g, 1, 1st winter male,
    rather than store this in comment where it is harder to extract and
    display.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('entry')
        verbose_name_plural = _('entries')
        translate = ('description', 'comment',)

    include = BooleanField(default=True)
    identifier = CharField(max_length=20, blank=True)
    checklist = ForeignKey(Checklist, related_name='entries')
    species = ForeignKey(Species, related_name='species_entries',
                         on_delete=PROTECT)
    count = IntegerField(default=0, validators=[MinValueValidator(0)])
    description = CharField(max_length=255, blank=True, default='')
    comment = TextField(blank=True, default='')
    tags = ManyToManyField(EntryTag, blank=True, null=True)

    include.verbose_name = _('include')
    identifier.verbose_name = _('identifier')
    checklist.verbose_name = _('checklist')
    species.verbose_name = _('species')
    count.verbose_name = _('count')
    description.verbose_name = _('description')
    comment.verbose_name = _('comment')
    tags.verbose_name = _('tags')

    include.help_text = _('Include when retrieving a set of entries.')
    identifier.help_text = _('A unique identifier for the entry.')
    checklist.help_text = _('The checklist this entry belongs to.')
    species.help_text = _('The identified species .')
    count.help_text = _('The number of birds seen.')
    description.help_text = _('More detailed information about the count.')
    comment.help_text = _('Any useful information about the observation.')
    tags.help_text = _('Keywords describing the significance of an entry')

    def __unicode__(self):
        return "%s (%s)" % (self.species.common_name, self.count)


class Age(ChecklistsModel):

    """Define the age for a bird.

    There are several ways to define the birds of known age based on plumage,
    for example a gull in its first year, seen in December in the northern
    hemisphere can be described as "first calendar year", "first winter",
    "juvenile", "immature" or even using the Euring age code "3". (Strictly
    speaking "juvenile" is not quite correct since it generally refers to the
    first plumage a bird has and which is typically moulted within a few weeks
    of becoming independent). Using a separate table allows the most
    appropriate set of ages to be defined without have to support all possible
    values.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('age')
        verbose_name_plural = _('ages')
        translate = ('name',)

    slug = CharField(max_length=20, unique=True)
    name = CharField(max_length=40)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifies the age.')
    name.help_text = _('The translated name for the age.')

    def __unicode__(self):
        return self.name


class Sex(ChecklistsModel):

    """Define the sex for a bird.

    The set of slugs are probably limited:
    * F - female
    * M - male
    * X - unknown
    however they are defined in a separate table to match the implementation
    for age, plumage, etc.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('sex')
        verbose_name_plural = _('sexes')
        translate = ('name',)

    slug = CharField(max_length=10, unique=True)
    name = CharField(max_length=40)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifying a given sex.')
    name.help_text = _('The translated name for the sex.')

    def __unicode__(self):
        return self.name


class Plumage(ChecklistsModel):

    """Define the plumage for a bird.

    The set of slugs describe the different phases and aberrant plumages
    seen in wild birds:
    * DPH - Dark phase
    * LPH - Light phase
    * BPH - Blue phase
    * MEL - Melanistic
    * LEU - Leucistic
    * ALB - Albino
    * X   - Unknown

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('plumage')
        verbose_name_plural = _('plumages')
        translate = ('name',)

    slug = CharField(max_length=20, unique=True)
    name = CharField(max_length=20)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifying a given plumage.')
    name.help_text = _('The translated name for the plumage.')

    def __unicode__(self):
        return self.name


class Direction(ChecklistsModel):

    """Define the direction a bird was flying.

    The typical set of slugs will be limited to compass directions:
    * N  - North
    * NE - Northeast
    * E  - East
    * SE - Southeast
    * S  - South
    * SW - Southwest
    * W  - West
    * NW - Northwest

    The most common use will be for sea-watches or migration counts. It is
    not worth gather direction information for birds flying generally.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('direction')
        verbose_name_plural = _('directions')
        translate = ('name',)

    slug = CharField(max_length=20, unique=True)
    name = CharField(max_length=20)

    slug.verbose_name = _('slug')
    name.verbose_name = _('name')

    slug.help_text = _('A name that uniquely identifies a given direction.')
    name.help_text = _('The translated name for the direction.')

    def __unicode__(self):
        return self.name


class Detail(ChecklistsModel):
    """Detail is used to record extra information for an Entry.

    Currently Detail is used to record one or more of a given species where
    the age, sex, plumage, direction of flight or coordinates were recorded.
    Each of the fields are optional so make the table as flexible as possible.

    Typical uses would be for sea-watching for example an Entry for a count
    of 254 Gannets (Morus bassanus) might have two Detail records: 226 flying
    north and 28 flying south. Similarly the composition of a flock of 8 birds
    might be recorded with two Detail records: 6 males, 2 females.

    The latitude and longitude are intended to record the exact location a
    bird was seen, which is particularly useful if the location specified
    in the parent checklist covers a large area.

    """

    __metaclass__ = TransMeta

    class Meta:
        verbose_name = _('detail')
        verbose_name_plural = _('details')

    entry = ForeignKey(Entry, related_name='details')
    identifier = CharField(max_length=20, blank=True)
    count = IntegerField()
    age = ForeignKey(Age, on_delete=SET_NULL, blank=True, null=True)
    sex = ForeignKey(Sex, on_delete=SET_NULL, blank=True, null=True)
    plumage = ForeignKey(Plumage, on_delete=SET_NULL, blank=True, null=True)
    direction = ForeignKey(
        Direction, on_delete=SET_NULL, blank=True, null=True)
    time = TimeField(blank=True, null=True)
    duration = IntegerField(default=0, validators=[MinValueValidator(0)])
    lat = CharField(max_length=12, blank=True)
    lon = CharField(max_length=12, blank=True)

    entry.verbose_name = _('entry')
    identifier.verbose_name = _('identifier')
    count.verbose_name = _('count')
    sex.verbose_name = _('sex')
    plumage.verbose_name = _('plumage')
    direction.verbose_name = _('direction')
    time.verbose_name = _('time')
    duration.verbose_name = _('duration')
    lat.verbose_name = _('latitude')
    lon.verbose_name = _('longitude')

    entry.help_text = _('The Entry this record is for.')
    identifier.help_text = _('A unique identifier for the entry.')
    count.help_text = _('The number of birds counted.')
    sex.help_text = _('The sex of the birds')
    plumage.help_text = _('The plumage of the birds')
    direction.help_text = _('The direction they were flying.')
    time.help_text = _('The time the count was made.')
    duration.help_text = _('The number of minutes that the count covers.')
    lat.help_text = _('Latitude of the place the birds were seen.')
    lon.help_text = _('Longitude of the place the birds were seen.')

    def __unicode__(self):
        return "%s (%s)" % (self.entry, self.count)
