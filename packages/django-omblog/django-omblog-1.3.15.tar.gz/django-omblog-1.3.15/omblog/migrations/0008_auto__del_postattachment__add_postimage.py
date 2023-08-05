# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'PostAttachment'
        db.delete_table('omblog_postattachment')

        # Adding model 'PostImage'
        db.create_table('omblog_postimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omblog.Post'])),
            ('src', self.gf('omblog.fields.ImageWithThumbsField')(null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('omblog', ['PostImage'])


    def backwards(self, orm):
        # Adding model 'PostAttachment'
        db.create_table('omblog_postattachment', (
            ('src', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('image', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omblog.Post'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('omblog', ['PostAttachment'])

        # Deleting model 'PostImage'
        db.delete_table('omblog_postimage')


    models = {
        'omblog.post': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Post'},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rendered_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'source_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '4'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['omblog.Tag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'omblog.postimage': {
            'Meta': {'object_name': 'PostImage'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omblog.Post']"}),
            'src': ('omblog.fields.ImageWithThumbsField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'omblog.postversion': {
            'Meta': {'ordering': "['-created']", 'object_name': 'PostVersion'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('picklefield.fields.PickledObjectField', [], {})
        },
        'omblog.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['omblog']