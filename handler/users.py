import webapp2
import os
import util.auth as auth
from util.RequestHandler import AuthAwareRequestHandler
from model.user import User
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), '../template')
jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)


class SignUpHandler(AuthAwareRequestHandler):
    """
    Handles the signup process

    SignUpHandler responds to GET and POST requests.

    A GET request receives a registration form as a response.

    POST requests handle the form data from the registration form, check for
    validity, and either: re-render the form with validation errors, or add
    the data to the datastore and redirect to the welcome page.

    A valid registration is considered to be one in which:

        i) The proposed username is nonempty
        ii) The proposed password is nonempty
        iii) The proposed username is not already taken
    """

    def get(self):
        template = jinja_env.get_template('register.html')
        self.write(template)

    def post(self):
        template = jinja_env.get_template('register.html')

        username = self.request.POST['username']
        password = self.request.POST['password']

        if username == '':
            self.write(template, {'username_blank': True})
        elif User.get_by_id(username):
            self.write(template, {'username_taken': True,
                                  'username': username})
        elif password == '':
            self.write(template, {'password_blank': True,
                                  'username': username})
        else:
            User(id=username, password=str(password)).put()
            self.response.set_cookie('user',
                                     value=auth.create_user_cookie(username))
            self.redirect('/users/welcome')


class WelcomeHandler(AuthAwareRequestHandler):
    """
    Handles requests to the welcome page

    WelcomeHandler reponds to GET requests by rendering the phrase
    "Welcome, [username]". If a user is not signed in, the user is redirected
    to the sign up page.
    """

    def get(self):

        template = jinja_env.get_template('welcome.html')
        user_cookie = self.request.cookies.get('user')

        if user_cookie and len(user_cookie.split('|')) == 2:
            user = user_cookie.split('|')[0]
            self.write(template, {'username': user})
        else:
            self.redirect('/users/new')


class SignInHandler(AuthAwareRequestHandler):
    """
    Handles the login process

    SignInHandler responds to GET requests (which render the sign in form)
    and POST requests (which handle the submitted sign in form).

    The POST handler will check the user's credentials against the datastore.
    If their credentials are valid, they are redirected to the welcome page;
    otherwise, the form is re-rendered with validation errors.
    """

    def get(self):
        template = jinja_env.get_template('sign-in.html')
        self.write(template)

    def post(self):
        from model.user import check_password

        username = self.request.POST['username']
        password = self.request.POST['password']

        # If a password is valid, set the 'user' cookie and redirect
        # Otherwise, re-render the form with validation errors
        if check_password(username, password):
            self.response.set_cookie('user',
                                     value=auth.create_user_cookie(username))
            self.redirect('/users/welcome')
        else:
            template = jinja_env.get_template('sign-in.html')
            self.write(template, {'invalid_credentials': True,
                                  'username': username})


class SignOutHandler(webapp2.RequestHandler):
    """
    Handle the sign out process

    SignOutHandler responds to GET requests by invalidating a user's user
    cookie and redirecting to the sign in page
    """

    def get(self):
        self.response.delete_cookie('user')
        self.redirect('/users/in')
