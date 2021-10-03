from attr import dataclass
from importlib import import_module
from typing import Optional

from .app import App
from .router import Router


@dataclass(repr=False)
class Module:
    module_path: str
    router_location: str

    def __repr__(self) -> str:
        return f"<ApplicationModule module_path='{self.module_path}'>"

    def register(self, app: App, path: str) -> None:
        assert not self.module_path.startswith("/") and self.module_path, \
            "The module cannot be registered because module_path starts with a slash or is empty!"
        assert self.router_location.count(":") == 1, \
            "The module cannot be registered because router_location is written incorrectly!"

        view_path = self.router_location.split(":")[0]
        view_location = f"{self.module_path}.{view_path}".replace("/", ".")
        view_instance = import_module(path + view_location)
        router_name = self.router_location.split(":")[1]
        router_instance = getattr(view_instance, router_name)

        assert isinstance(router_instance, Router), \
            "The module cannot be registered because the router was not found in the instance!"
        router_instance.register(app, path + self.module_path + "/")


def module(module_path: str, router_location: Optional[str] = "view:router") -> Module:
    return Module(module_path, router_location)
