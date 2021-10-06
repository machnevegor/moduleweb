from attr import dataclass
from aiohttp import hdrs, web
from typing import Optional, List, Union, Any

from .options import Template, Preroute

TYPE_COMMON = "COMMON"
TYPE_ERROR = "ERROR"


@dataclass(repr=False)
class Route:
    uri: str
    method: str
    handler: object
    kwargs: dict

    def __repr__(self) -> str:
        return f"<WebRoute uri='{self.uri}', method='{self.method}'>"

    def register(self, router: web.UrlDispatcher) -> None:
        router.add_route(self.method, self.uri, self.handler, **self.kwargs)


class RoutesMixin:
    def __init__(self, options: List[Union["TemplateOption", "PrerouteOption"]]) -> None:
        for option in options:
            assert isinstance(option, (Template, Preroute)), \
                "Only templates and preroutes can be passed in the router options!"

        self._options = options
        self.routes = []

    def route(self, uri: str, *, methods: Optional[List[str]] = [hdrs.METH_GET, hdrs.METH_POST], **kwargs) -> object:
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

    def head(self, uri: str, **kwargs) -> object:
        return self.route(uri, methods=[hdrs.METH_HEAD], **kwargs)

    def get(self, uri: str, **kwargs) -> object:
        return self.route(uri, methods=[hdrs.METH_GET], **kwargs)

    def post(self, uri: str, **kwargs) -> object:
        return self.route(uri, methods=[hdrs.METH_POST], **kwargs)

    def put(self, uri: str, **kwargs) -> object:
        return self.route(uri, methods=[hdrs.METH_PUT], **kwargs)

    def patch(self, uri: str, **kwargs) -> object:
        return self.route(uri, methods=[hdrs.METH_PATCH], **kwargs)

    def delete(self, uri: str, **kwargs) -> object:
        return self.route(uri, methods=[hdrs.METH_DELETE], **kwargs)

    def lib(self, uri: str, handler: object, **kwargs) -> None:
        self.routes.append(
            Route(
                uri,
                hdrs.METH_ANY,
                handler,
                kwargs
            )
        )

    def _find_options(self, type: Union["TemplateOption", "PrerouteOption"]) -> List[object]:
        return [option for option in self._options if isinstance(option, type)]

    @property
    def templates(self) -> List["TemplateOption"]:
        return self._find_options(Template)

    @property
    def preroutes(self) -> List["PrerouteOption"]:
        return self._find_options(Preroute)

    def register(self, app: "ModularApplication", location: str) -> None:
        router = app.router
        for template in self.templates:
            template.register(router, location)
        for preroute in self.preroutes:
            preroute.parse(self.routes)
        for route in self.routes:
            route.register(router)


@dataclass(repr=False)
class Middleware:
    handler: object
    type: str

    def __repr__(self) -> str:
        return f"<WebMiddleware type='{self.type}'>"

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

    def register(self, app: "ModularApplication") -> None:
        middleware = getattr(self, self.type.lower())
        app.middlewares.append(middleware)


class MiddlewaresMixin:
    def __init__(self, *_) -> None:
        self.middlewares = []

    def middleware(self, handler: object) -> object:
        self.middlewares.append(
            Middleware(
                handler,
                TYPE_COMMON
            )
        )
        return handler

    def error(self, handler: object) -> object:
        self.middlewares.append(
            Middleware(
                handler,
                TYPE_ERROR
            )
        )
        return handler

    def register(self, app: "ModularApplication", *_) -> None:
        for middleware in self.middlewares:
            middleware.register(app)


class BaseRouter(RoutesMixin, MiddlewaresMixin):
    def __init__(self, options: Optional[List[Union["TemplateOption", "PrerouteOption"]]] = []) -> None:
        for base in BaseRouter.__bases__:
            base.__init__(self, options)

    def register(self, app: "ModularApplication", location: str) -> None:
        for base in BaseRouter.__bases__:
            base.register(self, app, location)


class Router(BaseRouter):
    def __repr__(self) -> str:
        return f"<WebRouter routes={len(self.routes)}, middlewares={len(self.middlewares)}>"
