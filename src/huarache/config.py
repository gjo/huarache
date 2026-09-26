from importlib import import_module
from typing import TYPE_CHECKING, Any

from .exceptions import AlreadyCommitedError
from .service_locator import Registry as _RegistryImpl

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .interfaces import ConfigActivator, ContainerFactory, RegistryFactory


class Configurator:
    def __init__(
        self,
        *,
        container_factory: ContainerFactory | None = None,
        registry_factory: RegistryFactory | None = None,
        settings: Mapping[str, Any] | None = None,
    ) -> None:
        self.registry = (registry_factory or _RegistryImpl)(container_factory=container_factory, settings=settings)
        self._commited = False
        self._included: list[str] = []

    def commit(self) -> None:
        self._commited = True

    def include(self, module_name: str) -> None:
        if self._commited:
            raise AlreadyCommitedError
        if module_name not in self._included:
            module = import_module(module_name)
            if hasattr(module, "includeme"):
                activator: ConfigActivator = module.includeme
                activator(self)
            self._included.append(module_name)
