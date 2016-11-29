from google.appengine.ext import ndb as db


class Post(db.Model):
    """
    Models a blog post

    Attributes:
        title: The title of the blog post
        content: The content of the blog post
        submitted: The submission datetime. Automatically set on insert, but
            not affected on update
        submitter: The username for the user that posted this Post
        liked_by: A repeated field comprising user_ids for users that have
            liked this post
        likes: A computed property equivalent to len(liked_by) + 1
    """
    title = db.StringProperty()
    content = db.TextProperty()
    submitted = db.DateTimeProperty(auto_now_add=True)
    submitter = db.StringProperty()
    liked_by = db.StringProperty(repeated=True)
    likes = db.ComputedProperty(lambda self: len(self.liked_by) + 1)
