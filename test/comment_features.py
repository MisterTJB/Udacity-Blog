"""
Test suite for testing the commenting features of a blog.

In particular, this test suite tests:

    - Creating comments
    - Editing comments
    - Deleting comments

Paths for signed in and sign out users, and authorship, are tested in each case

"""

import webtest
import unittest
from google.appengine.ext import testbed
from main import app
from model.comment import Comment
from model.post import Post
from model.user import User
from util.auth import create_user_cookie


def establish_users_and_post_with_comments():

    User(id="Test_User_01", password="password").put()
    User(id="Test_User_02", password="password").put()
    User(id="Test_User_03", password="password").put()

    post_key = Post(title="Test",
                    submitter="Test_User_01", content="Test").put()

    comment_01 = Comment(content="Test content 01", submitter="Test_User_01",
                         post_id=post_key.integer_id()).put()
    comment_02 = Comment(content="Test content 02", submitter="Test_User_02",
                         post_id=post_key.integer_id()).put()
    comment_03 = Comment(content="Test content 03", submitter="Test_User_03",
                         post_id=post_key.integer_id()).put()

    return (post_key.integer_id(), [comment_01.integer_id(),
                                    comment_02.integer_id(),
                                    comment_03.integer_id()])


class TestCommentFeatures(unittest.TestCase):

    def setUp(self):
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.test_post_id, self.comment_ids = \
            establish_users_and_post_with_comments()

    def tearDown(self):
        self.testbed.deactivate()

    def testCommentsAreListed(self):
        response = self.testapp.request("/posts/%d" % self.test_post_id)
        comments = response.html.select(".comment")
        self.assertEqual(len(comments), len(self.comment_ids))

    def testCommentsAreOrdered(self):
        response = self.testapp.request("/posts/%d" % self.test_post_id)
        comments = response.html.select(".comment")
        self.assertEqual(int(comments[0]['id']), self.comment_ids[0])
        self.assertEqual(int(comments[1]['id']), self.comment_ids[1])
        self.assertEqual(int(comments[2]['id']), self.comment_ids[2])

    def testSignedInUserCanAddComment(self):
        self.testapp.set_cookie('user', create_user_cookie('Test_User_01'))
        response = self.testapp.request("/posts/%d" % self.test_post_id)
        response.form['content'] = "New content"
        form_response = response.form.submit()
        redirect_response = form_response.follow()
        latest_comment = redirect_response.html.select(".comment")[-1]
        latest_comment_content = latest_comment.select(
            '.comment-content')[0].get_text()
        self.assertEqual(latest_comment_content, "New content")

    def testSignedOutUserCannotAddComment(self):
        response = self.testapp.request("/posts/%d" % self.test_post_id)
        response.form['content'] = "New content"
        form_response = response.form.submit()
        redirect_response = form_response.follow()
        sign_up_panel = redirect_response.html.select('.signup-panel')
        self.assertGreater(len(sign_up_panel), 0)

    def testUserCanEditTheirOwnComment(self):
        self.testapp.set_cookie('user', create_user_cookie('Test_User_01'))

        # Edit button is available on post page
        post_page_response = self.testapp.request("/posts/%d"
                                                  % self.test_post_id)
        comment = post_page_response.html.select('.comment')[0]
        comment_edit_controls = comment.select('.comment-options')
        self.assertEqual(len(comment_edit_controls), 1)

        # Edit form is available on edit page
        edit_page_response = self.testapp.request(
            "/posts/%d/comments/%d" % (self.test_post_id, self.comment_ids[0]))
        edit_form = edit_page_response.form
        self.assertEqual(edit_form['content'].value, "Test content 01")
        edit_form['content'].value = "Test content 01 (edited)"
        form_response = edit_form.submit()

        # Edit has taken effect on post page
        redirect_response = form_response.follow()
        edited_comment = redirect_response.html.select(".comment")[0]
        edited_comment_content = edited_comment.select('.comment-content')[
            0].get_text()
        self.assertEqual(edited_comment_content, "Test content 01 (edited)")

    def testUserCannotEditOtherComments(self):
        self.testapp.set_cookie('user', create_user_cookie('Test_User_01'))

        # Edit button is not available on post page
        post_page_response = self.testapp.request(
            "/posts/%d" % self.test_post_id)
        comment = post_page_response.html.select('.comment')[1]
        comment_edit_controls = comment.select('.comment-options')
        self.assertEqual(len(comment_edit_controls), 0)

        # Edit page is inaccessible for non-author
        # (i.e. redirects to post page)
        edit_page_response = self.testapp.request(
            "/posts/%d/comments/%d" % (self.test_post_id, self.comment_ids[1]))
        redirect = edit_page_response.follow()
        self.assertEqual(redirect.request.path, '/posts/%d' %
                         self.test_post_id)

    def testEditCommentViaPOSTIsIneffectiveForNonAuthor(self):
        self.testapp.set_cookie('user', create_user_cookie('Test_User_01'))

        # Attempt to POST directly to comment URL to edit the second comment
        url = "/posts/%d/comments/%d" % (self.test_post_id,
                                         self.comment_ids[1])
        _ = self.testapp.post(url, {'content': 'Test content 02 (edited)'})

        # Check that the second comment is unaltered
        post_page_response = self.testapp.request("/posts/%d"
                                                  % self.test_post_id)
        second_comment = post_page_response.html.select(".comment")[1]
        edited_comment = second_comment.select(
            '.comment-content')[0].get_text()
        self.assertNotEqual(edited_comment, "Test content 02 (edited)")
        self.assertEqual(edited_comment, "Test content 02")

    def testUserCanDeleteTheirOwnComment(self):
        self.testapp.set_cookie('user', create_user_cookie('Test_User_01'))
        user_01_comment = "/posts/%d/comments/%d" % (self.test_post_id,
                                                     self.comment_ids[0])
        delete_response = self.testapp.request(user_01_comment + "/delete")
        for comment in delete_response.html.select('.comment'):
            self.assertNotEqual(int(comment['id']), self.comment_ids[0])

    def testUserCannotDeleteOtherComments(self):
        self.testapp.set_cookie('user', create_user_cookie('Test_User_01'))
        user_02_comment = "/posts/%d/comments/%d" % (self.test_post_id,
                                                     self.comment_ids[1])
        delete_response = self.testapp.request(user_02_comment + "/delete")

        delete_redirect = delete_response.follow()
        self.assertEqual(delete_redirect.request.path,
                         '/posts/%d' % self.test_post_id)

        comments = delete_redirect.html.select('.comment')
        self.assertEqual(len(comments), 3)
