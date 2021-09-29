from attr import dataclass
from importlib import import_module

from .tools import validate_type


@dataclass(repr=False)
class Module:
    module_path: str
    router_location: str

    def __repr__(self):
        return f"<MW-ApplicationModule module_path='{self.module_path}'>"

    def register(self, app: object, path: str):
        assert not self.module_path.startswith("/") and self.module_path, \
            "The module cannot be registered because module_path starts with a slash or empty!"
        assert self.router_location.count(":") == 1, \
            "The module cannot be registered because it is written incorrectly in router_location!"

        view_path = self.router_location.split(":")[0]
        view_location = f"{self.module_path}.{view_path}".replace("/", ".")
        view_instance = import_module(path + view_location)
        router_name = self.router_location.split(":")[1]
        router_instance = getattr(view_instance, router_name)

        assert validate_type(router_instance, "MW-WebRouter"), \
            "The module cannot be registered because the router has not been found!"
        return router_instance.register(app, path + self.module_path + "/")


def module(module_path: str, router_location: str = "view:router"):
    return Module(module_path, router_location)
