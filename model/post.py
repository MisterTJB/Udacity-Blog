from google.appengine.ext import ndb as db

class Post(db.Model):
  title = db.StringProperty()
  votes = db.IntegerProperty()
  submitted = db.DateTimeProperty(auto_now=True)
  submitter = db.IntegerProperty()
