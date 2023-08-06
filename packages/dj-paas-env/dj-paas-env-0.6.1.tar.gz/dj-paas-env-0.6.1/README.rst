===========
dj-paas-env
===========

.. image:: https://travis-ci.org/pbacterio/dj-paas-env.png?branch=master
   :target: https://travis-ci.org/pbacterio/dj-paas-env

Helper methods to configure Django database and static files in a PAAS environment.
The platforms currently supported are: Heroko, OpenShift, dotCloud and Gondor


--------
Database
--------

Basic example
=============

In ``settings.py``::

    DATABASES = {
        'default': dj_paas_env.database.config()
    }

This example tries to figure out the database configuration from the following environment variables:
``DATABASE_URL``, ``HEROKU_POSTGRESQL_<color>_URL``, ``CLEARDB_DATABASE_URL``, ``OPENSHIFT_POSTGRESQL_DB_URL``,
``OPENSHIFT_MYSQL_DB_URL``, ``GONDOR_DATABASE_URL`` and dotcloud environment file.

Local database
==============

For develop/testing in local environments, it's recomend to use a default configuration. With this option the
application works in local and remote (PAAS) environments::

    DATABASES = {
        'default': dj_paas_env.database.config(default='mysql://user@pass:localhost/testdb')
    }


Develop with SQLite
===================

::

    DATABASES = {
        'default': dj_paas_env.database.sqlite_dev()
    }


-----------------------
PAAS provider detection
-----------------------

The method ``dj_paas_env.provider.detect()`` returns the provider name (heroku, openshift, dotcloud, gondor) where the
application is running::

    >>> import dj_paas_env
    >>> dj_paas_env.provider.detect()
    'openshift'


