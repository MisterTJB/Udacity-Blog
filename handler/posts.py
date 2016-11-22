import webapp2
import os
from model.post import Post
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader = FileSystemLoader(template_dir), autoescape=True)


def post_age_formatter(creation_timestamp):
    return creation_timestamp.date().isoformat()

jinja_env.filters['post_age'] = post_age_formatter


class FrontPageHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('posts.html')

    def get(self):
        self.response.out.write(self.template.render(posts=Post().query()))

class NewPostFormHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('new_post.html')

    def get(self):
        form_data = {'title': '', 'content': '', 'error': False}
        self.response.out.write(self.template.render(form=form_data))

class PostsHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('new_post.html')

    def post(self):
        title = self.request.POST['title']
        content = self.request.POST['content']

        if title != '' and content != '':
            new_post = Post(title=title, content=content, submitter="TEST")
            new_post_key = new_post.put()
            new_post_id = new_post_key.id()
            self.redirect('/posts/%d' % new_post_id)
        else:
            form_data = {'title': title, 'content': content, 'error': True}
            self.response.out.write(self.template.render(form=form_data))

class PostHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('post.html')

    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.response.out.write(self.template.render(post=post))