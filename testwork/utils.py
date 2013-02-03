# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.db import models, connection
from django.db.models.loading import cache
from django.core.urlresolvers import clear_url_caches
from django.utils.importlib import import_module
from south.db import db

ftypes = {'char':'CharField', 'int':'IntegerField', 'str':'TextField'}
params= {
    'CharField':{'max_length':'255','blank':'True','null':'True'},
    'IntegerField':{'null':'True','blank':'True'},
    'TextField':{'null':'True','blank':'True'}
    }

def make_dynamic_model(name, val):
    """
    Make Dynamic Class
    """
    name = name
    _app_label = 'Dynamic'

    try:
        del cache.app_models[_app_label][name.lower()]
    except KeyError:
        pass

    class Meta:
        app_label = _app_label
        verbose_name = val['title']

    # Collect the dynamic model's class attributes
    attrs = {
        '__module__' : __name__,
        '__unicode__': lambda s: '%s dynamic' % name,
        'Meta'       :Meta
    }

    # Make object with "name"
    model = type(name, (models.Model,), attrs)

    fields = val['fields']
    # Add a fields to model
    for field in fields :
        field_type=ftypes[field['type']]
        param = params[field_type]
        verbose = {'verbose_name': field['title']}
        param.update(verbose)
        model.add_to_class(field['id'], getattr(models, field_type)(**param))

    # Create database for model if not exist.
    create_db_table(model)
    # Add fields to database
    add_necessary_db_columns(model)
    # Reregister the model in the admin
    reregister_in_admin(admin.site, model)

def create_db_table(model_class):
    """ Takes a Django model class and create a database table, if necessary.
    """

    db.start_transaction()
    table_name = model_class._meta.db_table

    # Introspect the database to see if it doesn't already exist
    if (connection.introspection.table_name_converter(table_name)
        not in connection.introspection.table_names()):

        fields = _get_fields(model_class)

        try:
            db.create_table(table_name, fields)
        except :
            pass
        # Some fields are added differently, after table creation
        db.execute_deferred_sql()

    db.commit_transaction()

def reload_url():
    # Reload the URL conf and clear the URL cache
    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()


def reregister_in_admin(admin_site, model, admin_class=None):
    # (re)registers a dynamic model in the given admin site
    unregister_from_admin(admin_site, model)
    admin_site.register(model, admin_class)
    reload_url()

def unregister_from_admin(admin_site, model):
    # Removes the dynamic model from the given admin site
    for reg_model in admin_site._registry.keys():
        if model._meta.db_table == reg_model._meta.db_table:
            del admin_site._registry[reg_model]

    # Try the normal approach too
    try:
        admin_site.unregister(model)
    except NotRegistered:
        pass

    reload_url()

def _get_fields(model_class):
    """ Return a list of fields that require table columns. """
    return [(f.name, f) for f in model_class._meta.local_fields]


def add_necessary_db_columns(model_class):
    """ Creates new table or relevant columns as necessary based on the model_class.
        No columns or data are renamed or removed.
        This is available in case a database exception occurs.
    """
    db.start_transaction()

    # Add field columns if missing
    table_name = model_class._meta.db_table
    fields = _get_fields(model_class)
    db_column_names = [row[0] for row in connection.introspection.get_table_description(connection.cursor(), table_name)]

    for field_name, field in fields:
        if field.column not in db_column_names:
            db.add_column(table_name, field_name, field)

    # Some columns require deferred SQL to be run. This was collected
    # when running db.add_column().
    db.execute_deferred_sql()

    db.commit_transaction()
