from aiohttp import web

METH_VIEW = "*"
METH_HEAD = "HEAD"
METH_GET = "GET"
METH_POST = "POST"
METH_PUT = "PUT"
METH_PATCH = "PATCH"
METH_DELETE = "DELETE"

TYPE_COMMON = "COMMON"
TYPE_ERROR = "ERROR"


class Route:
    def __init__(self, path: str, method: str, handler: object, kwargs: dict):
        self.path = path
        self.method = method
        self.handler = handler
        self.kwargs = kwargs

    def __repr__(self):
        return f"<MW WebRoute path='{self.path}', method='{self.method}'>"

    def register(self, router: object):
        router.add_route(self.method, self.path, self.handler, **self.kwargs)


class RoutesMixin:
    def __init__(self, options: list, *args, **kwargs):
        self.options = options
        self.routes = []

    def route(self, path: str, *, methods: list = [METH_GET, METH_POST], **kwargs):
        def inner(handler: object):
            self.routes += [
                Route(
                    path,
                    method,
                    handler,
                    kwargs
                ) for method in methods
            ]
            return handler

        return inner

    def head(self, path: str, **kwargs):
        return self.route(path, methods=[METH_HEAD], **kwargs)

    def get(self, path: str, **kwargs):
        return self.route(path, methods=[METH_GET], **kwargs)

    def post(self, path: str, **kwargs):
        return self.route(path, methods=[METH_POST], **kwargs)

    def put(self, path: str, **kwargs):
        return self.route(path, methods=[METH_PUT], **kwargs)

    def patch(self, path: str, **kwargs):
        return self.route(path, methods=[METH_PATCH], **kwargs)

    def delete(self, path: str, **kwargs):
        return self.route(path, methods=[METH_DELETE], **kwargs)

    def lib(self, path: str, handler: object, **kwargs):
        self.routes.append(
            Route(
                path,
                METH_VIEW,
                handler,
                kwargs
            )
        )

    def _find_options(self, type: str):
        suitable_options = []
        for option in self.options:
            if isinstance(option, object) and f"MW {type}" in str(option):
                suitable_options.append(option)
        return suitable_options

    @property
    def templates(self):
        return self._find_options("TemplateOption")

    @property
    def preroutes(self):
        return self._find_options("PrerouteOption")

    def register(self, app: object, path: str, *args, **kwargs):
        router = app.router
        for template in self.templates:
            template.register(router, path)
        for preroute in self.preroutes:
            preroute.parse(self.routes)
        for route in self.routes:
            route.register(router)


class Middleware:
    def __init__(self, handler: object, type: str):
        self.handler = handler
        self.type = type

    def __repr__(self):
        return f"<MW WebMiddleware type='{self.type}'>"

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
        return f"<MW WebRouter routes={len(self.routes)}, middlewares={len(self.middlewares)}>"

    def register(self, app: object, path: str):
        super().register(app, path)
