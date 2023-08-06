# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Species'
        db.create_table('checklists_species', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('iou_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('scientific_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('name_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rank', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))

        # Add localized fields for the Species table
        for language_code, language_name in settings.LANGUAGES:
            db.add_column('checklists_species', 'common_name_%s' % language_code,
                          self.gf('django.db.models.fields.CharField')
                          (default='', max_length=40, blank=True))
            db.add_column('checklists_species', 'plural_name_%s' % language_code,
                          self.gf('django.db.models.fields.CharField')
                          (max_length=40, null=True, blank=True))

        db.send_create_signal('checklists', ['Species'])

        # Adding model 'SpeciesAlias'
        db.create_table('checklists_speciesalias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('species', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Species'])),
        ))
        db.send_create_signal('checklists', ['SpeciesAlias'])

        # Adding model 'Location'
        db.create_table('checklists_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('lat', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('long', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('gridref', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('include', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checklists', ['Location'])

        # Adding model 'LocationAlias'
        db.create_table('checklists_locationalias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Location'])),
        ))
        db.send_create_signal('checklists', ['LocationAlias'])

        # Adding model 'Checklist'
        db.create_table('checklists_checklist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added_on', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Location'])),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('duration_hours', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('duration_minutes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('distance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('area', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('range', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('submitted_by', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('observers', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('observers_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('source_url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('include', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))

        # Add localized fields for the Entry table
        for language_code, language_name in settings.LANGUAGES:
            db.add_column('checklists_checklist', 'comment_%s' % language_code,
                          self.gf('django.db.models.fields.TextField')
                          (null=True, blank=True))

        db.send_create_signal('checklists', ['Checklist'])

        # Adding model 'Entry'
        db.create_table('checklists_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('checklist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entries', to=orm['checklists.Checklist'])),
            ('species', self.gf('django.db.models.fields.related.ForeignKey')(related_name='species_entries', to=orm['checklists.Species'])),
            ('subspecies', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subspecies_entries', null=True, to=orm['checklists.Species'])),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('include', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lat', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('long', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
        ))

        # Add localized fields for the Entry table
        for language_code, language_name in settings.LANGUAGES:
            db.add_column('checklists_entry', 'description_%s' % language_code,
                          self.gf('django.db.models.fields.CharField')
                          (max_length=255, null=True, blank=True))
            db.add_column('checklists_entry', 'comment_%s' % language_code,
                          self.gf('django.db.models.fields.CharField')
                          (max_length=255, null=True, blank=True))

        db.send_create_signal('checklists', ['Entry'])

        # Adding model 'Detail'
        db.create_table('checklists_detail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='details', to=orm['checklists.Entry'])),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('age', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('plumage', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('lat', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('long', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
        ))
        db.send_create_signal('checklists', ['Detail'])

        # Adding model 'Photo'
        db.create_table('checklists_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('image_height', self.gf('django.db.models.fields.IntegerField')()),
            ('image_width', self.gf('django.db.models.fields.IntegerField')()),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('thumbnail_height', self.gf('django.db.models.fields.IntegerField')()),
            ('thumbnail_width', self.gf('django.db.models.fields.IntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))

        # Add localized fields for the Photo table
        for language_code, language_name in settings.LANGUAGES:
            db.add_column('checklists_photo', 'caption_%s' % language_code,
                          self.gf('django.db.models.fields.CharField')
                          (max_length=250, null=True, blank=True))

        db.send_create_signal('checklists', ['Photo'])


    def backwards(self, orm):
        # Deleting model 'Species'
        db.delete_table('checklists_species')

        # Deleting model 'SpeciesAlias'
        db.delete_table('checklists_speciesalias')

        # Deleting model 'Location'
        db.delete_table('checklists_location')

        # Deleting model 'LocationAlias'
        db.delete_table('checklists_locationalias')

        # Deleting model 'Checklist'
        db.delete_table('checklists_checklist')

        # Deleting model 'Entry'
        db.delete_table('checklists_entry')

        # Deleting model 'Detail'
        db.delete_table('checklists_detail')

        # Deleting model 'Photo'
        db.delete_table('checklists_photo')

    models = {
        'checklists.checklist': {
            'Meta': {'object_name': 'Checklist'},
            'added_on': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'area': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'comment_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'distance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'duration_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'duration_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']"}),
            'observers': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'observers_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'range': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'submitted_by': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'checklists.detail': {
            'Meta': {'object_name': 'Detail'},
            'age': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['checklists.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'long': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'plumage': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'})
        },
        'checklists.entry': {
            'Meta': {'object_name': 'Entry'},
            'checklist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['checklists.Checklist']"}),
            'comment_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'description_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'long': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'species_entries'", 'to': "orm['checklists.Species']"}),
            'subspecies': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subspecies_entries'", 'null': 'True', 'to': "orm['checklists.Species']"})
        },
        'checklists.location': {
            'Meta': {'object_name': 'Location'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gridref': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'long': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'checklists.locationalias': {
            'Meta': {'object_name': 'LocationAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'checklists.photo': {
            'Meta': {'object_name': 'Photo'},
            'caption_en': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['contenttypes.ContentType']"}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'image_height': ('django.db.models.fields.IntegerField', [], {}),
            'image_width': ('django.db.models.fields.IntegerField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'thumbnail_height': ('django.db.models.fields.IntegerField', [], {}),
            'thumbnail_width': ('django.db.models.fields.IntegerField', [], {})
        },
        'checklists.species': {
            'Meta': {'object_name': 'Species'},
            'common_name_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iou_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plural_name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'scientific_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'checklists.speciesalias': {
            'Meta': {'object_name': 'SpeciesAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Species']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['checklists']


from ..utils import i18n_migration

i18n_migration(Migration)
