from webob import Request, Response


class PySauronApp:
    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):

        user_agent = request.environ.get("HTTP_USER_AGENT", "user agent not found")

        response = Response()
        response.text = f"hello my friend: {user_agent}"

        return response
