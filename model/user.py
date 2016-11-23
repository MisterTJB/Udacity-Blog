from google.appengine.ext import ndb as db
from hashlib import sha512

class PasswordProperty(db.StringProperty):

    salt = '4c93dd3e'

    def _validate(self, value):
        if not isinstance(value, (str)):
            raise TypeError('expected a string, got %s' % repr(value))

    def _to_base_type(self, value):
        return sha512(value + PasswordProperty.salt).hexdigest()

    def _from_base_type(self, value):
        return value

class User(db.Model):
  username = db.StringProperty()
  password = PasswordProperty()