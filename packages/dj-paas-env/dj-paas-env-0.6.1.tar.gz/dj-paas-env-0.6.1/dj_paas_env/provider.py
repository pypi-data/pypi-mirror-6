import os

HEROKU = 'heroku'
OPENSHIFT = 'openshift'
DOTCLOUD = 'dotcloud'
GONDOR = 'gondor'
UNKNOWN = 'unknown'


def detect():
    if 'DYNO' in os.environ:
        return HEROKU
    if os.path.isfile('/home/dotcloud/environment.json'):
        return DOTCLOUD
    for varname in os.environ:
        if varname.startswith('OPENSHIFT_'):
            return OPENSHIFT
        if varname.startswith('GONDOR_'):
            return GONDOR
    return UNKNOWN
