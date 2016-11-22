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

        # Set up an initial post
        initial_post = Post(title="Test", votes=1, content="Some content", submitter="Me")
        initial_post.put()

    def tearDown(self):
        self.testbed.deactivate()

    # The front page has a <div class="post"> for each of the posts in the datastore
    def testFrontPageListsBlogPosts(self):
        response = self.testapp.get("/")
        self.assertEquals(response.status_int, 200)
        posts = response.html.find_all('div', {'class': 'post'})
        self.assertEquals(len(posts), 1)

    # The <div class="post"> element contains data for title, content, votes
    # submitter, submitted datetime, and a link to the post's entry
    def testPostElementStructure(self):
        test_post = Post(title="Test", votes=1, content="Some content",
                            submitter="Me")
        test_post_key = test_post.put()
        test_post_id = test_post_key.id()
        response = self.testapp.get("/")
        self.assertEquals(response.status_int, 200)
        post = response.html.find(id=test_post_id)
        self.assertIsNotNone(post)

        post_votes = post.select('.votes')[0].get_text()
        post_title = post.select('.title-anchor')[0].get_text()
        post_href = post.select('.title-anchor')[0].get('href')
        post_submission_info = post.select('.submission-info')[0].get_text()
        post_content = post.select('.content')[0].get_text()

        self.assertEqual(post_votes, "1")
        self.assertEqual(post_title, "Test")
        self.assertEqual(post_href, "/posts/%d" % test_post_id)
        self.assertEqual(post_submission_info, "Submitted by Me moments ago")
        self.assertTrue("Some content")



    # A post older than 86400 seconds should be echoed as "n days ago"
    def testJinjaAgeFilterDaysOld(self):
        self.fail("Not implemented")

    # A post older than 3600 seconds should be echoed as "n hours ago"
    def testJinjaAgeFilterHoursOld(self):
        self.fail("Not implemented")

    # A post older than 60 seconds should be echoed as "n minutes ago"
    def testJinjaAgeFilterMinutesOld(self):
        self.fail("Not implemented")

    # A post no older than 59 seconds should be echoed as "moments ago"
    def testJinjaAgeFilterMomentsOld(self):
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