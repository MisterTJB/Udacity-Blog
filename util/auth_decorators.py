"""
Decorator functions for aborting or redirecting responses depending on the
state of the user's authentication
"""
from model.post import Post
from model.comment import Comment
from util.auth import validate_user_cookie


def user_is_post_author(fn, invert=False):
    """
    Decorator function that only proceeds with formulating a response to a
    request in the case where the 'user' cookie is present, valid, and
    corresponds to the author of this post

    Args:
        fn: The function to wrap. Usually a RequestHandler method
        invert: If True, perform opposite test (i.e. user_is_NOT_post_author)

    Returns:
        A decorator function that proceeds with the request if the 'user'
        cookie is valid, or redirects to /posts/post-id otherwise.
    """

    def redirect_if_not_author(*args, **kwargs):
        self = args[0]
        user_id = kwargs['user_id']
        post_id = kwargs['post_id']
        post = Post().get_by_id(int(post_id))

        is_author = (post.submitter == user_id)

        # Perform is_author XOR invert to determine whether or not to
        # call the decorated function
        decorate = (is_author and not invert) or (not is_author and invert)

        if decorate:
            # Call the decorated function
            fn(*args, **kwargs)
        else:
            self.redirect('/posts/' + kwargs['post_id'])

    return redirect_if_not_author


def user_is_comment_author(fn):
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


def user_is_not_post_author(fn):
    """
    Convenience decorator for calling user_is_post_author with inverted logic
    """
    return user_is_post_author(fn, True)


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
            fn(self, **kwargs)
        else:
            self.redirect('/users/in')

    return redirect_if_not_signed_in


def post_exists(fn):
    """
    Decorator function that only proceeds with formulating a response to a
    request in the case where a Post with a given post_id actually exists.

    If a Post does not exist, the application will trigger a 404 response.

    """
    def error_if_post_does_not_exist(*args, **kwargs):
        self = args[0]
        post_id = kwargs['post_id']
        post = Post.get_by_id(int(post_id))

        if post:
            fn(self, **kwargs)
        else:
            self.abort(404)

    return error_if_post_does_not_exist


def comment_exists(fn):
    """
    Decorator function that only proceeds with formulating a response to a
    request in the case where a Comment with a given comment_id actually
    exists.

    If a Comment does not exist, the application will trigger a 404 response.

    """
    def error_if_comment_does_not_exist(*args, **kwargs):
        self = args[0]
        post_id = kwargs['comment_id']
        post = Comment.get_by_id(int(post_id))

        if post:
            fn(self, **kwargs)
        else:
            self.abort(404)

    return error_if_comment_does_not_exist
