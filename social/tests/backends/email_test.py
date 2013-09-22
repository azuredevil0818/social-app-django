import requests

from sure import expect
from httpretty import HTTPretty

from social.utils import module_member
from social.backends.utils import load_backends
from social.tests.base import BaseBackendTest
from social.tests.strategy import TestStrategy
from social.tests.models import TestStorage, User, TestUserSocialAuth, \
                                TestNonce, TestAssociation


FORM = """
<form method="post" action="/complete/email">
    <input name="email" type="text">
    <button>Submit</button>
</form>
"""
FORM_CT = 'application/x-www-form-urlencoded'


class EmailTest(BaseBackendTest):
    backend_path = 'social.backends.email.EmailAuth'
    expected_username = 'foo'

    def setUp(self):
        HTTPretty.enable()
        self.backend = module_member(self.backend_path)
        self.strategy = TestStrategy(self.backend, TestStorage)
        name = self.backend.name
        name = name.upper().replace('-', '_')
        self.strategy.set_settings({
            'SOCIAL_AUTH_EMAIL_FORM_URL': '/login/email',
            'SOCIAL_AUTH_AUTHENTICATION_BACKENDS': (
                self.backend_path,
                'social.tests.backends.broken_test.BrokenBackendAuth'
            )
        })
        # Force backends loading to trash PSA cache
        load_backends(
            self.strategy.get_setting('SOCIAL_AUTH_AUTHENTICATION_BACKENDS'),
            force_load=True
        )

    def tearDown(self):
        self.strategy = None
        self.backend = None
        User.reset_cache()
        TestUserSocialAuth.reset_cache()
        TestNonce.reset_cache()
        TestAssociation.reset_cache()
        HTTPretty.disable()

    def do_start(self):
        start_url = self.strategy.start().url
        start_url = self.strategy.build_absolute_uri(start_url)
        complete_url = self.strategy.build_absolute_uri('/complete/email')

        HTTPretty.register_uri(HTTPretty.GET, start_url, status=200, body=FORM)
        HTTPretty.register_uri(HTTPretty.POST, complete_url, status=200,
                               body='email=foo@bar.com', content_type=FORM_CT)
        response = requests.get(start_url)
        expect(response.text).to.equal(FORM)
        response = requests.post(complete_url, data={'email': 'foo@bar.com'})
        self.strategy.set_request_data({'email': 'foo@bar.com'})
        return self.strategy.complete()

    def test_login(self):
        self.do_login()

    def test_partial_pipeline(self):
        self.do_partial_pipeline()
