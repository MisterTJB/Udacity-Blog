import webapp2
import os
from model.user import User
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader = FileSystemLoader(template_dir), autoescape=True)

class SignUpHandler(webapp2.RequestHandler):

    # Handler for the form
    def get(self):
        self.response.write('Will render sign in form')

    # Handler for form submission
    def post(self):
        self.response.write('Will process signin form')

class SignInHandler(webapp2.RequestHandler):

    def post(self):
        self.response.write('Will sign in user')

class SignOutHandler(webapp2.RequestHandler):

    def get(self):
        self.response.write('Will sign user out')