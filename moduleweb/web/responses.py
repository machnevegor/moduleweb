from aiohttp import web
from json import dumps
from aiohttp_jinja2 import render_template

from .tools import validate_type


@web.middleware
async def response_processor(request: object, handler: object):
    response = await handler(request)
    if validate_type(response, [
        "MW-TextResponse",
        "MW-RenderResponse",
        "MW-FileResponse",
        "MW-RedirectResponse"
    ]):
        return response.parse(request)
    return response


class BaseResponse:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.cookies = {}
        self.headers = {}

    def prepare(self, response: object):
        for name, value in self.cookies.items():
            response.cookies[name] = value
        for name, value in self.headers.items():
            response.headers[name] = value


class Text(BaseResponse):
    def __init__(self, data: str, content_type: str, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.content_type = content_type

    def __repr__(self):
        return f"<MW-TextResponse content_type='{self.content_type}'>"

    def parse(self, *args, **kwargs):
        response = web.Response(
            text=self.data,
            content_type=self.content_type
                         ** self.kwargs
        )
        self.prepare(response)
        return response


def text(data: str, *, content_type="text/plain", **kwargs):
    return Text(data, content_type, **kwargs)


def json(data: dict, *, content_type="application/json", **kwargs):
    return Text(dumps(data), content_type, **kwargs)


class Render(BaseResponse):
    def __init__(self, entry_point: str, context: dict, **kwargs):
        super().__init__(**kwargs)
        self.entry_point = entry_point
        self.context = context

    def __repr__(self):
        return f"<MW-RenderResponse entry_point='{self.entry_point}'>"

    def parse(self, request: object, *args, **kwargs):
        response = render_template(
            self.entry_point,
            request,
            self.context,
            **self.kwargs
        )
        self.prepare(response)
        return response


def render(entry_point: str, context: dict = {}, **kwargs):
    return Render(entry_point, context, **kwargs)


class File(BaseResponse):
    def __init__(self, path: str, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    def __repr__(self):
        return f"<MW-FileResponse path='{self.path}'>"

    def parse(self, *args, **kwargs):
        response = web.FileResponse(
            path=self.path,
            **self.kwargs
        )
        self.prepare(response)
        return response


def file(path: str, **kwargs):
    return File(path, **kwargs)


class Redirect(BaseResponse):
    def __init__(self, location: str, **kwargs):
        super().__init__(**kwargs)
        self.location = location

    def __repr__(self):
        return f"<MW-RedirectResponse location='{self.location}'>"

    def parse(self, *args, **kwargs):
        response = web.HTTPSeeOther(
            location=self.location,
            **self.kwargs
        )
        self.prepare(response)
        return response


def redirect(location: str, **kwargs):
    return Redirect(location, **kwargs)
