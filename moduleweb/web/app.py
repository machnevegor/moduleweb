from aiohttp import web
from typing import Optional, Any, List, Union

from .response import response_processor, render_setuper
from .module import Module
from .router import Router

__all__ = ("App",)


class App(web.Application):
    def __init__(self, import_name: Optional[str] = "__main__", **kwargs: Any) -> None:
        """Method of the constructor of the modular application class.

        :param import_name:    The `import_name` parameter is very important for
                               a modular application, as it stores the location of
                               your application relative to the startup file. As you
                               know, all paths in a modular application are relative
                               (for example, to import an application module, you need
                               to specify the path relative to the application itself,
                               and to connect the template folder to your modular
                               application, you need to specify the path relative
                               to the application module), therefore, to avoid some
                               problems that may occur if you initialize your modular
                               application not in the startup file, you need to pass
                               `__name__` to `import_name`. Defaults to "__main__".
        :type import_name:     Optional[str]

        :param kwargs:         Since a modular application created with **moduleweb**
                               inherits a regular application created with **aiohttp**,
                               during initialization you can pass some parameter
                               via `kwargs` to the parent class.
        :type kwargs:          Any

        :return:               Nothing.
        :rtype:                None
        """

        super().__init__(**kwargs)
        self.import_name = import_name
        self.middlewares.append(response_processor)
        self.on_startup.append(render_setuper)

    def __repr__(self) -> str:
        """Method that outputs a description of the object.

        :return:    Just a description of the object.
        :rtype:     str
        """

        return f"<ModularApplication 0x{id(self):x}>"

    @property
    def location(self) -> str:
        """Class property that returns the location of the application.

        :return:    Path to directory where the file storing the modular
                    application is located, relative to the startup file.
        :rtype:     str
        """

        if self.import_name.count("."):
            path, _ = self.import_name.rsplit(".", 1)
            return path.replace(".", "/") + "/"
        return ""

    def add(self, modules: List[Union["Module", "Router"]]) -> None:
        """Method that registers application modules.

        :param modules:    A method that registers the application modules
                           into your modular application. Feature: if you want
                           to write the whole application in one file, you can
                           pass the router right away.
        :type modules:     List[Union[Module, Router]]

        :return:           Nothing.
        :rtype:            None
        """

        for module in modules:
            assert isinstance(module, (Module, Router)), \
                "The add method registers only modules for the application!"
            module.register(self, self.location)

    def run(self, **kwargs: Any) -> None:
        """Method that launches your modular application.

        :param kwargs:    Since a modular application created with **moduleweb**
                          inherits a regular application created with **aiohttp**,
                          at startup you can pass all the same parameters that you
                          would pass to `web.run_app` in **aiohttp**.
        :type kwargs:     Any

        :return:          Nothing.
        :rtype:           None
        """

        web.run_app(self, **kwargs)
