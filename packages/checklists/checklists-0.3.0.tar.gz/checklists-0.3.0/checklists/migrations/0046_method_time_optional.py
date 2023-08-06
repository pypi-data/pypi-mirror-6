# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Changing field 'Method.time'
        db.alter_column('checklists_method', 'time', self.gf('django.db.models.fields.TimeField')(null=True))


    def backwards(self, orm):
        # Changing field 'Method.time'
        db.alter_column('checklists_method', 'time', self.gf('django.db.models.fields.TimeField')(default='00:00:00'))


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'checklists.age': {
            'Meta': {'object_name': 'Age'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'checklists.checklist': {
            'Meta': {'object_name': 'Checklist'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Activity']", 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'db_index': 'True'}),
            'comment_en': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']", 'on_delete': 'models.PROTECT'}),
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
            'direction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Direction']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['checklists.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'plumage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Plumage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'sex': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Sex']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'checklists.direction': {
            'Meta': {'object_name': 'Direction'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'checklists.entry': {
            'Meta': {'object_name': 'Entry'},
            'checklist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['checklists.Checklist']"}),
            'comment_en': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'species_entries'", 'on_delete': 'models.PROTECT', 'to': "orm['checklists.Species']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['checklists.EntryTag']", 'null': 'True', 'blank': 'True'})
        },
        'checklists.entrytag': {
            'Meta': {'object_name': 'EntryTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'checklists.filter': {
            'Meta': {'object_name': 'Filter'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'checklists.location': {
            'Meta': {'object_name': 'Location'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gridref': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'island': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'checklists.map': {
            'Meta': {'object_name': 'Map'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'checklists.method': {
            'Meta': {'object_name': 'Method'},
            'area': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'checklist': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['checklists.Checklist']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'distance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration_hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration_minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Protocol']", 'on_delete': 'models.PROTECT'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'checklists.observer': {
            'Meta': {'object_name': 'Observer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'checklists.plumage': {
            'Meta': {'object_name': 'Plumage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'checklists.protocol': {
            'Meta': {'object_name': 'Protocol'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'checklists.rank': {
            'Meta': {'object_name': 'Rank'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'checklists.sex': {
            'Meta': {'object_name': 'Sex'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        'checklists.species': {
            'Meta': {'object_name': 'Species'},
            'common_name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.SpeciesGroup']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plural_name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'rank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Rank']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'scientific_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'standard_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['checklists.SpeciesStatus']", 'null': 'True', 'blank': 'True'})
        },
        'checklists.speciesgroup': {
            'Meta': {'object_name': 'SpeciesGroup'},
            'family': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'genus': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'order': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'checklists.speciesstatus': {
            'Meta': {'object_name': 'SpeciesStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
