from aiohttp import web
from jinja2 import FileSystemLoader, PrefixLoader
from aiohttp_jinja2 import setup

from .responses import response_processor
from .module import Module
from .router import Router


class App(web.Application):
    def __init__(self, root: str = "__main__", **kwargs):
        super().__init__(**kwargs)
        self.root = root.replace(".", "/") + "/" if root != "__main__" else ""
        self.middlewares.append(response_processor)

    def __repr__(self):
        return f"<ModularApplication 0x{id(self):x}>"

    def add(self, modules: list):
        for module in modules:
            assert isinstance(module, (Module, Router)), \
                "The add method registers only modules with the router in the application!"
            module.register(self, self.root)

    def setup_render(self):
        directory_prefixes = {}
        for resource in self.router.resources:
            if isinstance(resource, web.StaticResource):
                directory = FileSystemLoader(resource.directory)
                directory_prefixes[resource.prefix[1:]] = directory
        setup(self, loader=PrefixLoader(directory_prefixes))

    def run(self, *, host: str = "localhost", port: int = 8000, **kwargs):
        self.setup_render()
        web.run_app(self, host=host, port=port, **kwargs)
