from typing import NamedTuple
from importlib import import_module


class Module(NamedTuple):
    module_path: str
    router_location: str

    def __repr__(self):
        return f"<MW-ApplicationModule module_path='{self.module_path}'>"

    def register(self, app: object, path: str):
        router_location = self.router_location.replace("/", ".")
        view_path = ".".join(router_location.split(".")[:-1])
        view_location = f"{self.module_path}.{view_path}".replace("/", ".")
        view_instance = import_module(path + view_location)
        router_name = router_location.split(".")[-1]
        router_instance = getattr(view_instance, router_name)
        return router_instance.register(app, path + self.module_path + "/")


def module(module_path: str, router_location: str = "view.router"):
    return Module(module_path, router_location)
