# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Checklist.created_by'
        db.add_column('checklists_checklist', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Checklist.created_on'
        db.add_column('checklists_checklist', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Checklist.modified_by'
        db.add_column('checklists_checklist', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Checklist.modified_on'
        db.add_column('checklists_checklist', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Rank.created_by'
        db.add_column('checklists_rank', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Rank.created_on'
        db.add_column('checklists_rank', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Rank.modified_by'
        db.add_column('checklists_rank', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Rank.modified_on'
        db.add_column('checklists_rank', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Sex.created_by'
        db.add_column('checklists_sex', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Sex.created_on'
        db.add_column('checklists_sex', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Sex.modified_by'
        db.add_column('checklists_sex', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Sex.modified_on'
        db.add_column('checklists_sex', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Protocol.created_by'
        db.add_column('checklists_protocol', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Protocol.created_on'
        db.add_column('checklists_protocol', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Protocol.modified_by'
        db.add_column('checklists_protocol', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Protocol.modified_on'
        db.add_column('checklists_protocol', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'SpeciesGroup.created_by'
        db.add_column('checklists_speciesgroup', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'SpeciesGroup.created_on'
        db.add_column('checklists_speciesgroup', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'SpeciesGroup.modified_by'
        db.add_column('checklists_speciesgroup', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'SpeciesGroup.modified_on'
        db.add_column('checklists_speciesgroup', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Direction.created_by'
        db.add_column('checklists_direction', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Direction.created_on'
        db.add_column('checklists_direction', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Direction.modified_by'
        db.add_column('checklists_direction', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Direction.modified_on'
        db.add_column('checklists_direction', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Entry.created_by'
        db.add_column('checklists_entry', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Entry.created_on'
        db.add_column('checklists_entry', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Entry.modified_by'
        db.add_column('checklists_entry', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Entry.modified_on'
        db.add_column('checklists_entry', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Plumage.created_by'
        db.add_column('checklists_plumage', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Plumage.created_on'
        db.add_column('checklists_plumage', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Plumage.modified_by'
        db.add_column('checklists_plumage', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Plumage.modified_on'
        db.add_column('checklists_plumage', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Detail.created_by'
        db.add_column('checklists_detail', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Detail.created_on'
        db.add_column('checklists_detail', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Detail.modified_by'
        db.add_column('checklists_detail', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Detail.modified_on'
        db.add_column('checklists_detail', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'SpeciesStatus.created_by'
        db.add_column(u'checklists_speciesstatus', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'SpeciesStatus.created_on'
        db.add_column(u'checklists_speciesstatus', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'SpeciesStatus.modified_by'
        db.add_column(u'checklists_speciesstatus', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'SpeciesStatus.modified_on'
        db.add_column(u'checklists_speciesstatus', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Species.created_by'
        db.add_column('checklists_species', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Species.created_on'
        db.add_column('checklists_species', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Species.modified_by'
        db.add_column('checklists_species', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Species.modified_on'
        db.add_column('checklists_species', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Map.created_by'
        db.add_column('checklists_map', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Map.created_on'
        db.add_column('checklists_map', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Map.modified_by'
        db.add_column('checklists_map', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Map.modified_on'
        db.add_column('checklists_map', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Location.created_by'
        db.add_column('checklists_location', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Location.created_on'
        db.add_column('checklists_location', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Location.modified_by'
        db.add_column('checklists_location', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Location.modified_on'
        db.add_column('checklists_location', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'EntryTag.created_by'
        db.add_column(u'checklists_entrytag', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'EntryTag.created_on'
        db.add_column(u'checklists_entrytag', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'EntryTag.modified_by'
        db.add_column(u'checklists_entrytag', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'EntryTag.modified_on'
        db.add_column(u'checklists_entrytag', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Method.created_by'
        db.add_column('checklists_method', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Method.created_on'
        db.add_column('checklists_method', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Method.modified_by'
        db.add_column('checklists_method', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Method.modified_on'
        db.add_column('checklists_method', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Filter.created_by'
        db.add_column('checklists_filter', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Filter.created_on'
        db.add_column('checklists_filter', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Filter.modified_by'
        db.add_column('checklists_filter', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Filter.modified_on'
        db.add_column('checklists_filter', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Age.created_by'
        db.add_column('checklists_age', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Age.created_on'
        db.add_column('checklists_age', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Age.modified_by'
        db.add_column('checklists_age', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Age.modified_on'
        db.add_column('checklists_age', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Observer.created_by'
        db.add_column('checklists_observer', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Observer.created_on'
        db.add_column('checklists_observer', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Observer.modified_by'
        db.add_column('checklists_observer', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Observer.modified_on'
        db.add_column('checklists_observer', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Activity.created_by'
        db.add_column('checklists_activity', 'created_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Activity.created_on'
        db.add_column('checklists_activity', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)

        # Adding field 'Activity.modified_by'
        db.add_column('checklists_activity', 'modified_by',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Activity.modified_on'
        db.add_column('checklists_activity', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.min, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Checklist.created_by'
        db.delete_column('checklists_checklist', 'created_by')

        # Deleting field 'Checklist.created_on'
        db.delete_column('checklists_checklist', 'created_on')

        # Deleting field 'Checklist.modified_by'
        db.delete_column('checklists_checklist', 'modified_by')

        # Deleting field 'Checklist.modified_on'
        db.delete_column('checklists_checklist', 'modified_on')

        # Deleting field 'Rank.created_by'
        db.delete_column('checklists_rank', 'created_by')

        # Deleting field 'Rank.created_on'
        db.delete_column('checklists_rank', 'created_on')

        # Deleting field 'Rank.modified_by'
        db.delete_column('checklists_rank', 'modified_by')

        # Deleting field 'Rank.modified_on'
        db.delete_column('checklists_rank', 'modified_on')

        # Deleting field 'Sex.created_by'
        db.delete_column('checklists_sex', 'created_by')

        # Deleting field 'Sex.created_on'
        db.delete_column('checklists_sex', 'created_on')

        # Deleting field 'Sex.modified_by'
        db.delete_column('checklists_sex', 'modified_by')

        # Deleting field 'Sex.modified_on'
        db.delete_column('checklists_sex', 'modified_on')

        # Deleting field 'Protocol.created_by'
        db.delete_column('checklists_protocol', 'created_by')

        # Deleting field 'Protocol.created_on'
        db.delete_column('checklists_protocol', 'created_on')

        # Deleting field 'Protocol.modified_by'
        db.delete_column('checklists_protocol', 'modified_by')

        # Deleting field 'Protocol.modified_on'
        db.delete_column('checklists_protocol', 'modified_on')

        # Deleting field 'SpeciesGroup.created_by'
        db.delete_column('checklists_speciesgroup', 'created_by')

        # Deleting field 'SpeciesGroup.created_on'
        db.delete_column('checklists_speciesgroup', 'created_on')

        # Deleting field 'SpeciesGroup.modified_by'
        db.delete_column('checklists_speciesgroup', 'modified_by')

        # Deleting field 'SpeciesGroup.modified_on'
        db.delete_column('checklists_speciesgroup', 'modified_on')

        # Deleting field 'Direction.created_by'
        db.delete_column('checklists_direction', 'created_by')

        # Deleting field 'Direction.created_on'
        db.delete_column('checklists_direction', 'created_on')

        # Deleting field 'Direction.modified_by'
        db.delete_column('checklists_direction', 'modified_by')

        # Deleting field 'Direction.modified_on'
        db.delete_column('checklists_direction', 'modified_on')

        # Deleting field 'Entry.created_by'
        db.delete_column('checklists_entry', 'created_by')

        # Deleting field 'Entry.created_on'
        db.delete_column('checklists_entry', 'created_on')

        # Deleting field 'Entry.modified_by'
        db.delete_column('checklists_entry', 'modified_by')

        # Deleting field 'Entry.modified_on'
        db.delete_column('checklists_entry', 'modified_on')

        # Deleting field 'Plumage.created_by'
        db.delete_column('checklists_plumage', 'created_by')

        # Deleting field 'Plumage.created_on'
        db.delete_column('checklists_plumage', 'created_on')

        # Deleting field 'Plumage.modified_by'
        db.delete_column('checklists_plumage', 'modified_by')

        # Deleting field 'Plumage.modified_on'
        db.delete_column('checklists_plumage', 'modified_on')

        # Deleting field 'Detail.created_by'
        db.delete_column('checklists_detail', 'created_by')

        # Deleting field 'Detail.created_on'
        db.delete_column('checklists_detail', 'created_on')

        # Deleting field 'Detail.modified_by'
        db.delete_column('checklists_detail', 'modified_by')

        # Deleting field 'Detail.modified_on'
        db.delete_column('checklists_detail', 'modified_on')

        # Deleting field 'SpeciesStatus.created_by'
        db.delete_column(u'checklists_speciesstatus', 'created_by')

        # Deleting field 'SpeciesStatus.created_on'
        db.delete_column(u'checklists_speciesstatus', 'created_on')

        # Deleting field 'SpeciesStatus.modified_by'
        db.delete_column(u'checklists_speciesstatus', 'modified_by')

        # Deleting field 'SpeciesStatus.modified_on'
        db.delete_column(u'checklists_speciesstatus', 'modified_on')

        # Deleting field 'Species.created_by'
        db.delete_column('checklists_species', 'created_by')

        # Deleting field 'Species.created_on'
        db.delete_column('checklists_species', 'created_on')

        # Deleting field 'Species.modified_by'
        db.delete_column('checklists_species', 'modified_by')

        # Deleting field 'Species.modified_on'
        db.delete_column('checklists_species', 'modified_on')

        # Deleting field 'Map.created_by'
        db.delete_column('checklists_map', 'created_by')

        # Deleting field 'Map.created_on'
        db.delete_column('checklists_map', 'created_on')

        # Deleting field 'Map.modified_by'
        db.delete_column('checklists_map', 'modified_by')

        # Deleting field 'Map.modified_on'
        db.delete_column('checklists_map', 'modified_on')

        # Deleting field 'Location.created_by'
        db.delete_column('checklists_location', 'created_by')

        # Deleting field 'Location.created_on'
        db.delete_column('checklists_location', 'created_on')

        # Deleting field 'Location.modified_by'
        db.delete_column('checklists_location', 'modified_by')

        # Deleting field 'Location.modified_on'
        db.delete_column('checklists_location', 'modified_on')

        # Deleting field 'EntryTag.created_by'
        db.delete_column(u'checklists_entrytag', 'created_by')

        # Deleting field 'EntryTag.created_on'
        db.delete_column(u'checklists_entrytag', 'created_on')

        # Deleting field 'EntryTag.modified_by'
        db.delete_column(u'checklists_entrytag', 'modified_by')

        # Deleting field 'EntryTag.modified_on'
        db.delete_column(u'checklists_entrytag', 'modified_on')

        # Deleting field 'Method.created_by'
        db.delete_column('checklists_method', 'created_by')

        # Deleting field 'Method.created_on'
        db.delete_column('checklists_method', 'created_on')

        # Deleting field 'Method.modified_by'
        db.delete_column('checklists_method', 'modified_by')

        # Deleting field 'Method.modified_on'
        db.delete_column('checklists_method', 'modified_on')

        # Deleting field 'Filter.created_by'
        db.delete_column('checklists_filter', 'created_by')

        # Deleting field 'Filter.created_on'
        db.delete_column('checklists_filter', 'created_on')

        # Deleting field 'Filter.modified_by'
        db.delete_column('checklists_filter', 'modified_by')

        # Deleting field 'Filter.modified_on'
        db.delete_column('checklists_filter', 'modified_on')

        # Deleting field 'Age.created_by'
        db.delete_column('checklists_age', 'created_by')

        # Deleting field 'Age.created_on'
        db.delete_column('checklists_age', 'created_on')

        # Deleting field 'Age.modified_by'
        db.delete_column('checklists_age', 'modified_by')

        # Deleting field 'Age.modified_on'
        db.delete_column('checklists_age', 'modified_on')

        # Deleting field 'Observer.created_by'
        db.delete_column('checklists_observer', 'created_by')

        # Deleting field 'Observer.created_on'
        db.delete_column('checklists_observer', 'created_on')

        # Deleting field 'Observer.modified_by'
        db.delete_column('checklists_observer', 'modified_by')

        # Deleting field 'Observer.modified_on'
        db.delete_column('checklists_observer', 'modified_on')

        # Deleting field 'Activity.created_by'
        db.delete_column('checklists_activity', 'created_by')

        # Deleting field 'Activity.created_on'
        db.delete_column('checklists_activity', 'created_on')

        # Deleting field 'Activity.modified_by'
        db.delete_column('checklists_activity', 'modified_by')

        # Deleting field 'Activity.modified_on'
        db.delete_column('checklists_activity', 'modified_on')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'checklists.activity': {
            'Meta': {'object_name': 'Activity'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'checklists.age': {
            'Meta': {'object_name': 'Age'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'checklists.checklist': {
            'Meta': {'object_name': 'Checklist'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Activity']", 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'db_index': 'True'}),
            'comment_en': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']", 'on_delete': 'models.PROTECT'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'observers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['checklists.Observer']", 'null': 'True', 'blank': 'True'}),
            'observers_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reporter'", 'null': 'True', 'to': "orm['checklists.Observer']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'checklists.detail': {
            'Meta': {'object_name': 'Detail'},
            'age': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Age']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Direction']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['checklists.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plumage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Plumage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'sex': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Sex']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'checklists.direction': {
            'Meta': {'object_name': 'Direction'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'checklists.entry': {
            'Meta': {'object_name': 'Entry'},
            'checklist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['checklists.Checklist']"}),
            'comment_en': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'species_entries'", 'on_delete': 'models.PROTECT', 'to': "orm['checklists.Species']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['checklists.EntryTag']", 'null': 'True', 'blank': 'True'})
        },
        'checklists.entrytag': {
            'Meta': {'object_name': 'EntryTag'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'checklists.filter': {
            'Meta': {'object_name': 'Filter'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'checklists.location': {
            'Meta': {'object_name': 'Location'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gridref': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'island': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'checklists.map': {
            'Meta': {'object_name': 'Map'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'checklists.method': {
            'Meta': {'object_name': 'Method'},
            'area': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'checklist': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['checklists.Checklist']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'distance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration_hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration_minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Protocol']", 'on_delete': 'models.PROTECT'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'checklists.observer': {
            'Meta': {'object_name': 'Observer'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'checklists.plumage': {
            'Meta': {'object_name': 'Plumage'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'checklists.protocol': {
            'Meta': {'object_name': 'Protocol'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'checklists.rank': {
            'Meta': {'object_name': 'Rank'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'checklists.sex': {
            'Meta': {'object_name': 'Sex'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        'checklists.species': {
            'Meta': {'object_name': 'Species'},
            'common_name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.SpeciesGroup']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plural_name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'rank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Rank']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'scientific_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'standard_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['checklists.SpeciesStatus']", 'null': 'True', 'blank': 'True'})
        },
        'checklists.speciesgroup': {
            'Meta': {'object_name': 'SpeciesGroup'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'family': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'genus': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'order': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'checklists.speciesstatus': {
            'Meta': {'object_name': 'SpeciesStatus'},
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['checklists']


from ..utils import i18n_migration

i18n_migration(Migration)
