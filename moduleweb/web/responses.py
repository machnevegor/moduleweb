from aiohttp import web
from json import dumps
from aiohttp_jinja2 import render_template, setup
from jinja2 import FileSystemLoader, PrefixLoader


class BaseResponse:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.cookies = {}
        self.headers = {}

    def parse(self, request: object):
        response = self.respond(request)
        for name, value in self.cookies.items():
            response.cookies[name] = value
        for name, value in self.headers.items():
            response.headers[name] = value
        return response


class Text(BaseResponse):
    def __init__(self, data: str, content_type: str, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.content_type = content_type

    def __repr__(self):
        return f"<TextResponse content_type='{self.content_type}'>"

    def respond(self, *_):
        return web.Response(
            text=self.data,
            content_type=self.content_type,
            **self.kwargs
        )


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
        return f"<RenderResponse entry_point='{self.entry_point}'>"

    def respond(self, request: object):
        return render_template(
            self.entry_point,
            request,
            self.context,
            **self.kwargs
        )


def render(entry_point: str, context: dict = {}, **kwargs):
    return Render(entry_point, context, **kwargs)


class File(BaseResponse):
    def __init__(self, path: str, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    def __repr__(self):
        return f"<FileResponse path='{self.path}'>"

    def respond(self, *_):
        return web.FileResponse(self.path, **self.kwargs)


def file(path: str, **kwargs):
    return File(path, **kwargs)


class Redirect(BaseResponse):
    def __init__(self, location: str, **kwargs):
        super().__init__(**kwargs)
        self.location = location

    def __repr__(self):
        return f"<RedirectResponse location='{self.location}'>"

    def respond(self, *_):
        return web.HTTPSeeOther(self.location, **self.kwargs)


def redirect(location: str, **kwargs):
    return Redirect(location, **kwargs)


@web.middleware
async def response_processor(request: object, handler: object):
    response = await handler(request)
    if isinstance(response, BaseResponse):
        return response.parse(request)
    return response


async def setup_render(app: object):
    directory_prefixes = {}
    for resource in app.router.resources:
        if isinstance(resource, web.StaticResource):
            directory = FileSystemLoader(resource.directory)
            directory_prefixes[resource.prefix[1:]] = directory
    setup(app, loader=PrefixLoader(directory_prefixes))
