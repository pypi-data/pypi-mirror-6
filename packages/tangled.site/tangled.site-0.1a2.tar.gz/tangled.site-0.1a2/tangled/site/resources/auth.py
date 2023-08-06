import logging

from tangled.web import Resource, config
from tangled.site import auth


log = logging.getLogger(__name__)


class SignUp(Resource):

    @config('text/html', template='auth/sign-up.mako')
    def GET(self):
        """Show sign-up form."""
        req = self.request
        if req.user:
            location = req.make_url('/profile')
            req.update_response(status=307, location=location)
        else:
            return {}

    @config('*/*', status=303, location='/profile', not_logged_in=True)
    def POST(self):
        req = self.request
        username = req.POST['username']
        email = req.POST['email']
        password = req.POST['password']
        user_id = auth.sign_up(req, email, password, username)
        if user_id is not None:
            req.authenticator.remember(user_id)
            req.expire_csrf_token()
        else:
            location = req.make_url('/sign-up')
            req.response.location = location
            req.flash('Could not sign up')


class SignIn(Resource):

    @config('text/html', template='/auth/sign-in.mako')
    def GET(self):
        if self.request.user:
            req = self.request
            location = req.make_url('/profile')
            req.update_response(status=307, location=location)
        else:
            return {}

    @config('*/*', status=303, location='CAME_FROM', not_logged_in=True)
    def POST(self):
        req = self.request
        user_id = req.POST['username']
        password = req.POST['password']
        canonical_user_id = auth.check_credentials(req, user_id, password)
        if canonical_user_id is not None:
            req.authenticator.remember(canonical_user_id)
            came_from = req.POST['came_from']
            if came_from.endswith('/sign-in'):
                del req.POST['came_from']
            req.expire_csrf_token()
        else:
            location = req.make_url('/sign-in')
            req.response.location = location
            req.flash('Could not sign in')


class SignOut(Resource):

    # TODO: Redirect to /logged-out
    @config('*/*', status=303, location='/', requires_authentication=True)
    def POST(self):
        req = self.request
        req.authenticator.forget()
        req.expire_csrf_token()
        req.session.clear()
        req.session.save()
        log.debug('Cleared session: {}'.format(req.session))
        req.flash('You have been signed out')
