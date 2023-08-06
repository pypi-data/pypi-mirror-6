from tangled.web import Resource, config
from tangled.web.abcs import AMountedResource

from ..model import User


@config('*/*', permission='admin')
class Admin(Resource):

    @config('text/html', template='admin/index.mako')
    def GET(self):
        mounted_resources = self.app.get_all(AMountedResource)
        resources = []
        for r in mounted_resources:
            if r.name.startswith('admin/'):
                resources.append(r)
        return {
            'resources': resources,
        }

    @config('text/html', template='admin/users.mako')
    def users(self):
        q = self.request.db_session.query(User)
        users = q.all()
        return {
            'users': users,
        }


@config('*/*', permission='sudo')
class Meta(Resource):

    """Metadata about the site that only superuses should see."""

    @config('text/html', template='admin/meta.mako')
    def GET(self):
        return {}
