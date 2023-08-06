from tangled.web import Resource, config


TITLES = {
    400: "Bad request",
    403: "You're not allowed to do that",
    404: "That page wasn't found",
    405: "That operation isn't supported",
    500: 'Something unexpected happened',
}


DETAILS = {

}


class Error(Resource):

    @config('text/html', template='error.mako')
    def GET(self):
        request = self.request
        response = request.response
        if response.status_code == 401:
            came_from = request.url
            location = request.make_url(
                '/sign-in', query={'came_from': came_from})
            request.abort(307, location=location)
        else:
            return {
                'title': TITLES.get(response.status_code, 'Error'),
                'detail': DETAILS.get(response.status_code, '')
            }
