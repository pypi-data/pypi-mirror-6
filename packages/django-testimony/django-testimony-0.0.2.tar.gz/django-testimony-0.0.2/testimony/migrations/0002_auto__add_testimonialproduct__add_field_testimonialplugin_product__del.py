# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TestimonialProduct'
        db.create_table(u'testimony_testimonialproduct', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'testimony', ['TestimonialProduct'])

        # Adding field 'TestimonialPlugin.product'
        db.add_column(u'cmsplugin_testimonialplugin', 'product',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testimony.TestimonialProduct'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Testimonial.company'
        db.delete_column(u'testimony_testimonial', 'company')

        # Deleting field 'Testimonial.position'
        db.delete_column(u'testimony_testimonial', 'position')

        # Adding field 'Testimonial.product'
        db.add_column(u'testimony_testimonial', 'product',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testimony.TestimonialProduct'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'TestimonialProduct'
        db.delete_table(u'testimony_testimonialproduct')

        # Deleting field 'TestimonialPlugin.product'
        db.delete_column(u'cmsplugin_testimonialplugin', 'product_id')


        # User chose to not deal with backwards NULL issues for 'Testimonial.company'
        raise RuntimeError("Cannot reverse this migration. 'Testimonial.company' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Testimonial.company'
        db.add_column(u'testimony_testimonial', 'company',
                      self.gf('django.db.models.fields.CharField')(max_length=100),
                      keep_default=False)

        # Adding field 'Testimonial.position'
        db.add_column(u'testimony_testimonial', 'position',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Testimonial.product'
        db.delete_column(u'testimony_testimonial', 'product_id')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'testimony.testimonial': {
            'Meta': {'ordering': "['author']", 'object_name': 'Testimonial'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['testimony.TestimonialProduct']", 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'testimony': ('django.db.models.fields.TextField', [], {})
        },
        u'testimony.testimonialplugin': {
            'Meta': {'object_name': 'TestimonialPlugin', 'db_table': "u'cmsplugin_testimonialplugin'", '_ormbases': ['cms.CMSPlugin']},
            'block': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'list_type': ('django.db.models.fields.CharField', [], {'default': "'random'", 'max_length': '10'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['testimony.TestimonialProduct']", 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'template_path': ('django.db.models.fields.CharField', [], {'default': "('testimony/list_default.html', 'Default list (stationary)')", 'max_length': '100'})
        },
        u'testimony.testimonialproduct': {
            'Meta': {'ordering': "['name']", 'object_name': 'TestimonialProduct'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['testimony']