# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # for every status
        for category in orm['contact_form.ContactFormCategory'].objects.all():
            # iterate over the old renamed translation instances
            for categorytrans_old in orm['contact_form.ContactFormCategoryTranslationRenamed'].objects.filter(contact_form_category=category):
                orm['contact_form.ContactFormCategoryTranslation'].objects.create(
                    name=categorytrans_old.name,
                    language_code=categorytrans_old.language,
                    master=category,
                )

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'contact_form.contactformcategory': {
            'Meta': {'object_name': 'ContactFormCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256'})
        },
        u'contact_form.contactformcategorytranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ContactFormCategoryTranslation', 'db_table': "u'contact_form_contactformcategory_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['contact_form.ContactFormCategory']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'contact_form.contactformcategorytranslationrenamed': {
            'Meta': {'object_name': 'ContactFormCategoryTranslationRenamed'},
            'contact_form_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contact_form.ContactFormCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['contact_form']
    symmetrical = True
