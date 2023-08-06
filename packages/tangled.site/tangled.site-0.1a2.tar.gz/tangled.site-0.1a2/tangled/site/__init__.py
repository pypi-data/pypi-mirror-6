import os

from tangled.decorators import reify
from tangled.web.events import TemplateContextCreated

from . import model


def include(app):
    # The theme can be specified as...
    #     - an absolute file system path
    #     - an asset path (e.g.: 'tangled.site:themes/default')
    #     - relative to tangled.site:themes (e.g.: 'default')
    theme = app.settings.get('site.theme', 'default')

    if os.path.isabs(theme):
        theme_directory = theme
    else:
        if ':' in theme:
            theme_directory = theme
        else:
            theme_directory = 'tangled.site:themes/{}'.format(theme)

    static_directory = os.path.join(theme_directory, 'static')
    app.mount_static_directory('static', static_directory)

    template_directory = os.path.join(theme_directory, 'templates')
    app.settings['mako.lookup.directories'] = template_directory

    # Home
    app.mount_resource('home', '.resources.home:Home', '/')

    # Auth
    app.mount_resource('sign-up', '.resources.auth:SignUp', '/sign-up')
    app.mount_resource('sign-in', '.resources.auth:SignIn', '/sign-in')
    app.mount_resource('sign-out', '.resources.auth:SignOut', '/sign-out')

    # Admin
    admin = app.mount_resource('admin', '.resources.admin:Admin', '/admin')
    admin.mount('users', 'users', method_name='users')
    admin.mount('meta', 'meta', factory='.resources.admin:Meta')

    # Users
    app.mount_resource('user', '.resources.user:User', '/user/<id>')
    app.mount_resource('profile', '.resources.user:Profile', '/profile')

    # Entries
    entries_settings = app.get_settings(prefix='site.entries.')
    path = entries_settings['path']
    name = path.strip('/')
    app.mount_resource(name, '.resources.entry:Entries', path)

    app.mount_resource('entries', '.resources.entry:Entries', '/entries')
    app.mount_resource(
        'new_entry', '.resources.entry:NewEntry', '/entries/new')

    # Entry
    app.mount_resource('entry', '.resources.entry:Entry', '/entry/<id>')
    app.mount_resource(
        'edit_entry', '.resources.entry:EditEntry', '/entry/<id>/edit')

    app.mount_resource(
        'page', '.resources.entry:Entry', '/<id>', methods='GET')

    def update_template_context(event):
        request = event.request
        q = request.db_session.query(model.Entry)
        q = q.filter_by(published=True, is_page=True)
        event.context['pages'] = q.all()
        event.context['user'] = request.user

    app.add_subscriber(TemplateContextCreated, update_template_context)

    @reify
    def user(request):
        user_id = request.authenticator.user_id
        if user_id is None:
            return None
        q = request.db_session.query(model.User)
        return q.get(user_id)

    app.add_request_attribute(user)

    def format_datetime(datetime):
        if not datetime:
            return datetime
        day_of_month = datetime.strftime('%b').lstrip('0')
        hour = datetime.strftime('%I').lstrip('0')
        am_pm = datetime.strftime('%p').lower()
        return datetime.strftime(
            '%a, {d} %d, %Y at {I}:%M{p}'
            .format(d=day_of_month, I=hour, p=am_pm))

    app.add_helper(format_datetime, static=True)

    app.scan('.resources')
