from typing import TYPE_CHECKING, Any, Protocol, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Mapping, Sequence

T = TypeVar("T")


class ConfigActivator(Protocol):
    def __call__(self, config: Configurator) -> None: ...


class Configurator(Protocol):
    registry: Registry

    def commit(self) -> None: ...
    def include(self, module_name: str) -> None: ...


class Container(Protocol):
    registry: Registry

    def find(self, provide: type[T] | None, *, name: str = ...) -> T: ...
    async def async_find(self, provide: type[T] | None, *, name: str = ...) -> T: ...


class ContainerFactory(Protocol):
    def __call__(self, registry: Registry) -> Container: ...


class Factory[T](Protocol):
    def __call__(self, container: Container) -> T | Awaitable[T]: ...


class Registry(Protocol):
    settings: Mapping[str, Any]

    def create_container(self) -> Container: ...
    def find_names(self, provide: type) -> Sequence[str]: ...
    def register_factory(self, factory: Factory[T], provide: type[T] | None, *, name: str = ...) -> None: ...
    def find_factory(self, provide: type[T] | None, *, name: str = ...) -> Factory[T]: ...


class RegistryFactory(Protocol):
    def __call__(
        self, *, container_factory: ContainerFactory | None = ..., settings: Mapping[str, Any] | None = ...
    ) -> Registry: ...
