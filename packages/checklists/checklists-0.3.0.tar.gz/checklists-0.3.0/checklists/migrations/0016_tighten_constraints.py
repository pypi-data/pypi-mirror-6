# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Checklist.observers_count'
        db.alter_column('checklists_checklist', 'observers_count', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Checklist.comment_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_checklist', 'comment_%s' % language_code,
                            self.gf('django.db.models.fields.TextField')(default=''))


        # Changing field 'Age.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_age', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=20))
        # Adding unique constraint on 'Age', fields ['code']
        db.create_unique('checklists_age', ['code'])


        # Changing field 'Sex.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_sex', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=10))
        # Adding unique constraint on 'Sex', fields ['code']
        db.create_unique('checklists_sex', ['code'])


        # Changing field 'Direction.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_direction', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=20))
        # Adding unique constraint on 'Direction', fields ['code']
        db.create_unique('checklists_direction', ['code'])


        # Changing field 'Plumage.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_plumage', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=20))
        # Adding unique constraint on 'Plumage', fields ['code']
        db.create_unique('checklists_plumage', ['code'])


        # Changing field 'Protocol.distance'
        db.alter_column('checklists_protocol', 'distance', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Protocol.area'
        db.alter_column('checklists_protocol', 'area', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Protocol.duration_minutes'
        db.alter_column('checklists_protocol', 'duration_minutes', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Protocol.duration_hours'
        db.alter_column('checklists_protocol', 'duration_hours', self.gf('django.db.models.fields.IntegerField')())


        # Changing field 'Entry.description_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_entry', 'description_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Entry.comment_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_entry', 'comment_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Species.group'
        db.alter_column('checklists_species', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['checklists.SpeciesGroup']))

        # Changing field 'Species.plural_name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_species', 'plural_name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=40))

        # Changing field 'Species.species_type'
        db.alter_column('checklists_species', 'species_type_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['checklists.SpeciesType']))

        # Changing field 'ProtocolType.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_protocoltype', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=40))

        # Changing field 'SpeciesType.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_speciestype', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=40))
        # Adding unique constraint on 'SpeciesType', fields ['code']
        db.create_unique('checklists_speciestype', ['code'])

        # Changing field 'Photo.caption_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_photo', 'caption_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(default='', max_length=250))

    def backwards(self, orm):
        # Removing unique constraint on 'SpeciesType', fields ['code']
        db.delete_unique('checklists_speciestype', ['code'])

        # Removing unique constraint on 'Plumage', fields ['code']
        db.delete_unique('checklists_plumage', ['code'])

        # Removing unique constraint on 'Age', fields ['code']
        db.delete_unique('checklists_age', ['code'])

        # Removing unique constraint on 'Sex', fields ['code']
        db.delete_unique('checklists_sex', ['code'])

        # Removing unique constraint on 'Direction', fields ['code']
        db.delete_unique('checklists_direction', ['code'])


        # Changing field 'Checklist.observers_count'
        db.alter_column('checklists_checklist', 'observers_count', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'Checklist.comment_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_checklist', 'comment_%s' % language_code,
                            self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Direction.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_direction', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Sex.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_sex', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

        # Changing field 'Protocol.distance'
        db.alter_column('checklists_protocol', 'distance', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'Protocol.area'
        db.alter_column('checklists_protocol', 'area', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'Protocol.duration_minutes'
        db.alter_column('checklists_protocol', 'duration_minutes', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'Protocol.duration_hours'
        db.alter_column('checklists_protocol', 'duration_hours', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'Age.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_age', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Plumage.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_plumage', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=20, null=True))


        # Changing field 'Entry.description_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_entry', 'description_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Entry.comment_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_entry', 'comment_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Species.group'
        db.alter_column('checklists_species', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.SpeciesGroup'], null=True))

        # Changing field 'Species.plural_name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_species', 'plural_name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'Species.species_type'
        db.alter_column('checklists_species', 'species_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checklists.SpeciesType'], null=True))

        # Changing field 'ProtocolType.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_protocoltype', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'SpeciesType.name_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_speciestype', 'name_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'Photo.caption_en'
        for language_code, language_name in settings.LANGUAGES:
            db.alter_column('checklists_photo', 'caption_%s' % language_code,
                            self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

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
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Location']"}),
            'observers': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'observers_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'submitted_by': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'checklists.detail': {
            'Meta': {'object_name': 'Detail'},
            'age': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Age']", 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'direction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Direction']", 'null': 'True', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['checklists.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'plumage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Plumage']", 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Sex']", 'null': 'True', 'blank': 'True'})
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
            'species': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'species_entries'", 'to': "orm['checklists.Species']"}),
            'subspecies': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subspecies_entries'", 'null': 'True', 'to': "orm['checklists.Species']"})
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
            'long': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
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
            'protocol_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.ProtocolType']"})
        },
        'checklists.protocoltype': {
            'Meta': {'object_name': 'ProtocolType'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
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
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.SpeciesGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'iou_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plural_name_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'scientific_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'species_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.SpeciesType']"})
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
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'order': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'checklists.speciestype': {
            'Meta': {'object_name': 'SpeciesType'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '40'})
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
