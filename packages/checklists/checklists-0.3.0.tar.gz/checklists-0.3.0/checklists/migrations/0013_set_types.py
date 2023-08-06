# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.conf import settings

class Migration(DataMigration):

    def forwards(self, orm):
        # set the species types if there are existing records
        if orm['checklists.Species'].objects.all().exists():
            names = {}
            for language_code, language_name in settings.LANGUAGES:
                names["name_%s" % language_code] = ''
            subspecies_type = orm['checklists.SpeciesType'].objects.create(code='SUB', **names)
            species_type = orm['checklists.SpeciesType'].objects.create(code='SPE', **names)
            genus_type = orm['checklists.SpeciesType'].objects.create(code='GEN', **names)

            for species in orm['checklists.Species'].objects.all():
                if species.rank == 'SU':
                    species.species_type = subspecies_type
                elif species.rank == 'SP':
                    species.species_type = species_type
                elif species.rank == 'GE':
                    species.species_type = genus_type
                species.save()

        # set the age types if there are existing records
        if orm['checklists.Detail'].objects.all().exists():
            names = {}
            for language_code, language_name in settings.LANGUAGES:
                names["name_%s" % language_code] = ''
            juv = orm['checklists.Age'].objects.create(code='JUV', **names)
            imm = orm['checklists.Age'].objects.create(code='IMM', **names)
            ad = orm['checklists.Age'].objects.create(code='AD', **names)
            cy1 = orm['checklists.Age'].objects.create(code='1CY', **names)
            cy2 = orm['checklists.Age'].objects.create(code='2CY', **names)
            cy3 = orm['checklists.Age'].objects.create(code='3CY', **names)
            cy4 = orm['checklists.Age'].objects.create(code='4CY', **names)

            for detail in orm['checklists.Detail'].objects.all():
                if detail.age == 'JUV':
                    detail.age_type = juv
                elif detail.age == 'IMM':
                    detail.age_type = imm
                elif detail.age == 'AD':
                    detail.age_type = ad
                elif detail.age == '1CY':
                    detail.age_type = cy1
                elif detail.age == '2CY':
                    detail.age_type = cy2
                elif detail.age == '3CY':
                    detail.age_type = cy3
                elif detail.age == '4CY':
                    detail.age_type = cy4
                else:
                    detail.age_type = None
                detail.save()

            # set the sex types
            male = orm['checklists.Sex'].objects.create(code='M', **names)
            female = orm['checklists.Sex'].objects.create(code='F', **names)

            for detail in orm['checklists.Detail'].objects.all():
                if detail.sex == 'M':
                    detail.sex_type = male
                elif detail.sex == 'F':
                    detail.sex_type = female
                else:
                    detail.sex_type = None
                detail.save()

            # set the plumage types
            blue = orm['checklists.Plumage'].objects.create(code='BPH', **names)
            dark = orm['checklists.Plumage'].objects.create(code='DPH', **names)
            light = orm['checklists.Plumage'].objects.create(code='LPH', **names)
            mel = orm['checklists.Plumage'].objects.create(code='MEL', **names)
            leu = orm['checklists.Plumage'].objects.create(code='LEU', **names)
            alb = orm['checklists.Plumage'].objects.create(code='ALB', **names)

            for detail in orm['checklists.Detail'].objects.all():
                if detail.plumage == 'BPH':
                    detail.plumage_type = blue
                elif detail.plumage == 'DPH':
                    detail.plumage_type = dark
                elif detail.plumage == 'LPH':
                    detail.plumage_type = light
                elif detail.plumage == 'MEL':
                    detail.plumage_type = mel
                elif detail.plumage == 'LEU':
                    detail.plumage_type = leu
                elif detail.plumage == 'ALB':
                    detail.plumage_type = alb
                else:
                    detail.plumage_type = None
                detail.save()

            # set the direction types
            n = orm['checklists.Direction'].objects.create(code='N', **names)
            ne = orm['checklists.Direction'].objects.create(code='NE', **names)
            e = orm['checklists.Direction'].objects.create(code='E', **names)
            se = orm['checklists.Direction'].objects.create(code='SE', **names)
            s = orm['checklists.Direction'].objects.create(code='S', **names)
            sw = orm['checklists.Direction'].objects.create(code='SW', **names)
            w = orm['checklists.Direction'].objects.create(code='W', **names)
            nw = orm['checklists.Direction'].objects.create(code='NW', **names)

            for detail in orm['checklists.Detail'].objects.all():
                if detail.direction == 'N':
                    detail.direction_type = n
                elif detail.direction == 'NE':
                    detail.direction_type = ne
                elif detail.direction == 'E':
                    detail.direction_type = e
                elif detail.direction == 'SE':
                    detail.direction_type = se
                elif detail.direction == 'S':
                    detail.direction_type = s
                elif detail.direction == 'SW':
                    detail.direction_type = sw
                elif detail.direction == 'W':
                    detail.direction_type = w
                elif detail.direction == 'NW':
                    detail.direction_type = nw
                else:
                    detail.direction_type = None
                detail.save()


    def backwards(self, orm):

        if orm['checklists.Species'].objects.all().exists():
            # restore species rank
            subspecies_type = orm['checklists.SpeciesType'].objects.get(code='SUB')
            species_type = orm['checklists.SpeciesType'].objects.get(code='SPE')
            genus_type = orm['checklists.SpeciesType'].objects.get(code='GEN')

            for species in orm['checklists.Species'].objects.all():
                if species.species_type == subspecies_type:
                    species.rank = 'SU'
                elif species.species_type == species_type:
                    species.rank = 'SP'
                elif species.species_type == genus_type:
                    species.rank = 'GE'
                species.save()

            orm['checklists.SpeciesType'].objects.all().delete()

        if orm['checklists.Detail'].objects.all().exists():
            # restore age
            juv = orm['checklists.Age'].objects.get(code='JUV')
            imm = orm['checklists.Age'].objects.get(code='IMM')
            ad = orm['checklists.Age'].objects.get(code='AD')
            cy1 = orm['checklists.Age'].objects.get(code='1CY')
            cy2 = orm['checklists.Age'].objects.get(code='2CY')
            cy3 = orm['checklists.Age'].objects.get(code='3CY')
            cy4 = orm['checklists.Age'].objects.get(code='4CY')

            for detail in orm['checklists.Detail'].objects.all():
                if detail.age_type == juv:
                    detail.age = 'JUV'
                elif detail.age_type == imm:
                    detail.age = 'IMM'
                elif detail.age_type == ad:
                    detail.age = 'AD'
                elif detail.age_type == cy1:
                    detail.age = '1CY'
                elif detail.age_type == cy2:
                    detail.age = '2CY'
                elif detail.age_type == cy3:
                    detail.age = '3CY'
                elif detail.age_type == cy4:
                    detail.age = '4CY'
                else:
                    detail.age = ''
                detail.save()

            orm['checklists.Age'].objects.all().delete()

            # restore sex
            male = orm['checklists.Sex'].objects.get(code='M')
            female = orm['checklists.Sex'].objects.get(code='F')

            for detail in orm['checklists.Detail'].objects.all():
                if detail.sex_type == male:
                    detail.sex = 'M'
                elif detail.sex_type == female:
                    species.sex = 'F'
                else:
                    species.sex = ''
                detail.save()

            orm['checklists.Sex'].objects.all().delete()

            # restore plumage
            blue = orm['checklists.Plumage'].objects.get(code='BPH')
            dark = orm['checklists.Plumage'].objects.get(code='DPH')
            light = orm['checklists.Plumage'].objects.get(code='LPH')
            mel = orm['checklists.Plumage'].objects.get(code='MEL')
            leu = orm['checklists.Plumage'].objects.get(code='LEU')
            alb = orm['checklists.Plumage'].objects.get(code='ALB')

            for detail in orm['checklists.Detail'].objects.all():
                if detail.plumage_type == blue:
                    detail.plumage = 'BPH'
                elif detail.plumage_type == dark:
                    detail.plumage = 'DPH'
                elif detail.plumage_type == light:
                    detail.plumage = 'LPH'
                elif detail.plumage_type == mel:
                    detail.plumage = 'MEL'
                elif detail.plumage_type == leu:
                    detail.plumage = 'LEU'
                elif detail.plumage_type == alb:
                    detail.plumage = 'ALB'
                else:
                    detail.plumage_type = ''
                detail.save()

            orm['checklists.Plumage'].objects.all().delete()

            # restore direction
            n = orm['checklists.Direction'].objects.get(code='N')
            ne = orm['checklists.Direction'].objects.get(code='NE')
            e = orm['checklists.Direction'].objects.get(code='E')
            se = orm['checklists.Direction'].objects.get(code='SE')
            s = orm['checklists.Direction'].objects.get(code='S')
            sw = orm['checklists.Direction'].objects.get(code='SW')
            w = orm['checklists.Direction'].objects.get(code='W')
            nw = orm['checklists.Direction'].objects.get(code='NW')

            for detail in orm['checklists.Detail'].objects.all():
                if detail.direction_type == n:
                    detail.direction = 'N'
                elif detail.direction_type == ne:
                    detail.direction = 'NE'
                elif detail.direction_type == e:
                    detail.direction = 'E'
                elif detail.direction_type == se:
                    detail.direction = 'SE'
                elif detail.direction_type == s:
                    detail.direction = 'S'
                elif detail.direction_type == sw:
                    detail.direction = 'SW'
                elif detail.direction_type == w:
                    detail.direction = 'W'
                elif detail.direction_type == nw:
                    detail.direction = 'NW'
                else:
                    detail.direction_type = ''
                detail.save()

            orm['checklists.Direction'].objects.all().delete()

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
            'age': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'age_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Age']", 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'direction_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Direction']", 'null': 'True', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['checklists.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'plumage': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'plumage_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['checklists.Plumage']", 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
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
            'rank': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
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
    symmetrical = True


from ..utils import i18n_migration

i18n_migration(Migration)
