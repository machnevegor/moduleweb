from aiohttp import web
from typing import Optional, Dict, Any
from json import dumps
from aiohttp_jinja2 import render_template_async, setup
from asyncio import iscoroutinefunction, coroutine
from jinja2 import FileSystemLoader, PrefixLoader

__all__ = ("text", "json", "render", "file", "redirect", "stream", "socket")


class BaseResponse:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.cookies = {}
        self.headers = {}

    async def __call__(self, request: web.Request) -> web.StreamResponse:
        response = await self.convert(request)
        for name, value in self.cookies.items():
            response.cookies[name] = value
        for name, value in self.headers.items():
            response.headers[name] = value
        return response


class Text(BaseResponse):
    def __init__(self, data: str, content_type: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.content_type = content_type

    def __repr__(self) -> str:
        return f"<Text content_type='{self.content_type}'>"

    async def convert(self, *_) -> web.StreamResponse:
        return web.Response(
            text=self.data,
            content_type=self.content_type,
            **self.kwargs
        )


def text(data: str, *, content_type: Optional[str] = "text/plain", **kwargs: Any) -> "Text":
    return Text(data, content_type, **kwargs)


def json(data: dict, *, content_type: Optional[str] = "application/json", **kwargs: Any) -> "Text":
    return Text(dumps(data), content_type, **kwargs)


class Render(BaseResponse):
    def __init__(self, entry_point: str, context: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.entry_point = entry_point
        self.context = context

    def __repr__(self) -> str:
        return f"<Render entry_point='{self.entry_point}'>"

    async def convert(self, request: web.Request) -> web.StreamResponse:
        return await render_template_async(
            self.entry_point,
            request,
            self.context,
            **self.kwargs
        )


def render(entry_point: str, context: Optional[Dict[str, Any]] = {}, **kwargs: Any) -> "Render":
    return Render(entry_point, context, **kwargs)


class File(BaseResponse):
    def __init__(self, path: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.path = path

    def __repr__(self) -> str:
        return f"<File path='{self.path}'>"

    async def convert(self, *_) -> web.StreamResponse:
        return web.FileResponse(self.path, **self.kwargs)


def file(path: str, **kwargs: Any) -> "File":
    return File(path, **kwargs)


class Redirect(BaseResponse):
    def __init__(self, uri: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.uri = uri

    def __repr__(self) -> str:
        return f"<Redirect uri='{self.uri}'>"

    async def convert(self, *_) -> web.HTTPSeeOther:
        return web.HTTPSeeOther(self.uri, **self.kwargs)


def redirect(uri: str, **kwargs: Any) -> "Redirect":
    return Redirect(uri, **kwargs)


class Stream(BaseResponse):
    def __init__(self, handler: object, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.handler = handler

    def __repr__(self) -> str:
        return f"<Stream handler='{self.handler.__name__}'>"

    async def convert(self, request: web.Request) -> web.StreamResponse:
        response = web.StreamResponse(**self.kwargs)
        await response.prepare(request)

        if not iscoroutinefunction(self.handler):
            self.handler = coroutine(self.handler)
        await self.handler(request, response)

        return response


def stream(handler: object, **kwargs: Any) -> "Stream":
    return Stream(handler, **kwargs)


class WebSocket(BaseResponse):
    def __init__(self, handler: object, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.handler = handler

    def __repr__(self) -> str:
        return f"<WebSocket handler='{self.handler.__name__}'>"

    async def convert(self, request: web.Request) -> web.WebSocketResponse:
        websocket = web.WebSocketResponse(**self.kwargs)
        await websocket.prepare(request)

        if not iscoroutinefunction(self.handler):
            self.handler = coroutine(self.handler)
        await self.handler(request, websocket)

        return websocket


def socket(handler: object, **kwargs: Any) -> "WebSocket":
    return WebSocket(handler, **kwargs)


@web.middleware
async def response_processor(request: web.Request, handler: object) -> Any:
    response = await handler(request)
    if isinstance(response, BaseResponse):
        return await response(request)
    return response


async def render_setuper(app: "App") -> None:
    directory_prefixes = {}
    for resource in app.router._resources:
        if isinstance(resource, web.StaticResource):
            directory = FileSystemLoader(resource._directory)
            directory_prefixes[resource._prefix[1:]] = directory
    setup(app, loader=PrefixLoader(directory_prefixes))
