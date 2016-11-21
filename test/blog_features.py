import webtest
import unittest
from google.appengine.ext import testbed
from main import app
from model.post import Post

class BlogFeaturesTest(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    # The front page lists each of the posts in the datastore
    def testFrontPageListsBlogPosts(self):
        self.fail("Not implemented")

    # /new renders a form for submitting new posts
    def testThereIsAFormForSubmittingNewPosts(self):
        self.fail("Not implemented")

    # POSTing to /new with valid data adds the post to the datastore
    def testNewPostFormAddsPostToDatastoreIfValid(self):
        self.fail("Not implemented")

    # POSTing to /new with invalid data renders /new with errors
    def testNewPostFormRendersWithErrorsIfInvalid(self):
        self.fail("Not implemented")

    # GETing posts/post-id renders post with identifier post-id if post-id
    # exists
    def testBlogPostsHaveTheirOwnPageForValidIdentifier(self):
        self.fail("Not implemented")

    # GETing posts/post-id renders 404 if post with identifer post-id does not
    # exist
    def testBlogPostsHaveTheirOwnPage(self):
        self.fail("Not implemented")