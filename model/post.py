from google.appengine.ext import ndb as db

class Post(db.Model):
  title = db.StringProperty()
  liked_by = db.StringProperty(repeated=True)
  likes = db.ComputedProperty(lambda self: len(self.liked_by) + 1)
  content = db.TextProperty()
  submitted = db.DateTimeProperty(auto_now_add=True)
  submitter = db.StringProperty()
