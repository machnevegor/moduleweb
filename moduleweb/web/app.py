from aiohttp import web

from .responses import response_processor, setup_render
from .module import Module
from .router import Router


class App(web.Application):
    def __init__(self, root: str = "__main__", **kwargs):
        super().__init__(**kwargs)
        self.root = root.replace(".", "/") + "/" if root != "__main__" else ""
        self.middlewares.append(response_processor)
        self.on_startup.append(setup_render)

    def __repr__(self):
        return f"<ModularApplication 0x{id(self):x}>"

    def add(self, modules: list):
        for module in modules:
            assert isinstance(module, (Module, Router)), \
                "The add method registers only modules for the application!"
            module.register(self, self.root)

    def run(self, *, host: str = "localhost", port: int = 8000, **kwargs):
        web.run_app(self, host=host, port=port, **kwargs)
