from attr import dataclass


@dataclass(repr=False)
class Template:
    name: str
    folder: str
    kwargs: dict

    def __repr__(self):
        return f"<MW-TemplateOption name='{self.name}'>"

    def register(self, router: object, path: str):
        assert not self.name.startswith("/") and self.name, \
            "The template name cannot be registered because it starts with a slash or empty!"
        router.add_static("/" + self.name, path + self.folder, **self.kwargs)


def template(name: str, folder: str = "template", **kwargs):
    return Template(name, folder, kwargs)


@dataclass(repr=False)
class Preroute:
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
