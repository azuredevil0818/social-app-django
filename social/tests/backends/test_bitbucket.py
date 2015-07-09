import json

from httpretty import HTTPretty

from social.p3 import urlencode
from social.exceptions import AuthForbidden
from social.tests.backends.oauth import OAuth1Test


class BitbucketOAuth1Test(OAuth1Test):
    backend_path = 'social.backends.bitbucket.BitbucketOAuth'
    user_data_url = 'https://api.bitbucket.org/2.0/user'
    expected_username = 'foobar'
    access_token_body = json.dumps({
        'access_token': 'foobar',
        'token_type': 'bearer'
    })
    request_token_body = urlencode({
        'oauth_token_secret': 'foobar-secret',
        'oauth_token': 'foobar',
        'oauth_callback_confirmed': 'true'
    })
    emails_body = json.dumps({
        u'page': 1,
        u'pagelen': 10,
        u'size': 2,
        u'values': [
            {
                u'email': u'foo@bar.com',
                u'is_confirmed': True,
                u'is_primary': True,
                u'links': { u'self': {u'href': u'https://api.bitbucket.org/2.0/user/emails/foo@bar.com'}},
                u'type': u'email'
            },
            {
                u'email': u'not@confirme.com',
                u'is_confirmed': False,
                u'is_primary': False,
                u'links': {u'self': {u'href': u'https://api.bitbucket.org/2.0/user/emails/not@confirmed.com'}},
                u'type': u'email'
            }
        ]
    })
    user_data_body = json.dumps({
        u'created_on': u'2012-03-29T18:07:38+00:00',
        u'display_name': u'Foo Bar',
        u'links': {
            u'avatar': {u'href': u'https://bitbucket.org/account/foobar/avatar/32/'},
            u'followers': {u'href': u'https://api.bitbucket.org/2.0/users/foobar/followers'},
            u'following': {u'href': u'https://api.bitbucket.org/2.0/users/foobar/following'},
            u'hooks': {u'href': u'https://api.bitbucket.org/2.0/users/foobar/hooks'},
            u'html': {u'href': u'https://bitbucket.org/foobar'},
            u'repositories': {u'href': u'https://api.bitbucket.org/2.0/repositories/foobar'},
            u'self': {u'href': u'https://api.bitbucket.org/2.0/users/foobar'}},
        u'location': u'Fooville, Bar',
        u'type': u'user',
        u'username': u'foobar',
        u'uuid': u'{397621dc-0f78-329f-8d6d-727396248e3f}',
        u'website': u'http://foobar.com'
    })

    def test_login(self):
        HTTPretty.register_uri(HTTPretty.GET,
                               'https://api.bitbucket.org/2.0/user/emails',
                               status=200, body=self.emails_body)
        self.do_login()

    def test_partial_pipeline(self):
        HTTPretty.register_uri(HTTPretty.GET,
                               'https://api.bitbucket.org/2.0/user/emails',
                               status=200, body=self.emails_body)
        self.do_partial_pipeline()


class BitbucketOAuth1FailTest(BitbucketOAuth1Test):
    emails_body = json.dumps({
        u'page': 1,
        u'pagelen': 10,
        u'size': 1,
        u'values': [
            {
                u'email': u'foo@bar.com',
                u'is_confirmed': False,
                u'is_primary': True,
                u'links': { u'self': {u'href': u'https://api.bitbucket.org/2.0/user/emails/foo@bar.com'}},
                u'type': u'email'
            }
        ]
    })

    def test_login(self):
        self.strategy.set_settings({
            'SOCIAL_AUTH_BITBUCKET_VERIFIED_EMAILS_ONLY': True
        })
        with self.assertRaises(AuthForbidden):
            super(BitbucketOAuth1FailTest, self).test_login()

    def test_partial_pipeline(self):
        self.strategy.set_settings({
            'SOCIAL_AUTH_BITBUCKET_VERIFIED_EMAILS_ONLY': True
        })
        with self.assertRaises(AuthForbidden):
            super(BitbucketOAuth1FailTest, self).test_partial_pipeline()
