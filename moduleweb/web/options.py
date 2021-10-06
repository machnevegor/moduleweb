from attr import dataclass
from aiohttp import web
from typing import Optional, List


@dataclass(repr=False)
class Template:
    name: str
    folder: str
    kwargs: dict

    def __repr__(self) -> str:
        return f"<TemplateOption name='{self.name}'>"

    def register(self, router: web.UrlDispatcher, location: str) -> None:
        assert not self.name.startswith("/") and self.name, \
            "The template cannot be registered because name starts with a slash or is empty!"
        router.add_static("/" + self.name, location + self.folder, **self.kwargs)


def template(name: str, folder: Optional[str] = "template", **kwargs) -> "TemplateOption":
    return Template(name, folder, kwargs)


@dataclass(repr=False)
class Preroute:
    uri: str
    prefix: str
    kwargs: dict

    def __repr__(self) -> str:
        return f"<PrerouteOption prefix='{self.prefix}'>"

    def parse(self, routes: List["WebRoute"]) -> None:
        for route in routes:
            if route.uri.startswith(self.prefix):
                route.uri = self.uri + route.uri[len(self.prefix):]
                route.kwargs = {**self.kwargs, **route.kwargs}


def preroute(uri: str, prefix: Optional[str] = "~", **kwargs) -> "PrerouteOption":
    return Preroute(uri, prefix, kwargs)
