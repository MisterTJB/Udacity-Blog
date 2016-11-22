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
        test_user = User(username="Test", password="test_password")
        self.test_user_key = test_user.put()

    def tearDown(self):
        self.testbed.deactivate()

    def testUserPasswordIsHashed(self):
        from hashlib import sha512
        from model.user import PasswordProperty
        user = User().get_by_id(self.test_user_key.id())
        self.assertEqual(user.password, sha512("test_password" + PasswordProperty.salt).hexdigest())