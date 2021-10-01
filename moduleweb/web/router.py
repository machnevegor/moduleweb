from attr import dataclass
from aiohttp import hdrs, web

from .options import Template, Preroute

TYPE_COMMON = "COMMON"
TYPE_ERROR = "ERROR"


@dataclass(repr=False)
class Route:
    uri: str
    method: str
    handler: object
    kwargs: dict

    def __repr__(self):
        return f"<WebRoute uri='{self.uri}', method='{self.method}'>"

    def register(self, router: object):
        router.add_route(self.method, self.uri, self.handler, **self.kwargs)


class RoutesMixin:
    def __init__(self, options: list, *args, **kwargs):
        for option in options:
            assert isinstance(option, (Template, Preroute)), \
                "Only templates and preroutes can be passed in the router option!"

        self.options = options
        self.routes = []

    def route(self, uri: str, *, methods: list = [hdrs.METH_GET, hdrs.METH_POST], **kwargs):
        def inner(handler: object):
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

    def head(self, uri: str, **kwargs):
        return self.route(uri, methods=[hdrs.METH_HEAD], **kwargs)

    def get(self, uri: str, **kwargs):
        return self.route(uri, methods=[hdrs.METH_GET], **kwargs)

    def post(self, uri: str, **kwargs):
        return self.route(uri, methods=[hdrs.METH_POST], **kwargs)

    def put(self, uri: str, **kwargs):
        return self.route(uri, methods=[hdrs.METH_PUT], **kwargs)

    def patch(self, uri: str, **kwargs):
        return self.route(uri, methods=[hdrs.METH_PATCH], **kwargs)

    def delete(self, uri: str, **kwargs):
        return self.route(uri, methods=[hdrs.METH_DELETE], **kwargs)

    def lib(self, uri: str, handler: object, **kwargs):
        self.routes.append(
            Route(
                uri,
                hdrs.METH_ANY,
                handler,
                kwargs
            )
        )

    def _find_options(self, type: str):
        return [option for option in self.options if isinstance(option, type)]

    @property
    def templates(self):
        return self._find_options(Template)

    @property
    def preroutes(self):
        return self._find_options(Preroute)

    def register(self, app: object, path: str, *args, **kwargs):
        router = app.router
        for template in self.templates:
            template.register(router, path)
        for preroute in self.preroutes:
            preroute.parse(self.routes)
        for route in self.routes:
            route.register(router)


@dataclass(repr=False)
class Middleware:
    handler: object
    type: str

    def __repr__(self):
        return f"<WebMiddleware type='{self.type}'>"

    @web.middleware
    async def common(self, request: object, handler: object):
        return await self.handler(request, handler)

    @web.middleware
    async def error(self, request: object, handler: object):
        try:
            return await handler(request)
        except web.HTTPException as exc:
            if exc.status != 404:
                raise
            return await self.handler(request)

    def register(self, app: object):
        middleware = getattr(self, self.type.lower())
        app.middlewares.append(middleware)


class MiddlewaresMixin:
    def __init__(self, *args, **kwargs):
        self.middlewares = []

    def middleware(self, handler: object):
        self.middlewares.append(
            Middleware(
                handler,
                TYPE_COMMON
            )
        )
        return handler

    def error(self, handler: object):
        self.middlewares.append(
            Middleware(
                handler,
                TYPE_ERROR
            )
        )
        return handler

    def register(self, app: object, *args, **kwargs):
        for middleware in self.middlewares:
            middleware.register(app)


class BaseRouter(RoutesMixin, MiddlewaresMixin):
    def __init__(self, options: list):
        for base in BaseRouter.__bases__:
            base.__init__(self, options)

    def register(self, app: object, path: str):
        for base in BaseRouter.__bases__:
            base.register(self, app, path)


class Router(BaseRouter):
    def __init__(self, options: list = []):
        super().__init__(options)

    def __repr__(self):
        return f"<WebRouter routes={len(self.routes)}, middlewares={len(self.middlewares)}>"

    def register(self, app: object, path: str):
        super().register(app, path)
