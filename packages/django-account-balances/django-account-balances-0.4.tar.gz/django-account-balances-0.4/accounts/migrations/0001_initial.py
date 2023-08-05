# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

try:
    from oscar.core.compat import AUTH_USER_MODEL, AUTH_USER_MODEL_NAME
except ImportError:
    AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
    try:
        AUTH_USER_APP_LABEL, AUTH_USER_MODEL_NAME = AUTH_USER_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AccountType'
        db.create_table(u'accounts_accounttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('depth', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('numchild', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'accounts', ['AccountType'])

        # Adding model 'Account'
        db.create_table(u'accounts_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('account_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='accounts', null=True, to=orm['accounts.AccountType'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True, blank=True)),
            ('primary_user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='accounts', null=True, on_delete=models.SET_NULL, to=orm[AUTH_USER_MODEL])),
            ('status', self.gf('django.db.models.fields.CharField')(default='Open', max_length=32)),
            ('credit_limit', self.gf('django.db.models.fields.DecimalField')(default='0.00', null=True, max_digits=12, decimal_places=2, blank=True)),
            ('balance', self.gf('django.db.models.fields.DecimalField')(default='0.00', null=True, max_digits=12, decimal_places=2)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('can_be_used_for_non_products', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['Account'])

        # Adding model 'Transfer'
        db.create_table(u'accounts_transfer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=64, unique=True, null=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='source_transfers', to=orm['accounts.Account'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(related_name='destination_transfers', to=orm['accounts.Account'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related_transfers', null=True, to=orm['accounts.Transfer'])),
            ('merchant_reference', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfers', null=True, on_delete=models.SET_NULL, to=orm[AUTH_USER_MODEL])),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['Transfer'])

        # Adding model 'Transaction'
        db.create_table(u'accounts_transaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transfer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['accounts.Transfer'])),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['accounts.Account'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['Transaction'])

        # Adding unique constraint on 'Transaction', fields ['transfer', 'account']
        db.create_unique(u'accounts_transaction', ['transfer_id', 'account_id'])

        # Adding model 'IPAddressRecord'
        db.create_table(u'accounts_ipaddressrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15)),
            ('total_failures', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('consecutive_failures', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_last_failure', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'accounts', ['IPAddressRecord'])

        # Adding model 'AccountSecondaryUsers'
        db.create_table(u'accounts_accountsecondaryusers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Account'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[AUTH_USER_MODEL])),
        ))
        db.send_create_signal(u'accounts', ['AccountSecondaryUsers'])


    def backwards(self, orm):
        # Removing unique constraint on 'Transaction', fields ['transfer', 'account']
        db.delete_unique(u'accounts_transaction', ['transfer_id', 'account_id'])

        # Deleting model 'AccountType'
        db.delete_table(u'accounts_accounttype')

        # Deleting model 'Account'
        db.delete_table(u'accounts_account')

        # Deleting model 'Transfer'
        db.delete_table(u'accounts_transfer')

        # Deleting model 'Transaction'
        db.delete_table(u'accounts_transaction')

        # Deleting model 'IPAddressRecord'
        db.delete_table(u'accounts_ipaddressrecord')

        # Deleting model 'AccountSecondaryUsers'
        db.delete_table(u'accounts_accountsecondaryusers')


    models = {
        u'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'account_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accounts'", 'null': 'True', 'to': u"orm['accounts.AccountType']"}),
            'balance': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'can_be_used_for_non_products': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'credit_limit': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'primary_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'accounts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['{}']".format(AUTH_USER_MODEL)}),
            'secondary_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['{}']".format(AUTH_USER_MODEL), 'symmetrical': 'False', 'through': u"orm['accounts.AccountSecondaryUsers']", 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Open'", 'max_length': '32'})
        },
        u'accounts.accountsecondaryusers': {
            'Meta': {'object_name': 'AccountSecondaryUsers'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['{}']".format(AUTH_USER_MODEL)})
        },
        u'accounts.accounttype': {
            'Meta': {'object_name': 'AccountType'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'accounts.ipaddressrecord': {
            'Meta': {'object_name': 'IPAddressRecord'},
            'consecutive_failures': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_last_failure': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'total_failures': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'accounts.transaction': {
            'Meta': {'unique_together': "(('transfer', 'account'),)", 'object_name': 'Transaction'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['accounts.Account']"}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'transfer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['accounts.Transfer']"})
        },
        u'accounts.transfer': {
            'Meta': {'ordering': "('-date_created',)", 'object_name': 'Transfer'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'destination_transfers'", 'to': u"orm['accounts.Account']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_reference': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_transfers'", 'null': 'True', 'to': u"orm['accounts.Transfer']"}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '64', 'unique': 'True', 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_transfers'", 'to': u"orm['accounts.Account']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transfers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['{}']".format(AUTH_USER_MODEL)}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'django_facebook.facebookcustomuser': {
            'Meta': {'object_name': 'FacebookCustomUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['accounts']
