import webapp2
import os
from jinja2 import Environment, FileSystemLoader
from util.jinja_filters import post_age_formatter
import util.auth_decorators as check
from model.comment import Comment
from model.post import Post
from util.RequestHandler import AuthAwareRequestHandler


template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
jinja_env.filters['post_age'] = post_age_formatter


class CreateCommentHandler(webapp2.RequestHandler):
    """
    Handles the creation of comments

    CreateCommentHandler manages POST requests that should submit comments
    to the Comment datastore.

    The POST method expects kwargs 'post_id' and 'user_id'
    """

    @check.post_exists
    @check.user_is_signed_in
    def post(self, **kwargs):
        post_id = kwargs['post_id']
        user_id = kwargs['user_id']
        content = self.request.POST['content']

        Comment(content=content, submitter=user_id, post_id=int(post_id)).put()

        self.redirect('/posts/' + post_id)


class UpdateCommentHandler(AuthAwareRequestHandler):
    """
    Handles editing of comments

    UpdateCommentHandler manages GET and POST requests. GET will render
    an editable form; POST handles the submission of that form.

    Both GET and POST requests expect kwargs 'post_id' and 'comment_id'
    """

    @check.user_is_signed_in
    @check.user_is_comment_author
    def get(self, **kwargs):
        template = jinja_env.get_template('edit-form.html')
        post_id = kwargs['post_id']
        comment_id = kwargs['comment_id']

        # Retrieve Post and its Comment(s) from the datastore
        post = Post.get_by_id(int(post_id))
        comments_query = Comment.query(Comment.post_id == int(post_id)).order(Comment.submitted)
        comments = [comment for comment in comments_query]

        self.write(template, {'post': post,
                              'edit_comment_id': int(comment_id),
                              'comments': comments})

    @check.comment_exists
    @check.user_is_signed_in
    @check.user_is_comment_author
    def post(self, **kwargs):
        post_id = kwargs['post_id']
        comment_id = kwargs['comment_id']
        content = self.request.POST['content']

        # Update the comment
        comment = Comment.get_by_id(int(comment_id))
        comment.content = content
        comment.put()

        self.redirect('/posts/' + post_id)


class DeleteCommentHandler(webapp2.RequestHandler):
    """
    Handles deleting of comments

    DeleteCommentHandler manages GET requests. GET will cause the comment
    with a given comment_id to be deleted, and redirect to the post at
    post_id.

    GET expects kwargs 'post_id' and 'comment_id'
    """

    @check.comment_exists
    @check.user_is_signed_in
    @check.user_is_comment_author
    def get(self, **kwargs):
        comment_id = kwargs['comment_id']
        post_id = kwargs['post_id']
        Comment().get_by_id(int(comment_id)).key.delete()
        self.redirect('/posts/' + post_id)
