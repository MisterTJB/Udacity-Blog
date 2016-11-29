from google.appengine.ext import ndb as db


class Comment(db.Model):
    """
    Models a Comment on a blog.

    Attributes:
        content: The copy for a blog post
        submitted: The submission datetime for a blog post. Set automatically
            on insert, but not on update
        submitter: The username of the user that posted the comment
        post_id: The identifier for the post that this comment is associated
            with
    """
    content = db.TextProperty()
    submitted = db.DateTimeProperty(auto_now_add=True)
    submitter = db.StringProperty()
    post_id = db.IntegerProperty()
