# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.conf import settings
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):

        if orm['checklists.Species'].objects.all().exists():
            names = {}
            for language_code, language_name in settings.LANGUAGES:
                names["name_%s" % language_code] = ''
            # set the species type and group if there are existing records
            species_type, created = orm['checklists.SpeciesType'].objects.get_or_create(
                code='SPE', **names)

            species_group, created = orm['checklists.SpeciesGroup'].objects.get_or_create(
                order='Order', family='Family', genus='Genus', **names)

            for species in orm['checklists.Species'].objects.all():
                if species.species_type is None:
                    species.species_type = species_type
                if species.group is None:
                    species.group = species_group
                for language_code, language_name in settings.LANGUAGES:
                    if hasattr(species, 'plural_name_%s' % language_code):
                        if getattr(species, 'plural_name_%s' % language_code) is None:
                            setattr(species, 'plural_name_%s' % language_code, '')
                species.save()

        for checklist in orm['checklists.Checklist'].objects.all():
            for language_code, language_name in settings.LANGUAGES:
                if hasattr(checklist, 'comment_%s' % language_code):
                    if getattr(checklist, 'comment_%s' % language_code) is None:
                        setattr(checklist, 'comment_%s' % language_code, '')
            checklist.save()

        for entry in orm['checklists.Entry'].objects.all():
            for language_code, language_name in settings.LANGUAGES:
                if hasattr(entry, 'description_%s' % language_code):
                    if getattr(entry, 'description_%s' % language_code) is None:
                        setattr(entry, 'description_%s' % language_code, '')
                if hasattr(entry, 'comment_%s' % language_code):
                    if getattr(entry, 'comment_%s' % language_code) is None:
                        setattr(entry, 'comment_%s' % language_code, '')
            entry.save()

    def backwards(self, orm):
        pass

    models = {
        'checklists.age': {
            'Meta': {'object_name': 'Age'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'checklists.checklist': {
            'Meta': {'object_name': 'Checklist'},
            'added_on': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'comment_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']"}),
            'observers': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'observers_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'submitted_by': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'checklists.detail': {
            'Meta': {'object_name': 'Detail'},
            'age_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Age']", 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'direction_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Direction']", 'null': 'True', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['checklists.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'plumage_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Plumage']", 'null': 'True', 'blank': 'True'}),
            'sex_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Sex']", 'null': 'True', 'blank': 'True'})
        },
        'checklists.direction': {
            'Meta': {'object_name': 'Direction'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'checklists.entry': {
            'Meta': {'object_name': 'Entry'},
            'checklist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['checklists.Checklist']"}),
            'comment_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'description_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
        'checklists.plumage': {
            'Meta': {'object_name': 'Plumage'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'checklists.protocol': {
            'Meta': {'object_name': 'Protocol'},
            'area': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'checklist': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['checklists.Checklist']", 'unique': 'True'}),
            'distance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'duration_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'duration_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.ProtocolType']"})
        },
        'checklists.protocoltype': {
            'Meta': {'object_name': 'ProtocolType'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        'checklists.sex': {
            'Meta': {'object_name': 'Sex'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'checklists.species': {
            'Meta': {'object_name': 'Species'},
            'common_name_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.SpeciesGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'iou_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plural_name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'scientific_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'species_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.SpeciesType']", 'null': 'True', 'blank': 'True'})
        },
        'checklists.speciesalias': {
            'Meta': {'object_name': 'SpeciesAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Species']"})
        },
        'checklists.speciesgroup': {
            'Meta': {'object_name': 'SpeciesGroup'},
            'family': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'genus': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'}),
            'order': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'checklists.speciestype': {
            'Meta': {'object_name': 'SpeciesType'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
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
