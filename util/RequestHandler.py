import webapp2
from util.auth import validate_user_cookie

class AuthAwareRequestHandler(webapp2.RequestHandler):

    def write(self, template, context):
        cookie = self.request.cookies.get('user')
        signed_in = validate_user_cookie(cookie)
        context['signed_in'] = signed_in
        self.response.out.write(template.render(context=context))