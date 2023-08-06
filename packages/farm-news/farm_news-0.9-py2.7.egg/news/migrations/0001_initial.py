# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'news_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('news', ['Category'])

        # Adding model 'Article'
        db.create_table(u'news_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='articles', to=orm['news.Category'])),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('publish', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publish_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('news', ['Article'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'news_category')

        # Deleting model 'Article'
        db.delete_table(u'news_article')


    models = {
        'news.article': {
            'Meta': {'ordering': "['-publish_on']", 'object_name': 'Article'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles'", 'to': "orm['news.Category']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {})
        },
        'news.category': {
            'Meta': {'ordering': "['order', 'title']", 'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['news']