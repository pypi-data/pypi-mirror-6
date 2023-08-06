import os
from dj_paas_env import provider

def root():
    paas_prov = provider.detect()
    if paas_prov == provider.HEROKU:
        return 'staticfiles'
    if paas_prov == provider.GONDOR:
        return os.path.join(os.environ['GONDOR_DATA_DIR'], 'site_media',
                            'static')
    if paas_prov == provider.DOTCLOUD:
        return '/home/dotcloud/volatile/static/'
    return 'wsgi/static'
