import webtest
import unittest
from google.appengine.ext import testbed
from main import app
from model.post import Post

class TestAdvancedBlogFeatures(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        # Set up an initial post
        initial_post = Post(title="Test", content="Some content", submitter="Me")
        self.initial_post_key = initial_post.put()

    def tearDown(self):
        self.testbed.deactivate()

    def testAuthorCanEditOwnPost(self):
        self.fail()

    def testNonAuthorCannotPost(self):
        self.fail()

    def testAuthorCanDeleteOwnPost(self):
        self.fail()

    def testNonAuthorCannotDeletePost(self):
        self.fail()

    def testNonAuthorCanLikePost(self):
        self.fail()

    def testAuthorCannotLikePost(self):
        self.fail()

    def testLikedPostCanBeUnliked(self):
        self.fail()

    def testUnlikedPostCanBeLiked(self):
        self.fail()