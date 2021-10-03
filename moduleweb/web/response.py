from aiohttp import web
from typing import Optional, Dict, Any
from json import dumps
from aiohttp_jinja2 import render_template, setup
from jinja2 import FileSystemLoader, PrefixLoader


class BaseResponse:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.cookies = {}
        self.headers = {}

    def parse(self, request: object) -> web.StreamResponse:
        response = self.respond(request)
        for name, value in self.cookies.items():
            response.cookies[name] = value
        for name, value in self.headers.items():
            response.headers[name] = value
        return response


class Text(BaseResponse):
    def __init__(self, data: str, content_type: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.content_type = content_type

    def __repr__(self) -> str:
        return f"<TextResponse content_type='{self.content_type}'>"

    def respond(self, *_) -> web.StreamResponse:
        return web.Response(
            text=self.data,
            content_type=self.content_type,
            **self.kwargs
        )


def text(data: str, *, content_type: Optional[str]="text/plain", **kwargs) -> Text:
    return Text(data, content_type, **kwargs)


def json(data: dict, *, content_type: Optional[str]="application/json", **kwargs) -> Text:
    return Text(dumps(data), content_type, **kwargs)


class Render(BaseResponse):
    def __init__(self, entry_point: str, context: Dict[str, Any], **kwargs) -> None:
        super().__init__(**kwargs)
        self.entry_point = entry_point
        self.context = context

    def __repr__(self) -> str:
        return f"<RenderResponse entry_point='{self.entry_point}'>"

    def respond(self, request: object) -> web.StreamResponse:
        return render_template(
            self.entry_point,
            request,
            self.context,
            **self.kwargs
        )


def render(entry_point: str, context: Optional[Dict[str, Any]] = {}, **kwargs) -> Render:
    return Render(entry_point, context, **kwargs)


class File(BaseResponse):
    def __init__(self, path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.path = path

    def __repr__(self) -> str:
        return f"<FileResponse path='{self.path}'>"

    def respond(self, *_) -> web.StreamResponse:
        return web.FileResponse(self.path, **self.kwargs)


def file(path: str, **kwargs) -> File:
    return File(path, **kwargs)


class Redirect(BaseResponse):
    def __init__(self, location: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.location = location

    def __repr__(self) -> str:
        return f"<RedirectResponse location='{self.location}'>"

    def respond(self, *_) -> web.HTTPSeeOther:
        return web.HTTPSeeOther(self.location, **self.kwargs)


def redirect(location: str, **kwargs) -> Redirect:
    return Redirect(location, **kwargs)


@web.middleware
async def response_processor(request: object, handler: object) -> Any:
    response = await handler(request)
    if isinstance(response, BaseResponse):
        return response.parse(request)
    return response


async def setup_render(app: App) -> None:
    directory_prefixes = {}
    for resource in app.router.resources:
        if isinstance(resource, web.StaticResource):
            directory = FileSystemLoader(resource.directory)
            directory_prefixes[resource.prefix[1:]] = directory
    setup(app, loader=PrefixLoader(directory_prefixes))
