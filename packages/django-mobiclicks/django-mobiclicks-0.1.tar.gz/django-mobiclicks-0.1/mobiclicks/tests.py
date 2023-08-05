from datetime import timedelta
from mock import patch
import unittest

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
try:
    from django.contrib.auth import get_user_model
except ImportError:  # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.http import HttpResponseNotFound
from django.middleware.locale import LocaleMiddleware
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.signals import setting_changed
from django.utils.importlib import import_module

from mobiclicks.middleware import MobiClicksMiddleware
from mobiclicks import conf
from mobiclicks import models


class CannotCreateCustomUser(unittest.SkipTest):
    pass


class RequestFactoryTestCase(TestCase):
    cpatoken = 'foo'

    def setUp(self):
        self.factory = RequestFactory()
        # set up a session
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.factory.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def make_request(self, url, method='get'):
        request = getattr(self.factory, method)(url)
        request.session = self.session
        return request


class MiddlewareTestCase(RequestFactoryTestCase):

    @classmethod
    def setUpClass(cls):
        super(MiddlewareTestCase, cls).setUpClass()
        cls.middleware = MobiClicksMiddleware()

    def test_store_token_default_settings(self):
        request = self.make_request('/?cpa=%s' % self.cpatoken)
        self.middleware.process_request(request)
        self.assertIn(conf.CPA_TOKEN_SESSION_KEY, self.session)
        self.assertEquals(self.session[conf.CPA_TOKEN_SESSION_KEY],
                          self.cpatoken)

    def test_store_token_custom_settings(self):
        with self.settings(MOBICLICKS={
            'CPA_TOKEN_SESSION_KEY': 'foo_session_key',
            'CPA_TOKEN_PARAMETER_NAME': 'foo_param_name',
            'CPA_SECURITY_TOKEN': 'foo'
        }):
            self.assertEqual(conf.CPA_TOKEN_SESSION_KEY, 'foo_session_key')
            self.assertEqual(conf.CPA_TOKEN_PARAMETER_NAME, 'foo_param_name')

            request = self.make_request('/?cpa=%s' % self.cpatoken)
            self.middleware.process_request(request)
            self.assertNotIn(conf.CPA_TOKEN_SESSION_KEY, self.session)

            request = self.make_request('/?foo_param_name=%s' % self.cpatoken)
            self.middleware.process_request(request)
            self.assertIn(conf.CPA_TOKEN_SESSION_KEY, self.session)
            self.assertEquals(self.session[conf.CPA_TOKEN_SESSION_KEY],
                              self.cpatoken)

    @patch('mobiclicks.tasks.requests.get')
    def test_click_confirmation(self, mock_get):
        click_ref = 'foo'
        with self.settings(MOBICLICKS={
            'CONFIRM_CLICKS': True,
            'CPA_SECURITY_TOKEN': 'foo'
        }):
            request = self.make_request('/?pollen8_click_ref=%s' % click_ref)
            self.middleware.process_request(request)
            mock_get.assert_called_once_with(
                conf.CLICK_CONFIRMATION_URL,
                params={
                    'action': 'clickReceived',
                    'clickRef': click_ref,
                    'authKey': conf.CPA_SECURITY_TOKEN,
                }
            )

        # click confirmation disabled
        with self.settings(MOBICLICKS={
            'CONFIRM_CLICKS': False,
            'CPA_SECURITY_TOKEN': 'foo'
        }):
            mock_get.reset()
            self.middleware.process_request(request)
            mock_get.assert_not_called()

    def test_click_confirmation_duplicate_on_redirect(self):
        with self.settings(
            MOBICLICKS={
                'CONFIRM_CLICKS': True,
                'CPA_SECURITY_TOKEN': 'foo'
            },
            LANGUAGES=(('en-us', 'English'),),
            ROOT_URLCONF=i18n_patterns('', url(r'', lambda r: r))
        ):
            qs_param_click = 'pollen8_click_ref=foo'
            qs_param_other = 'foo=foo'
            request = self.make_request('/?%s&%s' % (qs_param_click,
                                                     qs_param_other))
            locale_middleware = LocaleMiddleware()
            # activates language
            locale_middleware.process_request(request)
            # redirects for language
            response = locale_middleware.process_response(
                request,
                HttpResponseNotFound()
            )
            # should strip the pollen8_click_ref after
            # it has been tracked
            self.middleware.process_response(request, response)
            self.assertNotIn(qs_param_click, response['Location'])
            self.assertIn(qs_param_other, response['Location'])


class RegistrationTrackingTestCase(RequestFactoryTestCase):

    def setUp(self):
        super(RegistrationTrackingTestCase, self).setUp()
        self.session[conf.CPA_TOKEN_SESSION_KEY] = self.cpatoken

    def create_user(self, username='foo'):
        try:
            return User.objects.create_user(
                username,
                '%s@example.com' % username,
                'password'
            )
        except TypeError:
            # We cannot run this test if we don't know
            # how to create a user
            if settings.AUTH_USER_MODEL != 'auth.User':
                raise CannotCreateCustomUser
            raise

    @patch('mobiclicks.tasks.requests.get')
    def test_track_registration_on_login(self, mock_get):
        with self.settings(MOBICLICKS={
            'TRACK_REGISTRATIONS': True,
            'CPA_SECURITY_TOKEN': 'foo'
        }):
            request = self.make_request('/join/')
            # this can be a different user model but
            # it needs to have a 'date_joined' field
            user = self.create_user()
            user_logged_in.send(sender=User, user=user,
                                request=request)
            mock_get.assert_called_once_with(
                conf.ACQUISITION_TRACKING_URL,
                params={
                    'cpakey': conf.CPA_SECURITY_TOKEN,
                    'code': self.cpatoken,
                }
            )
            self.assertNotIn(conf.CPA_TOKEN_SESSION_KEY, self.session)

            # change date_joined so no longer a new user
            user.date_joined = user.date_joined - timedelta(days=1)
            user.save()
            self.session[conf.CPA_TOKEN_SESSION_KEY] = self.cpatoken
            mock_get.reset()
            user_logged_in.send(sender=User, user=user,
                                request=request)
            mock_get.assert_not_called()


@receiver(setting_changed)
def settings_changed_handler(sender, **kwargs):
    if kwargs['setting'] == 'MOBICLICKS':
        conf.init_configuration()
        reload(models)
