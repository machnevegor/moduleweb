from attr import dataclass
from importlib import import_module
from typing import Optional

from .router import Router

__all__ = ("module",)


@dataclass(repr=False)
class Module:
    module_path: str
    router_path: str

    def __repr__(self) -> str:
        """Method that outputs a description of the object.

        :return:    Just a description of the object.
        :rtype:     str
        """

        return f"<ApplicationModule module_path='{self.module_path}'>"

    def register(self, app: "App", location: str) -> None:
        """Service method registering the module to the application.

        :param app:         An instance of the modular application to which the
                            router of this module application with its routes
                            and middlewares will register.
        :type app:          App

        :param location:    The path to the modular application instance relative
                            to the startup file. This parameter is necessary because
                            it affects the correctness of importing the router and
                            registering folders with templates to the router.
        :type location:     str

        :return:            Nothing.
        :rtype:             None
        """

        assert not self.module_path.startswith("/") and self.module_path, \
            "The module cannot be registered because module_path starts with a slash or is empty!"
        assert self.router_path.count(":") == 1, \
            "The module cannot be registered because router_path is written incorrectly!"

        view_path, router_name = self.router_path.split(":")
        view_location = location + f"{self.module_path}.{view_path}"
        view = import_module(view_location.replace("/", "."))
        router = getattr(view, router_name, None)

        assert isinstance(router, Router), \
            "The module cannot be registered because the router was not found in the view!"
        router.register(app, location + self.module_path + "/")


def module(module_path: str, router_path: Optional[str] = "view:router") -> "Module":
    """A function that returns an application module object.

    :param module_path:    The path to the imported application module
                           relative to the modular application.
    :type module_path:     str

    :param router_path:    The path to the router file relative to the application
                           module and the name of the variable that stores the router
                           instance, separated by a colon. Defaults to "view:router".
    :type router_path:     Optional[str]

    :return:               Application module object.
    :rtype:                Module
    """

    return Module(module_path, router_path)
