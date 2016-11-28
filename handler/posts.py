import webapp2
import os
from model.post import Post
from model.comment import Comment
from util.auth import validate_user_cookie
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
        post_id = kwargs['post_id']
        post = Post().get_by_id(int(post_id))

        if post.submitter == user_id:
            fn(*args, **kwargs)
        else:
            self.redirect('/posts/' + kwargs['post_id'])

    return redirect_if_not_author

def user_is_not_author(fn):
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

def user_has_liked_post(user_id, post_id):
    post = Post.get_by_id(int(post_id))
    if post:
        return user_id in post.liked_by


class FrontPageHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('posts.html')

    def get(self):
        self.response.out.write(self.template.render(
            posts=Post().query().order(-Post.likes, -Post.submitted)))

class NewPostFormHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('new_post.html')

    @user_is_signed_in
    def get(self, **kwargs):
        form_data = {'title': '', 'content': '', 'error': False, 'new': True}
        self.response.out.write(self.template.render(form=form_data))

class PostsHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('new_post.html')

    @user_is_signed_in
    def post(self, **kwargs):
        title = self.request.POST['title']
        content = self.request.POST['content']
        submitter = self.request.cookies.get('user').split("|")[0]

        if title != '' and content != '':
            new_post = Post(title=title, content=content, submitter=submitter)
            new_post_key = new_post.put()
            new_post_id = new_post_key.id()
            self.redirect('/posts/%d' % new_post_id)
        else:
            form_data = {'title': title, 'content': content, 'error': True, 'new': True}
            self.response.out.write(self.template.render(form=form_data))

class PostHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('post.html')

    def get(self, **kwargs):
        post_id = kwargs['post_id']
        post = Post.get_by_id(int(post_id))
        comments_query = Comment.query(Comment.post_id == int(post_id)).order(Comment.submitted)
        comments = [comment for comment in comments_query]
        cookie = self.request.cookies.get('user')
        if validate_user_cookie(cookie):
            user = cookie.split("|")[0]
            has_liked = user_has_liked_post(user, post_id)
        else:
            user = None
            has_liked = None

        if post:
            self.response.out.write(self.template.render(post=post,
                                                         comments=comments,
                                                         current_user=user,
                                                         has_liked=has_liked))
        else:
            webapp2.abort(404)

class UpdateHandler(webapp2.RequestHandler):

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        template = jinja_env.get_template('new_post.html')
        post = Post().get_by_id(int(kwargs['post_id']))
        self.response.out.write(template.render(form={'title': post.title,
                                                      'content': post.content,
                                                      'new': False}))
    @user_is_signed_in
    @user_is_author
    def post(self, **kwargs):
        post_id = kwargs['post_id']
        title = self.request.POST['title']
        content = self.request.POST['content']

        post = Post.get_by_id(int(post_id))
        post.title = title
        post.content = content
        post.put()

        self.redirect('/posts/' + post_id)

class DeleteHandler(webapp2.RequestHandler):

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        post_id = kwargs['post_id']
        Post.get_by_id(int(post_id)).key.delete()
        self.redirect('/')

class LikeHandler(webapp2.RequestHandler):

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