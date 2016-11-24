import webapp2
import os
import util.auth as auth
from model.user import User
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader = FileSystemLoader(template_dir), autoescape=True)

class SignUpHandler(webapp2.RequestHandler):

    # Handler for the form
    def get(self):
        template = jinja_env.get_template('register.html')
        self.response.write(template.render())

    # Handler for form submission
    def post(self):

        username = self.request.POST['username']
        password = self.request.POST['password']

        template = jinja_env.get_template('register.html')
        if username == '':
            self.response.write(template.render(username_blank=True))
        elif User.get_by_id(username):
            self.response.write(template.render(username_taken=True))
        elif password == '':
            self.response.write(template.render(password_blank=True, username=username))
        else:
            User(id=username, password=str(password)).put()
            self.response.set_cookie('user', value=auth.create_user_cookie(username))
            self.redirect('/users/welcome')

class WelcomeHandler(webapp2.RequestHandler):

    def get(self):

        template = jinja_env.get_template('welcome.html')
        user_cookie = self.request.cookies.get('user')

        if user_cookie and len(user_cookie.split('|')) == 2:
            user = user_cookie.split('|')[0]
            self.response.write(template.render(username=user))
        else:
            self.redirect('/users/new')


class SignInHandler(webapp2.RequestHandler):

    def get(self):
        template = jinja_env.get_template('sign-in.html')
        self.response.write(template.render())

    def post(self):
        username = self.request.POST['username']
        password = self.request.POST['password']

        def check_password():
            from hashlib import sha512
            from model.user import salt
            user_data = User().get_by_id(username)
            if user_data:
                return user_data.password == sha512(password + salt).hexdigest()
            return False

        if check_password():
            self.response.set_cookie('user', value=auth.create_user_cookie(username))
            self.redirect('/users/welcome')
        else:
            template = jinja_env.get_template('sign-in.html')
            self.response.write(template.render(invalid_credentials=True, username=username))

class SignOutHandler(webapp2.RequestHandler):

    def get(self):
        self.response.delete_cookie('user')
        self.redirect('/users/in')