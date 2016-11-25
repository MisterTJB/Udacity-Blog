from google.appengine.ext import ndb as db

class Comment(db.Model):
  content = db.TextProperty()
  submitted = db.DateTimeProperty(auto_now_add=True)
  submitter = db.StringProperty()
  post_id = db.IntegerProperty()