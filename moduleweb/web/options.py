from typing import NamedTuple


class Template(NamedTuple):
    name: str
    folder: str
    kwargs: dict

    def __repr__(self):
        return f"<MW-TemplateOption path='/{self.name}'>"

    def register(self, router: object, path: str):
        assert not self.name in ["", "/"], \
            "An empty name cannot be passed to the template option!"
        router.add_static("/" + self.name, path + self.folder, **self.kwargs)


def template(name: str, folder: str = "template", **kwargs):
    return Template(name, folder, kwargs)


class Preroute(NamedTuple):
    uri: str
    prefix: str
    kwargs: dict

    def __repr__(self):
        return f"<MW-PrerouteOption prefix='{self.prefix}'>"

    def parse(self, routes: list):
        for route in routes:
            if route.uri.startswith(self.prefix):
                route.uri = self.uri + route.uri[len(self.prefix):]
                route.kwargs = {**self.kwargs, **route.kwargs}


def preroute(uri: str, prefix: str = "~", **kwargs):
    return Preroute(uri, prefix, kwargs)
