import webapp2
import os
from util.RequestHandler import AuthAwareRequestHandler
from model.post import Post
from model.comment import Comment
from util.auth import validate_user_cookie
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)


def post_age_formatter(creation_timestamp):
    """
    Format a datetime object as YYYY-MM-DD

    Args:
        creation_timestamp: A datetime object

    Returns:
        A string representation of the datetime object having the form
        YYYY-MM-DD
    """
    return creation_timestamp.date().isoformat()


def trim_to_two_sentences(post):
    """
    Trim a multi-sentence string to the first three sentences and append an
    ellipsis. A sentence is considered to terminate with a period ('.').

    If a string is fewer than three sentences, the entire string will be
    returned (i.e. without an ellipsis)
    """
    trimmed_post = post.split(".")[:3]
    if len(trimmed_post) >= 3:
        return '. '.join(trimmed_post) + "..."
    else:
        return post

jinja_env.filters['post_age'] = post_age_formatter
jinja_env.filters['trim'] = trim_to_two_sentences


def user_is_author(fn):
    """
    Decorator function that only proceeds with formulating a response to a
    request in the case where the 'user' cookie is present, valid, and
    corresponds to the author of this post

    Args:
        fn: The function to wrap. Usually a RequestHandler method

    Returns:
        A decorator function that proceeds with the request if the 'user'
        cookie is valid, or redirects to /posts/post-id otherwise.
    """

    def redirect_if_not_author(*args, **kwargs):
        self = args[0]
        user_id = kwargs['user_id']
        post_id = kwargs['post_id']
        post = Post().get_by_id(int(post_id))

        if post.submitter == user_id:
            # Call the decorated function
            fn(*args, **kwargs)
        else:
            self.redirect('/posts/' + kwargs['post_id'])

    return redirect_if_not_author


def user_is_not_author(fn):
    """
    Decorator function that only proceeds with formulating a response to a
    request in any case where the case where the 'user' cookie is present,
    valid, and does not correspond to the author of this post

    Args:
        fn: The function to wrap. Usually a RequestHandler method

    Returns:
        A decorator function that proceeds with the request if the 'user'
        is not a post author, or redirects to /posts/post-id otherwise.

    """

    def redirect_if_author(*args, **kwargs):
        self = args[0]
        user_id = kwargs['user_id']
        post_id = kwargs['post_id']
        post = Post().get_by_id(int(post_id))

        if post.submitter != user_id:
            fn(*args, **kwargs)
        else:
            self.redirect('/posts/' + kwargs['post_id'])

    return redirect_if_author


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


def user_has_liked_post(user_id, post_id):
    """
    Indicates whether a user has already liked a given post

    Args:
        user_id: The user id of the user to test against this post, as an int
            or str
        post_id: The post id for the post to test this user against, as an int
            or str

    Returns:
        True if the user with id user_id has 'liked' the post with id post_id
        False otherwise
    """
    post = Post.get_by_id(int(post_id))
    if post:
        return user_id in post.liked_by


class FrontPageHandler(AuthAwareRequestHandler):
    """
    Handles the main page listing blog posts

    FrontPageHandler manages GET requests that expect a response that will
    render a list of blog posts sorted in descending order (first by likes,
    then by submission date)
    """
    template = jinja_env.get_template('posts.html')

    def get(self):
        self.write(self.template, {
            'posts': Post().query().order(-Post.likes, -Post.submitted)
        })


class NewPostFormHandler(AuthAwareRequestHandler):
    """
    Handles the rendering of the new post page

    NewPostFormHandler manages GET requests that expect a form to be rendered
    for creating new blog posts, including with form validation hints
    """

    @user_is_signed_in
    def get(self, **kwargs):
        self.write(jinja_env.get_template('new-post.html'),
                   {'form': {'title': '', 'content': '', 'error': False},
                    'new': True})


class PostsHandler(AuthAwareRequestHandler):
    """
    Handles the submission of new posts to the datastore

    PostsHandler manages POST requests whose form data is intended for
    submission to the datastore as a new blog post. Performs validation and
    rerenders the form if validation fail.

    The POST method expects kwargs 'title' and 'content' (corresponding to the
    title and content of a post)
    """

    @user_is_signed_in
    def post(self, **kwargs):
        title = self.request.POST['title']
        content = self.request.POST['content']
        submitter = self.request.cookies.get('user').split("|")[0]

        # Check that title and content are non-empty and add the data to the
        # datastore; otherwise, re-render the form with errors
        if title != '' and content != '':
            new_post = Post(title=title, content=content, submitter=submitter)
            new_post_key = new_post.put()
            new_post_id = new_post_key.id()
            self.redirect('/posts/%d' % new_post_id)
        else:
            template = jinja_env.get_template('new-post.html')
            form_data = {'title': title, 'content': content, 'error': True}
            self.write(template, {'form': form_data, 'new': True})


class PostHandler(AuthAwareRequestHandler):
    """
    Handles requests that expect a response that renders a single page
    comprising a blog post and its comments section.

    PostHandler handles GET requests and responds with a page comprising
    a blog posts and its comments, with appropriate options for mutating
    posts and comments, depending on the current user

    The GET method expects kwargs 'post_id' -- the identifier of the post
    to present
    """

    def get(self, **kwargs):
        template = jinja_env.get_template('post.html')
        post_id = kwargs['post_id']
        post = Post.get_by_id(int(post_id))

        # Retrieve all comments
        comments_query = Comment.query(
            Comment.post_id == int(post_id)).order(Comment.submitted)
        comments = [comment for comment in comments_query]

        # Discern anonymous browsers from users
        cookie = self.request.cookies.get('user')
        user = None
        has_liked = None
        if validate_user_cookie(cookie):
            user = cookie.split("|")[0]
            has_liked = user_has_liked_post(user, post_id)

        # If this post exists, render it (otherwise, 404)
        if post:
            self.write(template, {'post': post, 'comments': comments,
                                  'current_user': user,
                                  'has_liked': has_liked})
        else:
            webapp2.abort(404)


class UpdateHandler(AuthAwareRequestHandler):
    """
    Handles the mutating of existing posts

    UpdateHandler implements handlers for GET and POST requests.

    A GET request to UpdateHandler responds with a pre-populated form that a
    user will use to edit their post.

    A POST request to UpdateHandler will submit the edited post to the
    datastore.

    In each case, a user must be signed in and must be the author of a given
    post. As well, both methods expect kwargs 'post_id' -- the identifier of
    the post to update.
    """

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        template = jinja_env.get_template('new-post.html')
        post = Post().get_by_id(int(kwargs['post_id']))
        self.write(template, {'form': {'title': post.title,
                                       'content': post.content},
                              'new': False})

    @user_is_signed_in
    @user_is_author
    def post(self, **kwargs):
        post_id = kwargs['post_id']
        title = self.request.POST['title']
        content = self.request.POST['content']

        # Check that title and content are non empty and add the post to the
        # datastore; otherwise, rerender the form with validation errors
        if title != '' and content != '':
            post = Post.get_by_id(int(post_id))
            post.title = title
            post.content = content
            post.put()

            self.redirect('/posts/' + post_id)

        else:
            template = jinja_env.get_template('new-post.html')
            form_data = {'title': title, 'content': content, 'error': True}
            self.write(template, {'form': form_data, 'new': True})


class DeleteHandler(webapp2.RequestHandler):
    """
    Handles the deletion of posts.

    DeleteHandler responds to GET requests by deleting a post with a given
    identifier (cascading that delete through each comment) from the datastore
    and redirecting to the main page.

    The GET method expects kwargs 'post_id' -- the identifier of the post to
    delete
    """

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        post_id = kwargs['post_id']
        Post.get_by_id(int(post_id)).key.delete()

        # Cascade the delete to all comments associated with the post
        comments = Comment.query(Comment.post_id == int(post_id))
        for comment in comments:
            comment.key.delete()
        self.redirect('/')


class LikeHandler(webapp2.RequestHandler):
    """
    Handles the 'liking' of posts

    LikeHandler responds to GET requests by adding a given user to the
    list of users that have liked a post, then redirecting to the posts' page

    The GET method expects kwargs 'post_id' and 'user_id' -- the identifiers of
    the post that has been liked, and the user that liked it
    """

    @user_is_signed_in
    @user_is_not_author
    def get(self, **kwargs):

        post = Post.get_by_id(int(kwargs['post_id']))
        if not user_has_liked_post(kwargs['user_id'], kwargs['post_id']):
            post.liked_by.append(kwargs['user_id'])
            post.put()
        else:
            post.liked_by.remove(kwargs['user_id'])
            post.put()

        self.redirect('/posts/%s' % kwargs['post_id'])
