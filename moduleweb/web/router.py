from attr import dataclass
from aiohttp import web, hdrs
from asyncio import iscoroutinefunction, coroutine
from typing import Dict, Any, Optional, List, Union

from .options import Template, Preroute

__all__ = ("Router",)

TYPE_COMMON = "COMMON"
TYPE_ERROR = "ERROR"


@dataclass(repr=False)
class Middleware:
    handler: object
    type: str

    def __repr__(self) -> str:
        return f"<Middleware type='{self.type}'>"

    @web.middleware
    async def common(self, request: web.Request, handler: object) -> Any:
        return await self.handler(request, handler)

    @web.middleware
    async def error(self, request: web.Request, handler: object) -> Any:
        try:
            return await handler(request)
        except web.HTTPException as exc:
            if exc.status != 404:
                raise
            return await self.handler(request)

    def register(self, app: "App") -> None:
        if not iscoroutinefunction(self.handler):
            self.handler = coroutine(self.handler)

        middleware = getattr(self, self.type.lower())
        app.middlewares.append(middleware)


class MiddlewaresMixin:
    def __init__(self, *_) -> None:
        self.middlewares = []

    def middleware(self, handler: object) -> object:
        self.middlewares.append(Middleware(handler, TYPE_COMMON))
        return handler

    def error(self, handler: object) -> object:
        self.middlewares.append(Middleware(handler, TYPE_ERROR))
        return handler

    def register(self, app: "App", *_) -> None:
        for middleware in self.middlewares:
            middleware.register(app)


@dataclass(repr=False)
class Route:
    uri: str
    method: str
    handler: object
    kwargs: Dict[str, Any]

    def __repr__(self) -> str:
        return f"<Route uri='{self.uri}', method='{self.method}'>"

    def register(self, router: web.UrlDispatcher) -> None:
        router.add_route(self.method, self.uri, self.handler, **self.kwargs)


class RoutesMixin:
    def __init__(self, options: List[Union["Template", "Preroute"]]) -> None:
        for option in options:
            assert isinstance(option, (Template, Preroute)), \
                "Only templates and preroutes can be passed in the router options!"

        self._options = options
        self.routes = []

    def route(self, uri: str, *, methods: Optional[List[str]] = [hdrs.METH_GET, hdrs.METH_POST],
              **kwargs: Any) -> object:
        def inner(handler: object) -> object:
            self.routes += [
                Route(
                    uri,
                    method,
                    handler,
                    kwargs
                ) for method in methods
            ]
            return handler

        return inner

    def head(self, uri: str, **kwargs: Any) -> object:
        return self.route(uri, methods=[hdrs.METH_HEAD], **kwargs)

    def get(self, uri: str, **kwargs: Any) -> object:
        return self.route(uri, methods=[hdrs.METH_GET], **kwargs)

    def post(self, uri: str, **kwargs: Any) -> object:
        return self.route(uri, methods=[hdrs.METH_POST], **kwargs)

    def put(self, uri: str, **kwargs: Any) -> object:
        return self.route(uri, methods=[hdrs.METH_PUT], **kwargs)

    def patch(self, uri: str, **kwargs: Any) -> object:
        return self.route(uri, methods=[hdrs.METH_PATCH], **kwargs)

    def delete(self, uri: str, **kwargs: Any) -> object:
        return self.route(uri, methods=[hdrs.METH_DELETE], **kwargs)

    def lib(self, uri: str, handler: object, **kwargs: Any) -> None:
        self.routes.append(Route(uri, hdrs.METH_ANY, handler, kwargs))

    def _find_options(self, type: Union["Template", "Preroute"]) -> List[object]:
        return [option for option in self._options if isinstance(option, type)]

    @property
    def templates(self) -> List["Template"]:
        return self._find_options(Template)

    @property
    def preroutes(self) -> List["Preroute"]:
        return self._find_options(Preroute)

    def register(self, app: "App", location: str) -> None:
        router = app.router
        for template in self.templates:
            template.register(router, location)
        for preroute in self.preroutes:
            preroute.parse(self.routes)
        for route in self.routes:
            route.register(router)


class BaseRouter(MiddlewaresMixin, RoutesMixin):
    def __init__(self, options: Optional[List[Union["Template", "Preroute"]]] = []) -> None:
        for base in BaseRouter.__bases__:
            base.__init__(self, options)

    def register(self, app: "App", location: str) -> None:
        for base in BaseRouter.__bases__:
            base.register(self, app, location)


class Router(BaseRouter):
    def __repr__(self) -> str:
        return f"<Router routes={len(self.routes)}, middlewares={len(self.middlewares)}>"
