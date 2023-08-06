from tangled.web import Resource, config

from .. import auth, model


@config('*/*', requires_authentication=True)
class User(Resource):

    @config('*/*', status=303, location='REFERER')
    def PUT(self):
        req = self.request
        user = req.user

        authorized = (
            user.id == int(self.urlvars['id']) or
            user.has_permission('update_user'))
        if not authorized:
            req.abort(403)

        params = self.app.get_settings(req.POST, 'user.')
        if not params:
            req.abort(400)

        if 'password' in params:
            current_password = params.pop('current_password')
            if not auth.passwords_equal(current_password, user.password):
                req.flash('Incorrect current password', 'error')
                return

            new_password = params.pop('password')
            confirm_password = params.pop('confirm_password')

            if new_password != confirm_password:
                req.flash("Passwords don't match", 'error')
                return

            if len(new_password) < 4:
                req.flash('That password is too short', 'error')
                return

            if not auth.passwords_equal(new_password, user.password):
                user.password = new_password
                req.flash('Password changed')

        if 'username' in params:
            username = params.pop('username')
            q = req.db_session.query(model.User.id)
            q = q.filter_by(username=username)
            user_id_for_username = q.scalar()
            if user_id_for_username is None:
                req.flash('Username updated')
                user.username = username
            elif user_id_for_username != user.id:
                req.flash('Username unavailable', 'error')

        if 'email' in params:
            email = params.pop('email')
            q = req.db_session.query(model.User.id)
            q = q.filter_by(email=email)
            user_id_for_email = q.scalar()
            if user_id_for_email is None:
                req.flash('Email address updated')
                user.email = email
            elif user_id_for_email != user.id:
                req.flash('Email address unavailable', 'error')

        # Set all other attributes directly
        for k, v in params.items():
            setattr(user, k, v)
            req.flash('{} updated'.format(k.title()))

    @config('*/*', permission='delete_user', status=303, location='REFERER')
    def DELETE(self):
        req = self.request
        user = req.db_session.query(model.User).get(self.urlvars['id'])
        if user.id == req.user.id:
            req.flash(
                "You can't delete your own account while you are signed in")
            req.abort(400)
        else:
            req.db_session.delete(user)


@config('*/*', requires_authentication=True)
class Profile(Resource):

    @config('text/html', template='profile.mako')
    def GET(self):
        return {}
