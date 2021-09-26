from aiohttp import web
from jinja2 import FileSystemLoader, PrefixLoader
from aiohttp_jinja2 import setup


class App(web.Application):
    def __init__(self, root: str = "__main__", **kwargs):
        super().__init__(**kwargs)
        self.root = root.replace(".", "/") + "/" if root != "__main__" else ""
        self.middlewares.append(self._response_processor)

    def __repr__(self):
        return f"<ModularApplication 0x{id(self):x}>"

    @web.middleware
    async def _response_processor(self, request: object, handler: object):
        response = await handler(request)
        if isinstance(response, object):
            for response_type in ["TextResponse", "RenderResponse", "FileResponse", "RedirectResponse"]:
                if response_type in str(response):
                    return response.parse(request)
        return response

    def add(self, modules: list):
        for module in modules:
            module.register(self, self.root)

    def setup_render(self):
        prefixes_dict = {}
        for resource in self.router._resources:
            if isinstance(resource, object) and "StaticResource" in str(resource):
                prefixes_dict[resource._prefix[1:]] = FileSystemLoader(resource._directory)
        setup(self, loader=PrefixLoader(prefixes_dict))

    def run(self, *, host: str = "localhost", port: int = 8000, **kwargs):
        self.setup_render()
        web.run_app(
            self,
            host=host,
            port=port,
            **kwargs
        )
