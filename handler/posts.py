import webapp2
import os
from util.RequestHandler import AuthAwareRequestHandler
from model.post import Post
from model.comment import Comment
from util.auth import validate_user_cookie
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader = FileSystemLoader(template_dir), autoescape=True)


def post_age_formatter(creation_timestamp):
    return creation_timestamp.date().isoformat()

def trim_to_two_sentences(post):
    trimmed_post = post.split(".")[:3]
    return '. '.join(trimmed_post) + "..."

jinja_env.filters['post_age'] = post_age_formatter
jinja_env.filters['trim'] = trim_to_two_sentences

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


class FrontPageHandler(AuthAwareRequestHandler):
    template = jinja_env.get_template('posts.html')

    def get(self):
        self.write(self.template, {'posts': Post().query().order(-Post.likes, -Post.submitted)})

class NewPostFormHandler(AuthAwareRequestHandler):

    @user_is_signed_in
    def get(self, **kwargs):
        self.write(jinja_env.get_template('new-post.html'),
                   {'form': {'title': '', 'content': '', 'error': False}, 'new': True})


class PostsHandler(AuthAwareRequestHandler):


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
            template = jinja_env.get_template('new-post.html')
            form_data = {'title': title, 'content': content, 'error': True}
            self.write(template, {'form': form_data, 'new': True})

class PostHandler(AuthAwareRequestHandler):


    def get(self, **kwargs):
        template = jinja_env.get_template('post.html')
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
            self.write(template, {'post': post, 'comments': comments,
                                  'current_user': user,
                                  'has_liked': has_liked})
        else:
            webapp2.abort(404)

class UpdateHandler(AuthAwareRequestHandler):

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

    @user_is_signed_in
    @user_is_author
    def get(self, **kwargs):
        post_id = kwargs['post_id']
        Post.get_by_id(int(post_id)).key.delete()

        comments = Comment.query(Comment.post_id == int(post_id))
        for comment in comments:
            comment.key.delete()
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