__all__ = ('config', 'parse', 'ENGINES', 'data_dir')

import os
import re
import json

try:
    from urllib.parse import urlparse  # Python 3
except ImportError:
    from urlparse import urlparse  # Python 2

from dj_paas_env import provider

ENGINES = {
    'postgres': 'django.db.backends.postgresql_psycopg2',
    'postgresql': 'django.db.backends.postgresql_psycopg2',
    'pgsql': 'django.db.backends.postgresql_psycopg2',
    'mysql': 'django.db.backends.mysql',
    'sqlite': 'django.db.backends.sqlite3',
}

re_keys = [r'.*DATABASE_URL', r'HEROKU_POSTGRESQL_.+_URL',
           r'OPENSHIFT_.+_DB_URL', 'DOTCLOUD_.+_.*SQL_URL']
re_keys = list(map(re.compile, re_keys))


def config(default=None, engine=None):
    provider_detected = provider.detect()
    url = None
    if provider_detected == provider.DOTCLOUD:
        with open('/home/dotcloud/environment.json', 'r') as f:
            os.environ.update(json.load(f))
    for key in os.environ:
        for re_key in re_keys:
            if re_key.match(key):
                url = os.environ[key]
                break
    if not url:
        return parse(default, engine)
    conf = parse(url, engine)
    if provider_detected == provider.OPENSHIFT:
        if 'OPENSHIFT_POSTGRESQL_DB_URL' in os.environ:
            conf['NAME'] = os.environ['PGDATABASE']
        elif 'OPENSHIFT_MYSQL_DB_URL' in os.environ:
            conf['NAME'] = os.environ['OPENSHIFT_APP_NAME']
    return conf


def parse(url, engine=None):
    if url in ('sqlite://:memory:', 'sqlite://'):
        return {
            'ENGINE': ENGINES['sqlite'],
            'NAME': ':memory:'
        }
    url = urlparse(url)
    return {
        'ENGINE': engine if engine else ENGINES[url.scheme],
        'NAME': url.path[1:].split('?', 2)[0],
        'USER': url.username or '',
        'PASSWORD': url.password or '',
        'HOST': url.hostname,
        'PORT': url.port or ''
    }


def sqlite_dev():
    return 'sqlite:///' + os.path.join(data_dir(), 'database.sqlite3')


def data_dir(default='data'):
    """
    Return persistent data directory or ``default`` if not found
    Warning: Do not use this directory to store sqlite databases in producction
    """
    if 'OPENSHIFT_DATA_DIR' in os.environ:
        return os.environ['OPENSHIFT_DATA_DIR']
    if 'GONDOR_DATA_DIR' in os.environ:
        return os.environ['GONDOR_DATA_DIR']
    if provider.detect() == provider.DOTCLOUD:
        return os.path.expanduser('~/data')
    return default
