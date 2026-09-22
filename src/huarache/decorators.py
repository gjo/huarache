from dataclasses import dataclass, field
from inspect import getmodule
from logging import getLogger
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from .interfaces import Container, Factory, P, Provide, Registry, T


logger = getLogger(__name__)


@dataclass(frozen=True, slots=True)
class FromSettings:
    key: str


@dataclass(frozen=True, slots=True)
class Spec[T]:
    provide: Provide[T]
    name: str = field(default="", kw_only=True)


@dataclass
class _Info[T]:
    callable_: Callable[..., T]
    provide: Provide[T]
    name: str


class FactoryDecorator:
    def __init__(self) -> None:
        self._registered: dict[str, list[_Info[Any]]] = {}

    def service(self, provide: Provide[T], *, name: str = "") -> Callable[[Callable[P, T]], Callable[P, T]]:
        def wrapper(wrapped: Callable[P, T]) -> Callable[P, T]:
            module = getmodule(provide)
            if module:
                self._registered.setdefault(module.__name__, []).append(
                    _Info(callable_=wrapped, provide=provide, name=name)
                )
            return wrapped

        return wrapper

    def activate(self, registry: Registry, module_name: str) -> None:
        if module_name in self._registered:
            for info in self._registered[module_name]:
                registry.register_factory(self._make_factory(info), info.provide, name=info.name)

    def _make_factory(self, info: _Info[T]) -> Factory[T]:
        def factory(container: Container) -> T:
            kwargs: dict[str, Any] = {}
            return info.callable_(**kwargs)

        return factory


global_instance = FactoryDecorator()
service = global_instance.service
