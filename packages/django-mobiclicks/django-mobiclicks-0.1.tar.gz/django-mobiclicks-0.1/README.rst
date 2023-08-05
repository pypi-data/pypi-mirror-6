django-mobiclicks v.0.1
=======================

Requirements
------------
If a custom user model is used, it needs to have a datetime ``date_joined`` field. This is used to determine if a user is new or not. Check setup.py for other requirements.

Settings
--------
- ``CPA_TOKEN_PARAMETER_NAME``: the name of the querystring parameter that contains the CPA token. Default is 'cpa'.
- ``CPA_TOKEN_SESSION_KEY``: the name of the Django session key used to store the CPA token. Default is 'mobiclicks_cpatoken'.
- ``CPA_SECURITY_TOKEN``: the security token provided by MobiClicks. This setting is required.
- ``CLICK_REF_PARAMETER_NAME``: the name of the querystring parameter that contains the click ref value. Default is 'pollen8_click_ref'.
- ``ACQUISITION_TRACKING_URL``: the MobiClicks URL that acquisitions are posted to. Default is 'http://t.mobiclicksdirect.com/acquisition'.
- ``CLICK_CONFIRMATION_URL``: the MobiClicks URL that click confirmation is posted to. Default is 'http://t.mobiclicksdirect.com/advertiser'.
- ``TRACK_REGISTRATIONS``: track registration conversions via MobiClicks. Default is 'True'.
- ``CONFIRM_CLICKS``: track a user landing on the site from an ad via MobiClicks. Default is 'True'.
