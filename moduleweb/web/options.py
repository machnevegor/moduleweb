from attr import dataclass


@dataclass(repr=False)
class Template:
    name: str
    folder: str
    kwargs: dict

    def __repr__(self):
        return f"<TemplateOption name='{self.name}'>"

    def register(self, router: object, path: str):
        assert not self.name.startswith("/") and self.name, \
            "The template cannot be registered because name starts with a slash or is empty!"
        router.add_static("/" + self.name, path + self.folder, **self.kwargs)


def template(name: str, folder: str = "template", **kwargs):
    return Template(name, folder, kwargs)


@dataclass(repr=False)
class Preroute:
    uri: str
    prefix: str
    kwargs: dict

    def __repr__(self):
        return f"<PrerouteOption prefix='{self.prefix}'>"

    def parse(self, routes: list):
        for route in routes:
            if route.uri.startswith(self.prefix):
                route.uri = self.uri + route.uri[len(self.prefix):]
                route.kwargs = {**self.kwargs, **route.kwargs}


def preroute(uri: str, prefix: str = "~", **kwargs):
    return Preroute(uri, prefix, kwargs)
