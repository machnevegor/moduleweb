from typing import NamedTuple


class Template(NamedTuple):
    name: str
    folder: str
    kwargs: dict

    def __repr__(self):
        return f"<MW TemplateOption path='/{self.name}'>"

    def register(self, router: object, path: str):
        assert not self.name in ["", "/"], \
            "An empty name cannot be passed to the template option!"
        router.add_static("/" + self.name, path + self.folder, **self.kwargs)


def template(name: str, folder: str = "template", **kwargs):
    return Template(name, folder, kwargs)


class Preroute(NamedTuple):
    path: str
    prefix: str
    kwargs: dict

    def __repr__(self):
        return f"<MW PrerouteOption prefix='{self.prefix}'>"

    def parse(self, routes: list):
        for route in routes:
            if route.path.startswith(self.prefix):
                route.path = self.path + route.path[len(self.prefix):]
                route.kwargs = {**self.kwargs, **route.kwargs}


def preroute(path: str, prefix: str = "~", **kwargs):
    return Preroute(path, prefix, kwargs)
