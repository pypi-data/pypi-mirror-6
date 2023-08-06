# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for entry in orm['checklists.Entry'].objects.all():
            if entry.subspecies:
                entry.species = entry.subspecies
                entry.save()

    def backwards(self, orm):
        for entry in orm['checklists.Entry'].objects.all():
            if entry.subspecies:
                # restore species from subspecies
                scientific_name = ' '.join(entry.subspecies.scientific_name.split()[:2])
                entry.species = orm['checklists.Species'].objects.get(scientific_name=scientific_name)
                entry.save()
            else:
                # recover from deleting subspecies field
                if len(entry.scientific_name.split()) == 3:
                    entry.subspecies = entry.species
                    entry.save()

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
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'})
        },
        'checklists.age': {
            'Meta': {'object_name': 'Age'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'checklists.checklist': {
            'Meta': {'object_name': 'Checklist'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Activity']", 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'db_index': 'True'}),
            'comment_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
        'checklists.code': {
            'Meta': {'object_name': 'Code'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'checklists.detail': {
            'Meta': {'object_name': 'Detail'},
            'age': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Age']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'direction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Direction']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['checklists.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'plumage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Plumage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'sex': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Sex']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'checklists.direction': {
            'Meta': {'object_name': 'Direction'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'checklists.entry': {
            'Meta': {'object_name': 'Entry'},
            'checklist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['checklists.Checklist']"}),
            'comment_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'species_entries'", 'on_delete': 'models.PROTECT', 'to': "orm['checklists.Species']"}),
            'subspecies': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subspecies_entries'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['checklists.Species']"})
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
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'checklists.locationalias': {
            'Meta': {'object_name': 'LocationAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'checklists.observer': {
            'Meta': {'object_name': 'Observer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'checklists.photo': {
            'Meta': {'object_name': 'Photo'},
            'caption_en': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['contenttypes.ContentType']"}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'image_height': ('django.db.models.fields.IntegerField', [], {}),
            'image_width': ('django.db.models.fields.IntegerField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'thumbnail_height': ('django.db.models.fields.IntegerField', [], {}),
            'thumbnail_width': ('django.db.models.fields.IntegerField', [], {})
        },
        'checklists.plumage': {
            'Meta': {'object_name': 'Plumage'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'checklists.protocol': {
            'Meta': {'object_name': 'Protocol'},
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'})
        },
        'checklists.rank': {
            'Meta': {'object_name': 'Rank'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'checklists.sex': {
            'Meta': {'object_name': 'Sex'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'standard_name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'checklists.speciesalias': {
            'Meta': {'object_name': 'SpeciesAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Species']"})
        },
        'checklists.speciesgroup': {
            'Meta': {'object_name': 'SpeciesGroup'},
            'family': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'genus': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'}),
            'order': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'})
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
    symmetrical = True


from ..utils import i18n_migration

i18n_migration(Migration)
