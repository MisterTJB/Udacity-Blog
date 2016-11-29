import webapp2
import os
from model.comment import Comment
from model.post import Post
from util.auth import validate_user_cookie
from util.RequestHandler import AuthAwareRequestHandler
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)


def post_age_formatter(creation_timestamp):
    """
    Format a datetime object in ISO format (YYYY-MM-DD)

    Args:
        creation_timestamp: A datetime object to format

    Returns:
         A string of the form YYYY-MM-DD
    """

    return creation_timestamp.date().isoformat()

jinja_env.filters['post_age'] = post_age_formatter


def user_is_author(fn):
    """
    Decorator function that only proceeds with formulating a response to a
    request in the case where the 'user' cookie is present, valid, and
    corresponds to the author of this comment

    Args:
        fn: The function to wrap. Usually a RequestHandler method

    Returns:
        A decorator function that proceeds with the request if the 'user'
        cookie is valid, or redirects to /posts/post-id otherwise.

        A 404 error is raised in the case that the comment does not exist
    """

    def redirect_if_not_author(*args, **kwargs):
        self = args[0]
        user_id = kwargs['user_id']
        comment_id = kwargs['comment_id']
        comment = Comment().get_by_id(int(comment_id))

        if comment and comment.submitter == user_id:
            # Call the decorated function
            fn(*args, **kwargs)
        elif comment:
            self.redirect('/posts/' + kwargs['post_id'])
        else:
            self.abort(404)

    return redirect_if_not_author


def user_is_signed_in(fn):
    """
    Decorator function that only proceeds with formulating a response to a
    request in the case where the 'user' cookie is present and valid

    Args:
        fn: The function to wrap. Usually a RequestHandler method

    Returns:
        A decorator function that proceeds with the request if the 'user'
        cookie is valid, or redirects to /users/in otherwise
    """

    def redirect_if_not_signed_in(*args, **kwargs):
        self = args[0]
        cookie = self.request.cookies.get('user')
        if validate_user_cookie(cookie):
            kwargs['user_id'] = self.request.cookies.get('user').split("|")[0]
            print "kwargs in user_is_signed_in: ", kwargs
            fn(self, **kwargs)
        else:
            self.redirect('/users/in')

    return redirect_if_not_signed_in


class CreateCommentHandler(webapp2.RequestHandler):
    """
    Handles the creation of comments

    CreateCommentHandler manages POST requests that should submit comments
    to the Comment datastore.

    The POST method expects kwargs 'post_id' and 'user_id'
    """

    @user_is_signed_in
    def post(self, **kwargs):
        post_id = kwargs['post_id']
        user_id = kwargs['user_id']
        content = self.request.POST['content']

        if post_id.isdigit():
            Comment(content=content,
                    submitter=user_id,
                    post_id=int(post_id)).put()

        self.redirect('/posts/' + post_id)


class UpdateCommentHandler(AuthAwareRequestHandler):
    """
    Handles editing of comments

    UpdateCommentHandler manages GET and POST requests. GET will render
    an editable form; POST handles the submission of that form.

    Both GET and POST requests expect kwargs 'post_id' and 'comment_id'
    """

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        template = jinja_env.get_template('edit-form.html')
        post_id = kwargs['post_id']
        comment_id = kwargs['comment_id']

        # Retrieve Post and its Comment(s) from the datastore
        post = Post.get_by_id(int(post_id))
        comments_query = Comment.query(
            Comment.post_id == int(post_id)).order(Comment.submitted)
        comments = [comment for comment in comments_query]

        if post:
            self.write(template, {'post': post,
                                  'edit_comment_id': int(comment_id),
                                  'comments': comments})
        else:
            self.abort(404)

    @user_is_signed_in
    @user_is_author
    def post(self, **kwargs):
        post_id = kwargs['post_id']
        comment_id = kwargs['comment_id']
        content = self.request.POST['content']

        # Update a comment
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

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        comment_id = kwargs['comment_id']
        post_id = kwargs['post_id']
        Comment().get_by_id(int(comment_id)).key.delete()
        self.redirect('/posts/' + post_id)
