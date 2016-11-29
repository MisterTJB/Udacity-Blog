import webapp2
import os
from model.comment import Comment
from model.post import Post
from util.auth import validate_user_cookie
from util.RequestHandler import AuthAwareRequestHandler
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader = FileSystemLoader(template_dir), autoescape=True)

def post_age_formatter(creation_timestamp):
    return creation_timestamp.date().isoformat()

jinja_env.filters['post_age'] = post_age_formatter


def user_is_author(fn):
    def redirect_if_not_author(*args, **kwargs):
        self = args[0]
        user_id = kwargs['user_id']
        comment_id = kwargs['comment_id']
        comment = Comment().get_by_id(int(comment_id))

        if comment and comment.submitter == user_id:
            fn(*args, **kwargs)
        elif comment:
            self.redirect('/posts/' + kwargs['post_id'])
        else:
            self.abort(404)

    return redirect_if_not_author


def user_is_signed_in(fn):
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

    @user_is_signed_in
    def post(self, **kwargs):
        post_id = kwargs['post_id']
        user_id = kwargs['user_id']
        content = self.request.POST['content']

        if post_id.isdigit():
            Comment(content=content, submitter=user_id, post_id=int(post_id)).put()
        self.redirect('/posts/' + post_id)


class UpdateCommentHandler(AuthAwareRequestHandler):

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        template = jinja_env.get_template('edit-form.html')
        post_id = kwargs['post_id']
        comment_id = kwargs['comment_id']

        post = Post.get_by_id(int(post_id))
        comments_query = Comment.query(Comment.post_id == int(post_id)).order(
            Comment.submitted)
        comments = [comment for comment in comments_query]

        if post:
            self.write(template, {'post': post, 'edit_comment_id': int(comment_id), 'comments': comments})
        else:
            self.abort(404)


    @user_is_signed_in
    @user_is_author
    def post(self, **kwargs):
        post_id = kwargs['post_id']
        comment_id = kwargs['comment_id']
        content = self.request.POST['content']

        comment = Comment.get_by_id(int(comment_id))
        comment.content = content
        comment.put()

        self.redirect('/posts/' + post_id)


class DeleteCommentHandler(webapp2.RequestHandler):

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        comment_id = kwargs['comment_id']
        post_id = kwargs['post_id']
        Comment().get_by_id(int(comment_id)).key.delete()
        self.redirect('/posts/' + post_id)


