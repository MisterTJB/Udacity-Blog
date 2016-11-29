from google.appengine.ext import ndb as db
from hashlib import sha512

salt = '4c93dd3e'


def check_password(username, password):
    """
    Salt and hash a password, and check against the datastore

    Returns:
        True if the credentials are valid
    """

    if not username:
        return False

    user_data = User().get_by_id(username)
    if user_data:
        return user_data.password == sha512(password + salt).hexdigest()
    return False


class PasswordProperty(db.StringProperty):
    """
    A PasswordProperty obfuscates a password so that that password may
    be stored securely.
    """

    def _validate(self, value):
        if not isinstance(value, str):
            raise TypeError('expected a string, got %s' % repr(value))

    def _to_base_type(self, value):
        return sha512(value + salt).hexdigest()

    def _from_base_type(self, value):
        return value


class User(db.Model):
    """
    Models a user

    Attributes:
        id = A user's username
        password = A user's password
    """

    password = PasswordProperty()
