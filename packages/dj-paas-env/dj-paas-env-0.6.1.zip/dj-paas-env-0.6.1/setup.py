# coding=utf-8
from setuptools import setup
import os.path
import codecs
import sys


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()

test_require = []
if sys.hexversion < 0x2070000:
    test_require.append('unittest2')
if sys.hexversion < 0x3030000:
    test_require.append(['mock'])


setup(
    name='dj-paas-env',
    description='Helper methods to configure Django database and static files in a PAAS environment.',
    long_description=read('README.rst'),
    version='0.6.1',
    packages=['dj_paas_env'],
    url='https://github.com/pbacterio/dj-paas-env',
    license='MIT',
    author='Germán Moya',
    author_email='pbacterio@gmail.com',
    test_suite='dj_paas_env.test.suite',
    tests_require=test_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
