import webtest
import unittest
from google.appengine.ext import testbed
from main import app
from model.post import Post
from model.user import User
from util.auth import create_user_cookie

class TestAdvancedBlogFeatures(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        # Set up some initial users
        valid_user = User(id="Valid User", password="password")
        self.valid_user_key = valid_user.put()

        invalid_user = User(id="Invalid User", password="password")
        self.invalid_user_key = invalid_user.put()

        valid_liker = User(id="Valid Liker", password="password")
        self.valid_liker_key = valid_user.put()

        invalid_liker = User(id="Invalid Liker", password="password")
        self.invalid_liker_key = invalid_user.put()

        # Set up an initial post
        initial_post = Post(title="Test Post", content="Some content", submitter="Valid User")
        self.initial_post_key = initial_post.put()

        initial_post_to_like = Post(title="Test Post", content="Some content", submitter="Invalid Liker")
        self.initial_post_to_like_key = initial_post_to_like.put()

        # Set up some other posts
        Post(title="Test Post A", content="Some content",
             submitter="Invalid Liker").put()
        Post(title="Test Post B", content="Some content",
             submitter="Valid User").put()
        Post(title="Test Post C", content="Some content",
             submitter="Valid User").put()

    def tearDown(self):
        self.testbed.deactivate()

    def testAuthorCanEditOwnPost(self):

        # Sign in as "Valid User" and navigate to the post's page
        self.testapp.set_cookie('user', create_user_cookie('Valid User'))
        response = self.testapp.request('/posts/%d' % self.initial_post_key.integer_id())

        # Check that an edit button is available and redirects to the edit page
        edit_button = response.html.select('.post-edit')
        self.assertEqual(len(edit_button), 1)
        edit_response = response.click(description="Edit", href="/posts/\d+/edit")
        # Perform an edit
        edit_response.form['title'] = "EDITED TITLE"
        edit_response.form['content'] = "EDITED CONTENT"
        form_redirect = edit_response.form.submit()
        edited_post_page = form_redirect.follow()

        # Check that the edit has updated title and content, but not submission info
        edited_title = edited_post_page.html.select('.post-title')[0].get_text()
        edited_submission_info = edited_post_page.html.select('.post-submitter')[0].get_text()
        unedited_submission_info = response.html.select('.post-submitter')[
            0].get_text()
        edited_content = edited_post_page.html.select('.post-content')[0].get_text()

        self.assertEqual(edited_title, "EDITED TITLE")
        self.assertEqual(edited_content, "EDITED CONTENT")
        self.assertEqual(unedited_submission_info, edited_submission_info)

    def testFormValidationIsPerformedOnEditedPost(self):
        self.testapp.set_cookie('user', create_user_cookie('Valid User'))
        response = self.testapp.request('/posts/%d' % self.initial_post_key.integer_id())

        # Check that an edit button is available and redirects to the edit page
        edit_button = response.html.select('.post-edit')
        self.assertEqual(len(edit_button), 1)
        edit_response = response.click(description="Edit", href="/posts/\d+/edit")
        # Perform an edit
        edit_response.form['title'] = ""
        edit_response.form['content'] = "EDITED CONTENT"
        invalid_form = edit_response.form.submit()
        validation_error = invalid_form.html.select('.validation-error')

        self.assertEqual(len(validation_error), 1)

    def testNonAuthorHasNoEditOption(self):

        # Sign in as "Invalid User" and navigate to the post's page
        self.testapp.set_cookie('user', create_user_cookie('Invalid User'))
        response = self.testapp.request(
            '/posts/%d' % self.initial_post_key.integer_id())

        # Test that the edit button is not available
        edit_button = response.html.select('.post-edit')
        self.assertEqual(len(edit_button), 0)

    def testNonAuthorCannotAccessEditPageViaUrl(self):

        # Sign in as "Invalid User" and navigate to the post's /edit page
        self.testapp.set_cookie('user', create_user_cookie('Invalid User'))
        response = self.testapp.request(
            '/posts/%d/edit' % self.initial_post_key.integer_id())

        # Test that the user is redirected to the post page
        self.assertEqual(response.status_int, 302)

    def testNonAuthorCannotEditPostViaPOSTRequestToUrl(self):

        # Sign in as "Invalid User" and attempt to POST to /posts/postid
        self.testapp.set_cookie('user', create_user_cookie('Invalid User'))
        post_response = self.testapp.post('/posts/%d/edit' % self.initial_post_key.integer_id(),
                              {'content': 'EDITED via POST',
                               'title': 'EDITED via POST'})

        # Ensure that a redirect occurs to posts/post_id
        self.assertEqual(post_response.status_int, 302)
        post_page = post_response.follow()

        # Ensure that the content was not altered
        title = post_page.html.select('.post-title')[0]
        content = post_page.html.select('.post-content')[0]
        self.assertNotEqual(title, "EDITED via POST")
        self.assertNotEqual(content, "EDITED via POST")

    def testAuthorCanDeleteOwnPost(self):
        # Sign in as "Valid User" and navigate to the post's page
        self.testapp.set_cookie('user', create_user_cookie('Valid User'))
        response = self.testapp.request('/posts/%d' % self.initial_post_key.integer_id())

        # Check that a delete button is available and points to the delete endpoint
        delete_button = response.html.select('.post-delete')
        self.assertEqual(len(delete_button), 1)
        delete_response = response.click(description="Delete", href="/posts/\d+/delete")

        # Follow the delete redirect to main page and check that deleted post isn't listed
        main_page = delete_response.follow()
        posts = main_page.html.select('.post')
        for post in posts:
            self.assertNotEqual(post['id'], self.initial_post_key.integer_id())

        # Check that the deleted post's page is unavailable
        deleted_post = self.testapp.request('/posts/%d' % self.initial_post_key.integer_id(), expect_errors=404)
        self.assertEqual(deleted_post.status_int, 404)

    def testNonAuthorHasNoDeleteOption(self):
        # Sign in as "Invalid User" and navigate to the post's page
        self.testapp.set_cookie('user', create_user_cookie('Invalid User'))
        response = self.testapp.request('/posts/%d' % self.initial_post_key.integer_id())

        # Check that the delete button is available and redirects to the delete endpoint
        delete_button = response.html.select('.post-delete')
        self.assertEqual(len(delete_button), 0)

    def testNonAuthorCannotDeletePostViaUrl(self):

        # Sign in as "Invalid User" and navigate to the post's /delete page
        self.testapp.set_cookie('user', create_user_cookie('Invalid User'))
        response = self.testapp.request(
            '/posts/%d/delete' % self.initial_post_key.integer_id())

        # Test that the user is redirected to the post page
        self.assertEqual(response.status_int, 302)

    def testNonAuthorCanLikePost(self):

        # Sign in as non author and navigate to another author's post
        self.testapp.set_cookie('user', create_user_cookie('Valid Liker'))
        response = self.testapp.request('/posts/%d' % self.initial_post_to_like_key.integer_id())

        # Store the like counter value
        like_counter_before = response.html.select('.post-likes')[0].get_text()

        # Assert that the like button is available
        like_button = response.html.select('.post-like')
        self.assertEqual(len(like_button), 1)
        like_response = response.click(description="Like", href="/posts/\d+/like")

        # Follow like response to post page and check counter increments
        post_page = like_response.follow()
        like_counter_after = post_page.html.select('.post-likes')[0].get_text()

        like_counter_before = int(like_counter_before)
        like_counter_after = int(like_counter_after)
        self.assertTrue(like_counter_after == like_counter_before + 1)

    def testAuthorCannotLikePostViaUI(self):

        # Sign in as author and navigate to an authored post
        self.testapp.set_cookie('user', create_user_cookie('Invalid Liker'))
        response = self.testapp.request('/posts/%d' % self.initial_post_to_like_key.integer_id())

        # Assert that the like button is unavailable
        like_button = response.html.select('.post-like')
        self.assertEqual(len(like_button), 0)

    def testAuthorCannotLikePostViaUrl(self):

        # Sign in as non author and navigate to another author's post
        self.testapp.set_cookie('user', create_user_cookie('Invalid Liker'))
        response = self.testapp.request('/posts/%d' % self.initial_post_to_like_key.integer_id())

        # Store the like counter value
        like_counter_before = response.html.select('.post-likes')[0].get_text()

        # Issue GET against the post's /like endpoint
        like_response = self.testapp.request('/posts/%d/like' % self.initial_post_to_like_key.integer_id())
        post_page = like_response.follow()
        like_counter_after = post_page.html.select('.post-likes')[0].get_text()

        like_counter_before = int(like_counter_before)
        like_counter_after = int(like_counter_after)
        self.assertTrue(like_counter_after == like_counter_before)

    def testLikedPostMustBeUnliked(self):

        # Ensure that post has been liked
        post = Post.get_by_id(self.initial_post_to_like_key.integer_id())
        post.liked_by.append("Valid Liker")
        post.put()

        # Ensure that the Unlike button appears
        self.testapp.set_cookie('user', create_user_cookie('Valid Liker'))
        response = self.testapp.request('/posts/%d' % self.initial_post_to_like_key.integer_id())
        like_button = response.html.select('.post-like')[0]
        self.assertEqual(like_button.get_text(), 'Unlike')

        # Click the Unlike button an ensure the like counter decrements
        unlike_response = response.click(description="Unlike").follow()
        like_counter = unlike_response.html.select('.post-likes')[0].get_text()

        self.assertEqual(int(like_counter), 1)


    def testUnlikedPostCanBeLiked(self):

        # Ensure that post has been liked
        post = Post.get_by_id(self.initial_post_to_like_key.integer_id())
        post.liked_by.append("Valid Liker")
        post.put()

        # Ensure that the Unlike button appears
        self.testapp.set_cookie('user', create_user_cookie('Valid Liker'))
        response = self.testapp.request('/posts/%d' % self.initial_post_to_like_key.integer_id())
        like_button = response.html.select('.post-like')[0]
        self.assertEqual(like_button.get_text(), 'Unlike')

        # Click the Unlike button an ensure the like counter decrements
        unlike_response = response.click(description="Unlike").follow()
        like_counter = unlike_response.html.select('.post-likes')[0].get_text()
        self.assertEqual(int(like_counter), 1)

        # Now ensure that there is a Like button and that re-liking increments the counter
        re_like_response = unlike_response.click(description="Like").follow()
        re_like_counter = re_like_response.html.select('.post-likes')[0].get_text()
        self.assertTrue(int(re_like_counter) == int(like_counter) + 1)