import webapp2
from util.auth import validate_user_cookie


class AuthAwareRequestHandler(webapp2.RequestHandler):
    """
    An AuthAwareRequestHandler implements one additional method -- write --
    that augments any template data with a 'signed_in' key-value that indicates
    whether a user is currently signed in.

    """

    def write(self, template, context={}):
        """
        Respond to a request by rendering a template with a given context

        Args:
            template: The Jinja2 template to render
            context: A dictionary of variables to render in the Jinja2 template
        """
        cookie = self.request.cookies.get('user')
        signed_in = validate_user_cookie(cookie)
        context['signed_in'] = signed_in
        self.response.out.write(template.render(context=context))