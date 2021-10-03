from aiohttp import web
from typing import Optional, List, Union

from .response import response_processor, setup_render
from .module import Module
from .router import Router


class App(web.Application):
    def __init__(self, root: Optional[str] = "__main__", **kwargs) -> None:
        super().__init__(**kwargs)
        self.root = root.replace(".", "/") + "/" if root != "__main__" else ""
        self.middlewares.append(response_processor)
        self.on_startup.append(setup_render)

    def __repr__(self) -> str:
        return f"<ModularApplication 0x{id(self):x}>"

    def add(self, modules: List[Union[Module, Router]]) -> None:
        for module in modules:
            assert isinstance(module, (Module, Router)), \
                "The add method registers only modules for the application!"
            module.register(self, self.root)

    def run(self, *, host: Optional[str] = "localhost", port: Optional[int] = 8000, **kwargs) -> None:
        web.run_app(self, host=host, port=port, **kwargs)
