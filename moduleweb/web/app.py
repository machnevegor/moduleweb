from aiohttp import web
from typing import Optional, List, Union

from .response import response_processor, render_setuper
from .module import Module
from .router import Router


class App(web.Application):
    def __init__(self, root: Optional[str] = "__main__", **kwargs) -> None:
        super().__init__(**kwargs)
        self._root = root.replace(".", "/") + "/" if root != "__main__" else ""
        self.middlewares.append(response_processor)
        self.on_startup.append(render_setuper)

    def __repr__(self) -> str:
        return f"<ModularApplication 0x{id(self):x}>"

    def add(self, modules: List[Union["ApplicationModule", "WebRouter"]]) -> None:
        for module in modules:
            assert isinstance(module, (Module, Router)), \
                "The add method registers only modules for the application!"
            module.register(self, self._root)

    def run(self, *, host: Optional[str] = "localhost", port: Optional[int] = 8000, **kwargs) -> None:
        web.run_app(self, host=host, port=port, **kwargs)
