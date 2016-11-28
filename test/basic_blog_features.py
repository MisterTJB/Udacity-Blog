import webtest
import unittest
from google.appengine.ext import testbed
from main import app
from model.post import Post
from util.auth import create_user_cookie

class TestBasicBlogFeatures(unittest.TestCase):
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

    # The front page has a <div class="post"> for each of the posts in the datastore
    def testFrontPageListsBlogPosts(self):
        response = self.testapp.get("/")
        self.assertEquals(response.status_int, 200)
        posts = response.html.find_all('div', {'class': 'post'})
        self.assertEquals(len(posts), 1)

    # The <div class="post"> element contains data for title, content, votes
    # submitter, submitted datetime, and a link to the post's entry
    def testPostElementStructure(self):
        import datetime
        test_post = Post(title="Test", content="Some content", submitter="Me")
        test_post_key = test_post.put()
        test_post_id = test_post_key.id()
        response = self.testapp.get("/")
        self.assertEquals(response.status_int, 200)
        post = response.html.find(id=test_post_id)
        self.assertIsNotNone(post)

        post_votes = post.select('.likes')[0].get_text()
        post_title = post.select('.title-anchor')[0].get_text()
        post_href = post.select('.title-anchor')[0].get('href')
        post_submission_info = post.select('.submission-info')[0].get_text()
        post_content = post.select('.content')[0].get_text()

        self.assertEqual(post_votes, "1")
        self.assertEqual(post_title, "Test")
        self.assertEqual(post_href, "/posts/%d" % test_post_id)
        self.assertEqual(post_submission_info, "Written by Me | %s" %
                         datetime.datetime.utcnow().date().isoformat())
        self.assertTrue(post_content, "Some content")

    # posts/new renders a form for submitting new posts
    def testThereIsAFormForSubmittingNewPosts(self):

        # Sign a user in
        self.testapp.set_cookie('user', create_user_cookie('user'))

        response = self.testapp.get("/posts/new")
        self.assertEqual(response.status_int, 200)
        form = response.html.find('form')
        self.assertIsNotNone(form)

    def testCreatePostRedirectsIfNotSignedIn(self):
        response = self.testapp.get("/posts/new")
        self.assertEqual(response.status_int, 302)

        redirect_response = response.follow()
        self.assertEqual(redirect_response.request.path, "/users/in")

    # POSTing to posts/new with valid data adds the post to the datastore
    def testNewPostFormAddsPostToDatastoreIfValid(self):

        # Sign a user in
        self.testapp.set_cookie('user', create_user_cookie('user'))

        response = self.testapp.get('/posts/new')
        form = response.form
        form['title'] = 'Test title'
        form['content'] = 'Test content'
        form_response = form.submit()
        redirect_response = form_response.follow()

        self.assertEqual(redirect_response.status_int, 200)
        post = redirect_response.html
        title = post.select(".post-title")[0].get_text()
        content = post.select(".post-content")[0].get_text()
        self.assertEqual(title, form['title'].value)
        self.assertEqual(content, form['content'].value)

    def testPOSTDoesNotAtPostToDatastoreIfNotSignedIn(self):
        pre_posts_query = Post.query()
        pre_total = len([post for post in pre_posts_query])

        post_response = self.testapp.post('/posts', {'title': 'junk', 'content': 'junk'})
        self.assertEqual(post_response.status_int, 302)
        redirect_response = post_response.follow()
        self.assertEqual(redirect_response.request.path, "/users/in")

        post_posts_query = Post.query()
        post_total = len([post for post in post_posts_query])
        self.assertEqual(pre_total, post_total)



    # POSTing to /new with invalid data renders /new with errors
    def testNewPostFormRendersWithErrorsIfInvalid(self):

        # Sign a user in
        self.testapp.set_cookie('user', create_user_cookie('user'))

        response = self.testapp.get('/posts/new')
        form = response.form
        form['title'] = 'Test title'
        form_response = form.submit()
        print form_response
        error_html = form_response.html

        title = error_html.select('.form-title')[0].get('value')
        content = error_html.select('.form-content')[0].get_text()
        error = error_html.select('.validation-error')[0]

        self.assertEqual(title, form['title'].value)
        self.assertEqual(content, form['content'].value)
        self.assertIsNotNone(error)


    # GETing posts/post-id renders post with identifier post-id if post-id
    # exists
    def testBlogPostsHaveTheirOwnPageForValidIdentifier(self):
        response = self.testapp.get("/posts/%d" % self.initial_post_key.id())
        self.assertEqual(response.status_int, 200)

    # GETing posts/post-id renders 404 if post with identifer post-id does not
    # exist
    def testBlogPosts404ForInvalidIdentifier(self):
        response = self.testapp.get("/posts/junk", status=404)
        self.assertEqual(response.status_int, 404)