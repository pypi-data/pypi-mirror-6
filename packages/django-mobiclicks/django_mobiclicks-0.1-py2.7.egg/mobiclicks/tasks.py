import requests
from celery import task

from mobiclicks import conf


@task()
def confirm_click(click_ref):
    requests.get(conf.CLICK_CONFIRMATION_URL,
                 params={'action': 'clickReceived',
                         'authKey': conf.CPA_SECURITY_TOKEN,
                         'clickRef': click_ref})


@task()
def track_registration_acquisition(cpa_token):
    requests.get(conf.ACQUISITION_TRACKING_URL,
                 params={'cpakey': conf.CPA_SECURITY_TOKEN,
                         'code': cpa_token})
