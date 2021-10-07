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

    def prepare(self, request: web.Request) -> web.StreamResponse:
        response = self.submit(request)
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

    def submit(self, *_) -> web.StreamResponse:
        return web.Response(
            text=self.data,
            content_type=self.content_type,
            **self.kwargs
        )


def text(data: str, *, content_type: Optional[str] = "text/plain", **kwargs) -> "TextResponse":
    return Text(data, content_type, **kwargs)


def json(data: dict, *, content_type: Optional[str] = "application/json", **kwargs) -> "TextResponse":
    return Text(dumps(data), content_type, **kwargs)


class Render(BaseResponse):
    def __init__(self, entry_point: str, context: Dict[str, Any], **kwargs) -> None:
        super().__init__(**kwargs)
        self.entry_point = entry_point
        self.context = context

    def __repr__(self) -> str:
        return f"<RenderResponse entry_point='{self.entry_point}'>"

    def submit(self, request: web.Request) -> web.StreamResponse:
        return render_template(
            self.entry_point,
            request,
            self.context,
            **self.kwargs
        )


def render(entry_point: str, context: Optional[Dict[str, Any]] = {}, **kwargs) -> "RenderResponse":
    return Render(entry_point, context, **kwargs)


class File(BaseResponse):
    def __init__(self, path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.path = path

    def __repr__(self) -> str:
        return f"<FileResponse path='{self.path}'>"

    def submit(self, *_) -> web.StreamResponse:
        return web.FileResponse(self.path, **self.kwargs)


def file(path: str, **kwargs) -> "FileResponse":
    return File(path, **kwargs)


class Redirect(BaseResponse):
    def __init__(self, uri: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.uri = uri

    def __repr__(self) -> str:
        return f"<RedirectResponse uri='{self.uri}'>"

    def submit(self, *_) -> web.HTTPSeeOther:
        return web.HTTPSeeOther(self.uri, **self.kwargs)


def redirect(uri: str, **kwargs) -> "RedirectResponse":
    return Redirect(uri, **kwargs)


@web.middleware
async def response_processor(request: web.Request, handler: object) -> Any:
    response = await handler(request)
    if isinstance(response, BaseResponse):
        return response.prepare(request)
    return response


async def render_setuper(app: "ModularApplication") -> None:
    directory_prefixes = {}
    for resource in app.router._resources:
        if isinstance(resource, web.StaticResource):
            directory = FileSystemLoader(resource._directory)
            directory_prefixes[resource._prefix[1:]] = directory
    setup(app, loader=PrefixLoader(directory_prefixes))
