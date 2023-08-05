# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserAccount'
        db.create_table(u'homebanking_useraccount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('remote_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'homebanking', ['UserAccount'])

        # Adding model 'Agreement'
        db.create_table(u'homebanking_agreement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['homebanking.UserAccount'])),
            ('remote_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'homebanking', ['Agreement'])

        # Adding model 'Account'
        db.create_table(u'homebanking_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('regnr', self.gf('django.db.models.fields.IntegerField')()),
            ('accountnr', self.gf('django.db.models.fields.IntegerField')()),
            ('agreement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['homebanking.Agreement'])),
        ))
        db.send_create_signal(u'homebanking', ['Account'])

        # Adding model 'Category'
        db.create_table(u'homebanking_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'homebanking', ['Category'])

        # Adding model 'Entry'
        db.create_table(u'homebanking_entry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('balance', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('subindex', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['homebanking.Account'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['homebanking.Category'])),
        ))
        db.send_create_signal(u'homebanking', ['Entry'])

        # Adding model 'CategoryMatcher'
        db.create_table(u'homebanking_categorymatcher', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['homebanking.Category'])),
            ('regex', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'homebanking', ['CategoryMatcher'])


    def backwards(self, orm):
        # Deleting model 'UserAccount'
        db.delete_table(u'homebanking_useraccount')

        # Deleting model 'Agreement'
        db.delete_table(u'homebanking_agreement')

        # Deleting model 'Account'
        db.delete_table(u'homebanking_account')

        # Deleting model 'Category'
        db.delete_table(u'homebanking_category')

        # Deleting model 'Entry'
        db.delete_table(u'homebanking_entry')

        # Deleting model 'CategoryMatcher'
        db.delete_table(u'homebanking_categorymatcher')


    models = {
        u'homebanking.account': {
            'Meta': {'object_name': 'Account'},
            'accountnr': ('django.db.models.fields.IntegerField', [], {}),
            'agreement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['homebanking.Agreement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'regnr': ('django.db.models.fields.IntegerField', [], {})
        },
        u'homebanking.agreement': {
            'Meta': {'object_name': 'Agreement'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['homebanking.UserAccount']"}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'homebanking.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'homebanking.categorymatcher': {
            'Meta': {'ordering': "('order',)", 'object_name': 'CategoryMatcher'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['homebanking.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'regex': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'homebanking.entry': {
            'Meta': {'object_name': 'Entry'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['homebanking.Account']"}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'balance': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['homebanking.Category']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subindex': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'homebanking.useraccount': {
            'Meta': {'object_name': 'UserAccount'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['homebanking']