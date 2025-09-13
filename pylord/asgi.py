from starlette.requests import Request as ASGIRequest
import inspect
from parse import parse
from jinja2 import Environment, FileSystemLoader
import os
from .asgi_response import Response
from starlette.staticfiles import StaticFiles


class PyLordASGI:

    def __init__(self, templates_dir='templates', static_dir="static"):
        self.routes = {}
        self.exception_handler = None

        if templates_dir:
            self.template_env = Environment(
                loader=FileSystemLoader(os.path.abspath(templates_dir))
            )
        else:
            self.template_env = None

        self.static_dir = static_dir

        if static_dir:
            self.static_app = StaticFiles(directory=static_dir)
        else:
            self.static_app = None

    async def __call__(self, scope, receive, send):
        if self.static_app and scope['path'].startswith('/static'):
            return await self.static_app(scope, receive, send)

        request = ASGIRequest(scope, receive)
        response = await self.handle_asgi_request(request)
        await response(scope, receive, send)

    async def handle_asgi_request(self, request):
        response = Response()

        handler_data, kwargs = self.find_handler(request)
        if handler_data is not None:
            handler = handler_data["handler"]
            allowed_methods = handler_data["methods"]

            if inspect.isclass(handler):
                handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    return self.method_not_allowed_response(response)
            else:
                if request.method.lower() not in allowed_methods:
                    return self.method_not_allowed_response(response)

            try:
                result = handler(request, response, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
            except Exception as e:
                if self.exception_handler is not None:
                    await self.exception_handler(request, response, e)
                else:
                    raise e
        else:
            self.default_response(response)

        return response

    def default_response(self, response):
        response.status_code = 404
        response.text = 'Not Found'

    def method_not_allowed_response(self, response):
        response.status_code = 405
        response.text = "Method not allowed"
        return response

    def add_route(self, path, handler, methods=None):
        assert path not in self.routes, "Duplicate Route. Please Change The URL"

        if methods is None:
            methods = ["post", "put", "patch", "options", "delete", "get", "head", "connect", "trace"]

        self.routes[path] = {"handler": handler, "methods": methods}
        return handler

    def route(self, path, methods=None):
        def wrapper(handler):
            self.add_route(path, handler, methods)
            return handler
        return wrapper

    def find_handler(self, request):
        for path, handler_data in self.routes.items():
            parsed_result = parse(path, request.scope["path"])
            if parsed_result is not None:
                return handler_data, parsed_result.named

        return None, None

    def template(self, template_name, context=None):
        if not self.template_env:
            raise RuntimeError("Templates Not Configured.")
        if context is None:
            context = {}

        return self.template_env.get_template(template_name).render(**context)

    def add_exception_handler(self, handler):
        self.exception_handler = handler



