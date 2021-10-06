from attr import dataclass
from importlib import import_module
from typing import Optional

from .router import Router


@dataclass(repr=False)
class Module:
    module_path: str
    router_path: str

    def __repr__(self) -> str:
        return f"<ApplicationModule module_path='{self.module_path}'>"

    def register(self, app: "ModularApplication", location: str) -> None:
        assert not self.module_path.startswith("/") and self.module_path, \
            "The module cannot be registered because module_path starts with a slash or is empty!"
        assert self.router_path.count(":") == 1, \
            "The module cannot be registered because router_path is written incorrectly!"

        view_path = self.router_path.split(":")[0]
        view_location = location + f"{self.module_path}.{view_path}"
        view = import_module(view_location.replace("/", "."))
        router_name = self.router_path.split(":")[1]
        router = getattr(view, router_name)

        assert isinstance(router, Router), \
            "The module cannot be registered because the router was not found in the view!"
        router.register(app, location + self.module_path + "/")


def module(module_path: str, router_path: Optional[str] = "view:router") -> "ApplicationModule":
    return Module(module_path, router_path)
