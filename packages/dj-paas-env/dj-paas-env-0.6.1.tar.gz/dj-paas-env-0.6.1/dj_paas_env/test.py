import os
import sys
import re

if sys.hexversion < 0x2070000:
    import unittest2 as unittest
else:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from dj_paas_env import database, provider, static


class TestDatabaseParse(unittest.TestCase):

    def test_parse_postgres_heroku(self):
        url = 'postgres://hleulxsesqdumt:vULaPXW9n4eGKK64d2_ujxLqGG@' + \
              'ec2-107-20-214-225.compute-1.amazonaws.com:5432/dcj1n178peejs9'
        parsed = database.parse(url)
        parsed_expect = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'dcj1n178peejs9',
            'USER': 'hleulxsesqdumt',
            'PASSWORD': 'vULaPXW9n4eGKK64d2_ujxLqGG',
            'HOST': 'ec2-107-20-214-225.compute-1.amazonaws.com',
            'PORT': 5432
        }
        self.assertDictEqual(parsed, parsed_expect)

    def test_parse_postgres_openshift(self):
        url = 'postgresql://ad_mingpxxnxy:ca5Dp1_yFet3@127.11.207.130:5432'
        parsed = database.parse(url)
        parsed_expect = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '',
            'USER': 'ad_mingpxxnxy',
            'PASSWORD': 'ca5Dp1_yFet3',
            'HOST': '127.11.207.130',
            'PORT': 5432
        }
        self.assertDictEqual(parsed, parsed_expect)

    def test_parse_postgres_dotcloud(self):
        url = 'pgsql://root:cR4zYr0o7pa5Sw0rD@abcd1234.dotcloud.com:1337'
        parsed = database.parse(url)
        parsed_expect = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '',
            'USER': 'root',
            'PASSWORD': 'cR4zYr0o7pa5Sw0rD',
            'HOST': 'abcd1234.dotcloud.com',
            'PORT': 1337
        }
        self.assertDictEqual(parsed, parsed_expect)

    def test_parse_mysql_heroku(self):
        url = 'mysql://b819c071b951a9:9ca7bbbb@us-cdbr-east-05.cleardb.net/heroku_ec5fddc308fbe9e?reconnect=true'
        parsed = database.parse(url)
        parsed_expect = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'heroku_ec5fddc308fbe9e',
            'USER': 'b819c071b951a9',
            'PASSWORD': '9ca7bbbb',
            'HOST': 'us-cdbr-east-05.cleardb.net',
            'PORT': ''
        }
        self.assertDictEqual(parsed, parsed_expect)

    def test_parse_mysql_openshift(self):
        url = 'mysql://admingJmQ37x:MDQ22l6xf1P-@127.11.207.130:3306/'
        parsed = database.parse(url)
        self.assertDictEqual(parsed, {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '',
            'USER': 'admingJmQ37x',
            'PASSWORD': 'MDQ22l6xf1P-',
            'HOST': '127.11.207.130',
            'PORT': 3306
        })

    def test_engine(self):
        url = 'scheme://user:pass@host:123/name'
        parsed = database.parse(url, engine='X')
        self.assertDictEqual(parsed, {
            'ENGINE': 'X',
            'NAME': 'name',
            'USER': 'user',
            'PASSWORD': 'pass',
            'HOST': 'host',
            'PORT': 123
        })

    def test_parse_sqlite(self):
        url = 'sqlite:///directory/file.db'
        parsed = database.parse(url)
        self.assertDictEqual(parsed, {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'directory/file.db',
            'USER': '',
            'PASSWORD': '',
            'HOST': None,
            'PORT': '',
        })

    def test_parse_sqlite_in_memory(self):
        url = 'sqlite://:memory:'
        parsed = database.parse(url)
        self.assertDictEqual(parsed, {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        })
        url = 'sqlite://'
        parsed = database.parse(url)
        self.assertDictEqual(parsed, {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        })


class SafeEnvironmentTestCase(unittest.TestCase):

    clean_vars = database.re_keys + [
        'DYNO',
        re.compile(r'OPENSHIFT_.+'),
        re.compile(r'GONDOR_.+'),
        'OPENSHIFT_APP_NAME',
        'PGDATABASE'
    ]

    def setUp(self):
        self.env_copy = os.environ.copy()
        for clean_var in self.clean_vars:
            if isinstance(clean_var, str):
                if clean_var in self.env_copy:
                    os.environ.pod(clean_var, None)
                break
            for key in self.env_copy:
                if clean_var.match(key):
                    os.environ.pop(key, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_copy)
        self.env_copy = None


class TestDatabaseConfig(SafeEnvironmentTestCase):

    def test_config_heroku_promoted(self):
        os.environ['DATABASE_URL'] = 'postgres://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'rewq',
            'USER': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_heroku_postgres(self):
        os.environ['HEROKU_POSTGRESQL_BLACK_URL'] = 'postgres://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'rewq',
            'USER': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_heroku_mysql(self):
        os.environ['CLEARDB_DATABASE_URL'] = 'mysql://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'rewq',
            'USER': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_openshift_postgres(self):
        os.environ['OPENSHIFT_POSTGRESQL_DB_URL'] = 'postgresql://asdf:fdsa@qwer:12345'
        os.environ['PGDATABASE'] = 'rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'rewq',
            'USER': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_openshift_mysql(self):
        os.environ['OPENSHIFT_MYSQL_DB_URL'] = 'mysql://asdf:fdsa@qwer:12345/rewq'
        os.environ['OPENSHIFT_APP_NAME'] = 'rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'rewq',
            'USER': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_gondor(self):
        os.environ['GONDOR_DATABASE_URL'] = 'postgres://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'rewq',
            'USER': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    @patch('dj_paas_env.database.parse')
    def test_config_default(self, mock):
        database.config(default='bbbb')
        mock.assert_called_with('bbbb', None)

    @patch('dj_paas_env.database.parse')
    def test_config_engine(self, mock):
        os.environ['DATABASE_URL'] = 'postgres://asdf:fdsa@qwer:12345/rewq'
        database.config(engine='xxxx')
        mock.assert_called_with('postgres://asdf:fdsa@qwer:12345/rewq', 'xxxx')


class TestDatabaseSqlitedev(SafeEnvironmentTestCase):

    def test_sqlitedev_openshift(self):
        os.environ['OPENSHIFT_DATA_DIR'] = 'qwerty'
        self.assertEqual(database.sqlite_dev(), 'sqlite:///' + os.path.join(
            'qwerty', 'database.sqlite3'))

    def test_sqlitedev_gondor(self):
        os.environ['GONDOR_DATA_DIR'] = 'asdf'
        self.assertEqual(database.sqlite_dev(), 'sqlite:///' + os.path.join(
            'asdf', 'database.sqlite3'))

    @patch('os.path.isfile', return_value=True)
    def test_sqlitedev_dotcloud(self, mock):
        self.assertEqual(database.sqlite_dev(), 'sqlite:///' + os.path.join(
            os.path.expanduser('~/data'), 'database.sqlite3'))


class TestDatabaseDatadir(SafeEnvironmentTestCase):

    def test_datadir_openshift(self):
        os.environ['OPENSHIFT_DATA_DIR'] = 'qwerty'
        self.assertEqual(database.data_dir(), 'qwerty')

    def test_datadir_gondor(self):
        os.environ['GONDOR_DATA_DIR'] = 'asdf'
        self.assertEqual(database.data_dir(), 'asdf')

    @patch('os.path.isfile', return_value=True)
    def test_datadir_dotcloud(self, mock):
        self.assertEqual(database.data_dir(), os.path.expanduser('~/data'))

    def test_datadir_default(self):
        self.assertEqual(database.data_dir(), 'data')


class TestStaticRoot(SafeEnvironmentTestCase):

    @patch('dj_paas_env.provider.detect', return_value=provider.HEROKU)
    def test_root_heroku(self, mock):
        self.assertEqual(static.root(), 'staticfiles')

    @patch('dj_paas_env.provider.detect', return_value=provider.OPENSHIFT)
    def test_root_openshift(self, mock):
        self.assertEqual(static.root(), 'wsgi/static')

    @patch('dj_paas_env.provider.detect', return_value=provider.GONDOR)
    def test_root_gondor(self, mock):
        os.environ['GONDOR_DATA_DIR'] = 'zxcvb'
        self.assertEqual(static.root(), os.path.join('zxcvb', 'site_media',
                                                     'static'))

    @patch('dj_paas_env.provider.detect', return_value=provider.DOTCLOUD)
    def test_root_dotcloud(self, mock):
        self.assertEqual(static.root(), '/home/dotcloud/volatile/static/')

    @patch('dj_paas_env.provider.detect', return_value=provider.UNKNOWN)
    def test_root_unknown(self, mock):
        self.assertEqual(static.root(), 'wsgi/static')


class TestProviderDetect(SafeEnvironmentTestCase):

    def test_detect_heroku(self):
        os.environ['DYNO'] = ''
        self.assertEqual(provider.detect(), 'heroku')

    def test_detect_openshift(self):
        os.environ['OPENSHIFT_xxx'] = ''
        self.assertEqual(provider.detect(), 'openshift')

    @patch('os.path.isfile', return_value=True)
    def test_detect_dotcloud(self, mock):
        self.assertEqual(provider.detect(), 'dotcloud')
        mock.assert_called_with('/home/dotcloud/environment.json')

    def test_detect_gondor(self):
        os.environ['GONDOR_xxx'] = ''
        self.assertEqual(provider.detect(), 'gondor')

    def test_detect_unknown(self):
        self.assertEqual(provider.detect(), 'unknown')


def suite():
    test_suite = unittest.TestSuite()
    tests = unittest.defaultTestLoader.loadTestsFromName(__name__)
    test_suite.addTests(tests)
    return test_suite

if __name__ == '__main__':
    unittest.main()
