# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScraperRun'
        db.create_table(u'okscraper_django_scraperrun', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scraper_label', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'okscraper_django', ['ScraperRun'])

        # Adding M2M table for field logs on 'ScraperRun'
        m2m_table_name = db.shorten_name(u'okscraper_django_scraperrun_logs')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scraperrun', models.ForeignKey(orm[u'okscraper_django.scraperrun'], null=False)),
            ('scraperrunlog', models.ForeignKey(orm[u'okscraper_django.scraperrunlog'], null=False))
        ))
        db.create_unique(m2m_table_name, ['scraperrun_id', 'scraperrunlog_id'])

        # Adding model 'ScraperRunLog'
        db.create_table(u'okscraper_django_scraperrunlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'okscraper_django', ['ScraperRunLog'])


    def backwards(self, orm):
        # Deleting model 'ScraperRun'
        db.delete_table(u'okscraper_django_scraperrun')

        # Removing M2M table for field logs on 'ScraperRun'
        db.delete_table(db.shorten_name(u'okscraper_django_scraperrun_logs'))

        # Deleting model 'ScraperRunLog'
        db.delete_table(u'okscraper_django_scraperrunlog')


    models = {
        u'okscraper_django.scraperrun': {
            'Meta': {'object_name': 'ScraperRun'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logs': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['okscraper_django.ScraperRunLog']", 'symmetrical': 'False'}),
            'scraper_label': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'okscraper_django.scraperrunlog': {
            'Meta': {'object_name': 'ScraperRunLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['okscraper_django']