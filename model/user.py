from google.appengine.ext import ndb as db
from hashlib import sha512

salt = '4c93dd3e'

class PasswordProperty(db.StringProperty):

    def _validate(self, value):
        if not isinstance(value, (str)):
            raise TypeError('expected a string, got %s' % repr(value))

    def _to_base_type(self, value):
        return sha512(value + salt).hexdigest()

    def _from_base_type(self, value):
        return value

class User(db.Model):
  password = PasswordProperty()