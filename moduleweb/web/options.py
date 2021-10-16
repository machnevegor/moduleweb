from attr import dataclass
from aiohttp import web
from typing import Dict, Any, Optional, List

__all__ = ("template", "preroute")


@dataclass(repr=False)
class Template:
    name: str
    folder: str
    kwargs: Dict[str, Any]

    def __repr__(self) -> str:
        """Method that outputs a description of the object.

        :return:    Just a description of the object.
        :rtype:     str
        """

        return f"<Template name='{self.name}'>"

    def register(self, router: web.UrlDispatcher, location: str) -> None:
        """A service method that registers a folder with a template in the router.

        :param router:      An instance of the main router modular application that
                            is `web.UrlDispatcher' from the parent application **aiohttp**.
                            The folder with the template is added as a static resource that
                            can be accessed by a route equal to the name of this template.
        :type router:       web.UrlDispatcher

        :param location:    The path where the application module is located relative to the
                            startup file. This parameter is important because the path to the
                            template folder is relative to the application module, and the
                            full path from the startup file is required for registration.
        :type location:     str

        :return:            Nothing.
        :rtype:             None
        """

        assert not self.name.startswith("/") and self.name, \
            "The template cannot be registered because name starts with a slash or is empty!"
        router.add_static("/" + self.name, location + self.folder, **self.kwargs)


def template(name: str, folder: Optional[str] = "template", **kwargs: Any) -> "Template":
    """A function that returns a template option object.

    :param name:      This parameter assigns a name to the template. By accessing
                      the template folder with this name, you can access its files
                      via routes or by calling the rendering.
    :type name:       str

    :param folder:    The path to the template folder relative to the
                      application module. Defaults to "template".
    :type folder:     Optional[str]

    :param kwargs:    Since this option is registered by the modular application as
                      a static resource, and the static resource is an object from
                      **aiohttp**, you can pass through `kwargs` those parameters that
                      would be passed when declaring a static route in **aiohttp**.
    :type kwargs:     Any

    :return:          Template option object.
    :rtype:           Template
    """

    return Template(name, folder, kwargs)


@dataclass(repr=False)
class Preroute:
    uri: str
    prefix: str
    kwargs: Dict[str, Any]

    def __repr__(self) -> str:
        """Method that outputs a description of the object.

        :return:    Just a description of the object.
        :rtype:     str
        """

        return f"<Preroute prefix='{self.prefix}'>"

    def parse(self, routes: List["Route"]) -> None:
        """Service method that processes the passed routes.

        :param routes:    The list of routes stored in the router of the application module
                          that will be processed for the presence of this preroute. Those
                          `kwargs` you previously passed to the preroute during initialization
                          will be applied to the route if `prefix` of that preroute is
                          encountered, and the `prefix` itself will be replaced by the
                          `uri` of the preroute.
        :type routes:     List[Route]

        :return:          Nothing.
        :rtype:           None
        """

        for route in routes:
            if route.uri.startswith(self.prefix):
                route.uri = self.uri + route.uri[len(self.prefix):]
                route.kwargs = {**self.kwargs, **route.kwargs}


def preroute(uri: str, prefix: Optional[str] = "~", **kwargs: Any) -> "Preroute":
    """A function that returns a preroute option object.

    :param uri:       The path to be inserted in place of the `prefix` if
                      the start of the route path matches this `prefix`.
    :type uri:        str

    :param prefix:    The short designation to be replaced by `uri` of this
                      provisional route. It is important to understand that the
                      `prefix` and the preroute option itself only applies to the
                      router, not the entire modular application. Defaults to "~".
    :type prefix:     Optional[str]

    :param kwargs:    You can pass some `kwargs` which will be applied by
                      default to all routes having the same preroute `prefix`.
    :type kwargs:     Any

    :return:          Preroute option object.
    :rtype:           Preroute
    """

    return Preroute(uri, prefix, kwargs)
