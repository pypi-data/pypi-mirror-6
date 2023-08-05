# -*- coding: utf-8 -*-

from __future__ import with_statement

import base64
import simplejson as json

try:
    from cookielib import Cookie
except ImportError:
    from http.cookiejar import Cookie

from werkzeug.utils import parse_cookie

from tests import SecurityTest


def get_cookies(rv):
    cookies = {}
    for value in rv.headers.get_all("Set-Cookie"):
        cookies.update(parse_cookie(value))
    return cookies


class DefaultSecurityTests(SecurityTest):

    def test_instance(self):
        self.assertIsNotNone(self.app)
        self.assertIsNotNone(self.app.security)
        self.assertIsNotNone(self.app.security.pwd_context)

    def test_login_view(self):
        r = self._get('/login')
        self.assertIn(b'<h1>Login</h1>', r.data)

    def test_authenticate(self):
        r = self.authenticate()
        self.assertIn(b'Hello matt@lp.com', r.data)

    def test_authenticate_case_insensitive_email(self):
        r = self.authenticate(email='MATT@lp.com')
        self.assertIn(b'Hello matt@lp.com', r.data)

    def test_unprovided_username(self):
        r = self.authenticate("")
        self.assertIn(self.get_message('EMAIL_NOT_PROVIDED').encode('utf-8'), r.data)

    def test_unprovided_password(self):
        r = self.authenticate(password="")
        self.assertIn(self.get_message('PASSWORD_NOT_PROVIDED').encode('utf-8'), r.data)

    def test_invalid_user(self):
        r = self.authenticate(email="bogus@bogus.com")
        self.assertIn(self.get_message('USER_DOES_NOT_EXIST').encode('utf-8'), r.data)

    def test_bad_password(self):
        r = self.authenticate(password="bogus")
        self.assertIn(self.get_message('INVALID_PASSWORD').encode('utf-8'), r.data)

    def test_inactive_user(self):
        r = self.authenticate("tiya@lp.com", "password")
        self.assertIn(self.get_message('DISABLED_ACCOUNT').encode('utf-8'), r.data)

    def test_logout(self):
        self.authenticate()
        r = self.logout()
        self.assertIsHomePage(r.data)

    def test_unauthorized_access(self):
        self.logout()
        r = self._get('/profile', follow_redirects=True)
        self.assertIn(b'<li class="info">Please log in to access this page.</li>', r.data)

    def test_authorized_access(self):
        self.authenticate()
        r = self._get("/profile")
        self.assertIn(b'profile', r.data)

    def test_valid_admin_role(self):
        self.authenticate()
        r = self._get("/admin")
        self.assertIn(b'Admin Page', r.data)

    def test_invalid_admin_role(self):
        self.authenticate("joe@lp.com")
        r = self._get("/admin", follow_redirects=True)
        self.assertIsHomePage(r.data)

    def test_roles_accepted(self):
        for user in ("matt@lp.com", "joe@lp.com"):
            self.authenticate(user)
            r = self._get("/admin_or_editor")
            self.assertIn(b'Admin or Editor Page', r.data)
            self.logout()

        self.authenticate("jill@lp.com")
        r = self._get("/admin_or_editor", follow_redirects=True)
        self.assertIsHomePage(r.data)

    def test_unauthenticated_role_required(self):
        r = self._get('/admin', follow_redirects=True)
        self.assertIn(self.get_message('UNAUTHORIZED').encode('utf-8'), r.data)

    def test_multiple_role_required(self):
        for user in ("matt@lp.com", "joe@lp.com"):
            self.authenticate(user)
            r = self._get("/admin_and_editor", follow_redirects=True)
            self.assertIsHomePage(r.data)
            self._get('/logout')

        self.authenticate('dave@lp.com')
        r = self._get("/admin_and_editor", follow_redirects=True)
        self.assertIn(b'Admin and Editor Page', r.data)

    def test_ok_json_auth(self):
        r = self.json_authenticate()
        data = json.loads(r.data)
        self.assertEquals(data['meta']['code'], 200)
        self.assertIn('authentication_token', data['response']['user'])

    def test_invalid_json_auth(self):
        r = self.json_authenticate(password='junk')
        self.assertIn(b'"code": 400', r.data)

    def test_token_auth_via_querystring_valid_token(self):
        r = self.json_authenticate()
        data = json.loads(r.data)
        token = data['response']['user']['authentication_token']
        r = self._get('/token?auth_token=' + token)
        self.assertIn(b'Token Authentication', r.data)

    def test_token_auth_via_header_valid_token(self):
        r = self.json_authenticate()
        data = json.loads(r.data)
        token = data['response']['user']['authentication_token']
        headers = {"Authentication-Token": token}
        r = self._get('/token', headers=headers)
        self.assertIn(b'Token Authentication', r.data)

    def test_token_auth_via_querystring_invalid_token(self):
        r = self._get('/token?auth_token=X')
        self.assertEqual(401, r.status_code)

    def test_token_auth_via_header_invalid_token(self):
        r = self._get('/token', headers={"Authentication-Token": 'X'})
        self.assertEqual(401, r.status_code)

    def test_http_auth(self):
        r = self._get('/http', headers={
            'Authorization': 'Basic %s' % base64.b64encode(b"joe@lp.com:password").decode('utf-8')
        })
        self.assertIn(b'HTTP Authentication', r.data)

    def test_http_auth_no_authorization(self):
        r = self._get('/http', headers={})
        self.assertIn(b'<h1>Unauthorized</h1>', r.data)
        self.assertIn('WWW-Authenticate', r.headers)
        self.assertEquals('Basic realm="Login Required"',
                          r.headers['WWW-Authenticate'])

    def test_invalid_http_auth_invalid_username(self):
        r = self._get('/http', headers={
            'Authorization': 'Basic %s' % base64.b64encode(b"bogus:bogus").decode('utf-8')
        })
        self.assertIn(b'<h1>Unauthorized</h1>', r.data)
        self.assertIn('WWW-Authenticate', r.headers)
        self.assertEquals('Basic realm="Login Required"',
                          r.headers['WWW-Authenticate'])

    def test_invalid_http_auth_bad_password(self):
        r = self._get('/http', headers={
            'Authorization': 'Basic %s' % base64.b64encode(b"joe@lp.com:bogus").decode('utf-8')
        })
        self.assertIn(b'<h1>Unauthorized</h1>', r.data)
        self.assertIn('WWW-Authenticate', r.headers)
        self.assertEquals('Basic realm="Login Required"',
                          r.headers['WWW-Authenticate'])

    def test_custom_http_auth_realm(self):
        r = self._get('/http_custom_realm', headers={
            'Authorization': 'Basic %s' % base64.b64encode(b"joe@lp.com:bogus").decode('utf-8')
        })
        self.assertIn(b'<h1>Unauthorized</h1>', r.data)
        self.assertIn('WWW-Authenticate', r.headers)
        self.assertEquals('Basic realm="My Realm"',
                          r.headers['WWW-Authenticate'])

    def test_multi_auth_basic(self):
        r = self._get('/multi_auth', headers={
            'Authorization': 'Basic %s' % base64.b64encode(b"joe@lp.com:password").decode('utf-8')
        })
        self.assertIn(b'Basic', r.data)

    def test_multi_auth_token(self):
        r = self.json_authenticate()
        data = json.loads(r.data)
        token = data['response']['user']['authentication_token']
        r = self._get('/multi_auth?auth_token=' + token)
        self.assertIn(b'Token', r.data)

    def test_multi_auth_session(self):
        self.authenticate()
        r = self._get('/multi_auth')
        self.assertIn(b'Session', r.data)

    def test_user_deleted_during_session_reverts_to_anonymous_user(self):
        self.authenticate()

        with self.app.test_request_context('/'):
            user = self.app.security.datastore.find_user(email='matt@lp.com')
            self.app.security.datastore.delete_user(user)
            self.app.security.datastore.commit()

        r = self._get('/')
        self.assertNotIn(b'Hello matt@lp.com', r.data)

    def test_remember_token(self):
        r = self.authenticate(follow_redirects=False)
        self.client.cookie_jar.clear_session_cookies()
        r = self._get('/profile')
        self.assertIn(b'profile', r.data)

    def test_token_loader_does_not_fail_with_invalid_token(self):
        c = Cookie(version=0, name='remember_token', value='None', port=None,
                   port_specified=False, domain='www.example.com',
                   domain_specified=False, domain_initial_dot=False, path='/',
                   path_specified=True, secure=False, expires=None,
                   discard=True, comment=None, comment_url=None,
                   rest={'HttpOnly': None}, rfc2109=False)

        self.client.cookie_jar.set_cookie(c)
        r = self._get('/')
        self.assertNotIn(b'BadSignature', r.data)


class MongoEngineSecurityTests(DefaultSecurityTests):

    def _create_app(self, auth_config, **kwargs):
        from tests.test_app.mongoengine import create_app
        return create_app(auth_config, **kwargs)


class PeeweeSecurityTests(DefaultSecurityTests):

    def _create_app(self, auth_config, **kwargs):
        from tests.test_app.peewee_app import create_app
        return create_app(auth_config, **kwargs)


class DefaultDatastoreTests(SecurityTest):

    def test_add_role_to_user(self):
        r = self._get('/coverage/add_role_to_user')
        self.assertIn(b'success', r.data)

    def test_remove_role_from_user(self):
        r = self._get('/coverage/remove_role_from_user')
        self.assertIn(b'success', r.data)

    def test_activate_user(self):
        r = self._get('/coverage/activate_user')
        self.assertIn(b'success', r.data)

    def test_deactivate_user(self):
        r = self._get('/coverage/deactivate_user')
        self.assertIn(b'success', r.data)

    def test_invalid_role(self):
        r = self._get('/coverage/invalid_role')
        self.assertIn(b'success', r.data)


class MongoEngineDatastoreTests(DefaultDatastoreTests):

    def _create_app(self, auth_config, **kwargs):
        from tests.test_app.mongoengine import create_app
        return create_app(auth_config, **kwargs)
