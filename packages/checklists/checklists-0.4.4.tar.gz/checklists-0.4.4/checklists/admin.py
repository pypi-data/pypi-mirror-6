# -*- coding: utf-8 -*-

import autocomplete_light

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from django.utils.translation import ugettext_lazy as _

from admin_enhancer.admin import EnhancedModelAdminMixin, EnhancedAdminMixin

from django_tablib.admin import TablibAdmin

import models

from filters import MapFilter
from forms import ChecklistForm, EntryInlineAdminForm, MapForm
from utils import i18n_fieldnames


class ChecklistsModelAdmin(EnhancedModelAdminMixin, TablibAdmin):
    formats = ['csv']

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        if request.user.is_superuser:
            fields = set(self.readonly_fields)
            fields.update(
                ['created_on', 'created_by', 'modified_on', 'modified_by'])
            self.readonly_fields = tuple(fields)
        else:
            self.exclude.extend(
                ['created_on', 'created_by', 'modified_on', 'modified_by'])
        return super(ChecklistsModelAdmin, self)\
            .get_form(request, obj, **kwargs)


class FilterAdmin(ChecklistsModelAdmin):
    list_display = ('key', 'value')
    ordering = ('key',)
    search_fields = ('key', 'value')

admin.site.register(models.Filter, FilterAdmin)


class MapAdmin(ChecklistsModelAdmin):
    list_display = ('name', 'content', 'value')
    ordering = ('content_type', 'name')
    list_filter = (MapFilter,)
    form = MapForm

    def content(self, obj):
        return obj.content_type.name.capitalize()

    def value(self, obj):
        return obj.content_object

admin.site.register(models.Map, MapAdmin)


class SpeciesAdmin(ChecklistsModelAdmin):
    list_display = ('standard_name', ) + i18n_fieldnames('common_name') + (
        'scientific_name', 'order', 'rank', 'group', 'include')
    ordering = ('order',)
    search_fields = ('standard_name',) + i18n_fieldnames('common_name') + (
        'scientific_name',)
    list_filter = ('rank', 'status', 'include')

admin.site.register(models.Species, SpeciesAdmin)


class SpeciesGroupAdmin(ChecklistsModelAdmin):
    list_display = ('genus', 'family', 'order', ) + i18n_fieldnames('name')
    ordering = ('order', 'family', 'genus')
    search_fields = ('order', 'family', 'genus') + i18n_fieldnames('name')

admin.site.register(models.SpeciesGroup, SpeciesGroupAdmin)


class RankAdmin(ChecklistsModelAdmin):
    list_display = ('slug',) + i18n_fieldnames('name')
    ordering = i18n_fieldnames('name')

admin.site.register(models.Rank, RankAdmin)


class LocationAdmin(ChecklistsModelAdmin):
    list_display = ('name', 'county', 'region', 'lat', 'lon', 'include')
    ordering = ('name',)
    search_fields = ('name', 'county')
    list_filter = ('county', 'include')

admin.site.register(models.Location, LocationAdmin)


class ActivityAdmin(ChecklistsModelAdmin):
    list_display = ('slug',) + i18n_fieldnames('name')
    ordering = i18n_fieldnames('name')

admin.site.register(models.Activity, ActivityAdmin)


class ProtocolAdmin(ChecklistsModelAdmin):
    list_display = ('slug',) + i18n_fieldnames('name')
    ordering = i18n_fieldnames('name')

admin.site.register(models.Protocol, ProtocolAdmin)


class MethodAdmin(ChecklistsModelAdmin):
    list_display = ('protocol', 'checklist', 'time', 'duration_hours',
                    'duration_minutes', 'distance', 'area',)
    list_filter = ('protocol', )
    search_fields = ('checklist__location__name',)
    form = autocomplete_light.forms.modelform_factory(models.Method)

admin.site.register(models.Method, MethodAdmin)


class EntryInline(EnhancedAdminMixin, admin.TabularInline):
    model = models.Entry
    fields = ('species', 'count') + \
             i18n_fieldnames('description') + i18n_fieldnames('comment') + \
             ('include', 'status', 'has_details', 'edit_entry')
    ordering = ('species__order',)
    readonly_fields = ('has_details', 'edit_entry')
    form = EntryInlineAdminForm
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(EntryInline, self)\
            .formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in i18n_fieldnames('description'):
            field.widget.attrs['class'] = ''
        return field

    def has_details(self, obj):
        if obj.details.all().exists():
            return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    has_details.allow_tags = True

    def edit_entry(self, obj):
        if obj.id:
            return u'<a target="_blank" href="%s">Edit</a>' % reverse(
                "admin:%s_%s_change" % (obj._meta.app_label,
                                        obj._meta.module_name),
                args=(obj.id,))
        else:
            return ''
    edit_entry.allow_tags = True


class MethodInline(admin.StackedInline):
    model = models.Method
    max_num = 1


class ChecklistAdmin(ChecklistsModelAdmin):
    list_display = ('location', 'reporter', 'added_on', 'date',
                    'show_activity', 'source_link', 'species_count', 'include')
    ordering = ('-date',)
    search_fields = ('location__name', 'location__county', 'reporter')
    list_filter = ('include', 'activity', 'source', 'added_on')
    inlines = [MethodInline, EntryInline]
    actions = ['filter_on_location', 'filter_on_reporter',
               'filter_on_activity']
    form = ChecklistForm

    def filter_on_location(self, request, queryset):
        if not request.user.is_staff:
            raise PermissionDenied

        for obj in queryset:
            models.Filter.objects.get_or_create(
                key='location.name', value=obj.location.name)
    filter_on_location.short_description = _(
        "Do not load checklists from these locations")

    def filter_on_reporter(self, request, queryset):
        if not request.user.is_staff:
            raise PermissionDenied

        for obj in queryset:
            models.Filter.objects.get_or_create(
                key='reporter.name', value=obj.reporter.name)
    filter_on_reporter.short_description = _(
        "Do not load checklists from these reporters")

    def filter_on_activity(self, request, queryset):
        if not request.user.is_staff:
            raise PermissionDenied

        for obj in queryset:
            if obj.activity:
                models.Filter.objects.get_or_create(
                    key='activity.name', value=obj.activity.name)
    filter_on_activity.short_description = _(
        "Do not load checklists matching these activities")

    def show_activity(self, obj):
        return obj.activity if obj.activity else ''
    show_activity.short_description = _('activity')

    def source_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.url, obj.source)
    source_link.allow_tags = True
    source_link.short_description = _('source')

    def species_count(self, obj):
        return obj.entries.all().count()
    species_count.short_description = _('species')

admin.site.register(models.Checklist, ChecklistAdmin)


class ObserverAdmin(ChecklistsModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(models.Observer, ObserverAdmin)


class DetailInline(admin.TabularInline):
    model = models.Detail
    fields = ('count', 'age', 'sex', 'plumage', 'direction', 'time',
              'duration', 'lat', 'lon')


class EntryAdmin(ChecklistsModelAdmin):
    list_display = ('species', 'count', 'date', 'location') + \
                   i18n_fieldnames('description') + \
                   i18n_fieldnames('comment') + \
                   ('has_details', 'include', 'checklist_link')
    search_fields = i18n_fieldnames('species__common_name') + \
                    ('species__scientific_name',)
    ordering = ('-checklist__date',)
    list_filter = ('checklist__added_on', 'tags')
    readonly_fields = ('checklist',)
    inlines = [DetailInline]
    form = autocomplete_light.modelform_factory(models.Entry)

    def date(self, obj):
        return obj.checklist.date
    date.short_description = _('date')

    def location(self, obj):
        return obj.checklist.location
    location.short_description = _('location')

    def has_details(self, obj):
        return 'Y' if obj.details.all().exists() else ''
    has_details.allow_tags = True
    has_details.short_description = _('details')

    def checklist_link(self, obj):
        return '<a href="%s">edit</a>' % (
            reverse(
                'admin:checklists_checklist_change',
                args=(obj.checklist.id,)
            )
        )
    checklist_link.allow_tags = True
    checklist_link.short_description = _('checklist')

admin.site.register(models.Entry, EntryAdmin)


class DetailAdmin(ChecklistsModelAdmin):
    list_display = (
        'show_species', 'count', 'show_age', 'show_sex', 'show_plumage',
        'show_direction', 'checklist_date', 'checklist_location',
        'checklist_link', 'entry_link')
    list_filter = ('entry__checklist__added_on',)
    readonly_fields = ('entry',)

    def show_species(self, obj):
        return unicode(obj.entry.species)
    show_species.short_description = _('species')

    def show_age(self, obj):
        return obj.age if obj.age else ''
    show_age.short_description = _('age')

    def show_sex(self, obj):
        return obj.sex if obj.sex else ''
    show_sex.short_description = _('sex')

    def show_plumage(self, obj):
        return obj.plumage if obj.plumage else ''
    show_plumage.short_description = _('plumage')

    def show_direction(self, obj):
        return obj.direction if obj.direction else ''
    show_direction.short_description = _('direction')

    def checklist_date(self, obj):
        return obj.entry.checklist.date
    checklist_date.short_description = _('date')

    def checklist_location(self, obj):
        return obj.entry.checklist.location.name
    checklist_location.short_description = _('location')

    def checklist_link(self, obj):
        return '<a href="%s">edit</a>' % reverse(
            'admin:checklists_checklist_change', 
            args=(obj.entry.checklist.id,))
    checklist_link.allow_tags = True
    checklist_link.short_description = _('checklist')

    def entry_link(self, obj):
        return '<a href="%s">edit</a>' % reverse(
            'admin:checklists_entry_change',
            args=(obj.entry.id,))
    entry_link.allow_tags = True
    entry_link.short_description = _('entry')

admin.site.register(models.Detail, DetailAdmin)


class AgeAdmin(ChecklistsModelAdmin):
    list_display = ('slug',) + i18n_fieldnames('name')
    ordering = i18n_fieldnames('name')

admin.site.register(models.Age, AgeAdmin)


class SexAdmin(ChecklistsModelAdmin):
    list_display = ('slug',) + i18n_fieldnames('name')
    ordering = i18n_fieldnames('name')

admin.site.register(models.Sex, SexAdmin)


class PlumageAdmin(ChecklistsModelAdmin):
    list_display = ('slug',) + i18n_fieldnames('name')
    ordering = i18n_fieldnames('name')

admin.site.register(models.Plumage, PlumageAdmin)


class DirectionAdmin(ChecklistsModelAdmin):
    list_display = ('slug',) + i18n_fieldnames('name')
    ordering = i18n_fieldnames('name')

admin.site.register(models.Direction, DirectionAdmin)
