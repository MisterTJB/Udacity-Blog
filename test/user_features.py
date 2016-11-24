import webtest
import unittest
from google.appengine.ext import testbed
from main import app
from model.user import User

class TestUserFeatures(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        # Set up an initial post
        test_user = User(id="Test", password="test_password")
        self.test_user_key = test_user.put()

    def tearDown(self):
        self.testbed.deactivate()

    def signUpNewUserWithUsername(self, username):
        sign_up_response = self.testapp.request("/users/new")
        form = sign_up_response.form
        form['username'] = username
        form['password'] = "PASSWORD"
        return form.submit()

    def testUserPasswordIsHashed(self):
        from hashlib import sha512
        from model.user import PasswordProperty
        user = User().get_by_id("Test")
        self.assertEqual(user.password, sha512("test_password" + PasswordProperty.salt).hexdigest())

    def testUserCanCreateAccountWithValidCredentials(self):
        _ = self.signUpNewUserWithUsername("User_02")
        user = User().get_by_id("User_02")
        self.assertIsNotNone(user)

    def testSuccessfulNewUserIsSignedIn(self):
        _ = self.signUpNewUserWithUsername("User_03")
        user_cookie = self.testapp.cookies.get('user')
        self.assertIsNotNone(user_cookie)

    def testSuccessfulNewUserIsRedirected(self):
        form_response = self.signUpNewUserWithUsername("User_04")
        redirect_response = form_response.follow()
        welcome_html = redirect_response.html
        welcome_message = welcome_html.select('.welcome-message')[0].get_text()
        self.assertEqual(welcome_message, "Welcome, User_04")

    def testUserCannotCreateAccountWithoutUsername(self):
        sign_up_response = self.testapp.request("/users/new")
        form = sign_up_response.form
        form['password'] = "password"
        form_response = form.submit()
        username_error_elements = form_response.html.select('.username-error')
        self.assertTrue(len(username_error_elements) > 0)

    def testUserCannotCreateAccountWithoutPassword(self):
        sign_up_response = self.testapp.request("/users/new")
        form = sign_up_response.form
        form['username'] = "User_05"
        form_response = form.submit()
        password_error_elements = form_response.html.select('.password-error')
        self.assertTrue(len(password_error_elements) > 0)

    def testUserCannotCreateAccountWithDuplicateUsername(self):
        sign_up_response = self.testapp.request("/users/new")
        form = sign_up_response.form
        form['username'] = "Test"
        form['password'] = "password"
        form_response = form.submit()
        username_error_elements = form_response.html.select('.username-error')
        self.assertTrue(len(username_error_elements) > 0)