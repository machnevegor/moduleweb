from aiohttp import web
from jinja2 import FileSystemLoader, PrefixLoader
from aiohttp_jinja2 import setup

from .responses import response_processor
from .tools import validate_type


class App(web.Application):
    def __init__(self, root: str = "__main__", **kwargs):
        super().__init__(**kwargs)
        self.root = root.replace(".", "/") + "/" if root != "__main__" else ""
        self.middlewares.append(response_processor)

    def __repr__(self):
        return f"<MW-ModularApplication 0x{id(self):x}>"

    def add(self, modules: list):
        for module in modules:
            assert validate_type(module, ["MW-ApplicationModule", "MW-WebRouter"]), \
                "The add method registers only modules with a router for the application!"
            module.register(self, self.root)

    def setup_render(self):
        prefixes_dict = {}
        for resource in self.router._resources:
            if validate_type(resource, "StaticResource"):
                directory = FileSystemLoader(resource._directory)
                prefixes_dict[resource._prefix[1:]] = directory
        setup(self, loader=PrefixLoader(prefixes_dict))

    def run(self, *, host: str = "localhost", port: int = 8000, **kwargs):
        self.setup_render()
        web.run_app(self, host=host, port=port, **kwargs)
