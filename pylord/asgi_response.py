from starlette.responses import Response as AsgiResponse
import json


class Response:

    def __init__(self):
        self.html = None
        self.json = None
        self.content = b''
        self.text = None
        self.content_type = None
        self.status_code = 200

    def set_body_and_content_type(self):
        if self.json is not None:
            self.content = json.dumps(self.json).encode()
            self.content_type = "application/json"

        if self.html is not None:
            self.content = self.html.encode()
            self.content_type = "text/html"

        if self.text is not None:
            self.content = self.text
            self.content_type = "text/plain"

    def __call__(self, scope, receive, send):
        self.set_body_and_content_type()

        response = AsgiResponse(
                content=self.content, status_code=self.status_code, media_type=self.content_type
        )

        return response(scope, receive, send)
