from tangled.web import Resource

from ..resources.entry import Entries, Entry


class Home(Resource):

    def GET(self):
        app = self.app
        req = self.request
        home_slug = app.settings['site.home']
        if home_slug:
            resource = Entry(app, req, urlvars={'id': home_slug})
        else:
            resource = Entries(app, req)
        del req.resource_config
        req.resource = resource
        return resource.GET()
