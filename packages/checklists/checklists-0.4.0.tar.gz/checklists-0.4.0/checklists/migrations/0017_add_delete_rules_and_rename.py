# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Rename model 'SpeciesType'
        db.rename_table('checklists_speciestype', 'checklists_rank')

        # Rename field 'Checklist.source_url'
        db.rename_column('checklists_checklist', 'source_url', 'url')

        # Rename field 'Checklist.iou_name'
        db.rename_column('checklists_species', 'iou_name', 'standard_name')

        # Rename field 'Species.species_type'
        db.rename_column('checklists_species', 'species_type_id', 'rank_id')

        # Rename field 'Species.name_order'
        db.rename_column('checklists_species', 'name_order', 'order')

        # Changing field 'Location.name'
        db.alter_column('checklists_location', 'name', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Location.slug'
        db.alter_column('checklists_location', 'slug', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Rename field 'Location.long'
        db.rename_column('checklists_location', 'long', 'lon')

        # Deleting field 'Location.url'
        db.delete_column('checklists_location', 'url')

        # Changing field 'Checklist.location'
        db.alter_column('checklists_checklist', 'location_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Location'], on_delete=models.PROTECT))

        # Changing field 'Protocol.protocol_type'
        db.alter_column('checklists_protocol', 'protocol_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.ProtocolType'], on_delete=models.PROTECT))

        # Changing field 'Detail.direction'
        db.alter_column('checklists_detail', 'direction_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Direction'], null=True, on_delete=models.SET_NULL))

        # Changing field 'Detail.age'
        db.alter_column('checklists_detail', 'age_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Age'], null=True, on_delete=models.SET_NULL))

        # Changing field 'Detail.sex'
        db.alter_column('checklists_detail', 'sex_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Sex'], null=True, on_delete=models.SET_NULL))

        # Changing field 'Detail.plumage'
        db.alter_column('checklists_detail', 'plumage_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Plumage'], null=True, on_delete=models.SET_NULL))

        # Changing field 'Entry.subspecies'
        db.alter_column('checklists_entry', 'subspecies_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['checklists.Species']))

        # Changing field 'Entry.species'
        db.alter_column('checklists_entry', 'species_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['checklists.Species']))

        # Changing field 'Species.group'
        db.alter_column('checklists_species', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.SpeciesGroup'], null=True, on_delete=models.SET_NULL))


    def backwards(self, orm):
        # Rename model 'SpeciesType'
        db.rename_table('checklists_rank', 'checklists_speciestype')

        # Rename field 'Checklist.source_url'
        db.rename_column('checklists_checklist', 'url', 'source_url')

        # Rename field 'Checklist.iou_name'
        db.rename_column('checklists_species', 'standard_name', 'iou_name')

        # Rename field 'Species.species_type'
        db.rename_column('checklists_species', 'rank', 'species_type')

        # Rename field 'Species.name_order'
        db.rename_column('checklists_species', 'order', 'name_order')

        # Rename field 'Location.long'
        db.rename_column('checklists_location', 'lon', 'long')

        # Changing field 'Location.name'
        db.alter_column('checklists_location', 'name', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'Location.slug'
        db.alter_column('checklists_location', 'slug', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Adding field 'Location.url'
        db.add_column('checklists_location', 'url',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Changing field 'Checklist.location'
        db.alter_column('checklists_checklist', 'location_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Location']))

        # Changing field 'Protocol.protocol_type'
        db.alter_column('checklists_protocol', 'protocol_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.ProtocolType']))

        # Changing field 'Detail.direction'
        db.alter_column('checklists_detail', 'direction_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Direction'], null=True))

        # Changing field 'Detail.age'
        db.alter_column('checklists_detail', 'age_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Age'], null=True))

        # Changing field 'Detail.sex'
        db.alter_column('checklists_detail', 'sex_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Sex'], null=True))

        # Changing field 'Detail.plumage'
        db.alter_column('checklists_detail', 'plumage_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Plumage'], null=True))

        # Changing field 'Entry.subspecies'
        db.alter_column('checklists_entry', 'subspecies_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['checklists.Species']))

        # Changing field 'Entry.species'
        db.alter_column('checklists_entry', 'species_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.Species']))

        # Changing field 'Species.group'
        db.alter_column('checklists_species', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['checklists.SpeciesGroup']))


    models = {
        'checklists.age': {
            'Meta': {'object_name': 'Age'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'checklists.checklist': {
            'Meta': {'object_name': 'Checklist'},
            'added_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'db_index': 'True'}),
            'comment_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']", 'on_delete': 'models.PROTECT'}),
            'observers': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'observers_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'submitted_by': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'checklists.detail': {
            'Meta': {'object_name': 'Detail'},
            'age': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Age']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'direction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Direction']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['checklists.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        'checklists.location': {
            'Meta': {'object_name': 'Location'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gridref': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'checklists.locationalias': {
            'Meta': {'object_name': 'LocationAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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
            'area': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'checklist': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['checklists.Checklist']", 'unique': 'True'}),
            'distance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration_hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration_minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.ProtocolType']", 'on_delete': 'models.PROTECT'})
        },
        'checklists.protocoltype': {
            'Meta': {'object_name': 'ProtocolType'},
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


from ..utils import i18n_migration

i18n_migration(Migration)
