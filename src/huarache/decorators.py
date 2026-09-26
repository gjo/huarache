from dataclasses import dataclass, field
from inspect import getmodule, iscoroutine
from logging import getLogger
from typing import TYPE_CHECKING, Annotated, Any, get_args, get_origin

from .annotation_resolver import get_resolved_annotations

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from .interfaces import Container, Factory, P, Provide, Registry, T


logger = getLogger(__name__)


class _InjectMarker:
    pass


_UNDEFINED = object()


@dataclass(frozen=True, slots=True)
class FromSettings(_InjectMarker):
    key: str
    as_type: type[Any] = field(default=str, kw_only=True)
    default: Any = field(default=_UNDEFINED, kw_only=True)


@dataclass(frozen=True, slots=True)
class Spec[T](_InjectMarker):
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
        assert provide is not None  # noqa: S101
        assert isinstance(name, str)  # noqa: S101

        def wrapper(wrapped: Callable[P, T]) -> Callable[P, T]:
            module = getmodule(wrapped)
            if module:
                self._registered.setdefault(module.__name__, []).append(
                    _Info(callable_=wrapped, provide=provide, name=name)
                )
            return wrapped

        return wrapper

    def activate(self, registry: Registry, module_name: str) -> None:
        if module_name in self._registered:
            for info in self._registered[module_name]:
                registry.register_factory(_make_factory(registry, info), info.provide, name=info.name)


def _make_factory[T](registry: Registry, info: _Info[T]) -> Factory[T]:
    kwargs: dict[str, Any] = {}
    for k, v in get_resolved_annotations(info.callable_).items():
        if k in ("cls", "return", "self"):
            continue
        if k in kwargs:
            continue
        if get_origin(v) is Annotated:
            type_args = get_args(v)
            for targ in type_args:
                if isinstance(targ, Spec):
                    kwargs[k] = v
                    break
                if isinstance(targ, FromSettings):
                    kwargs[k] = _from_settings(registry, v)
                    break
            else:
                kwargs[k] = Spec(type_args[0])  # TODO(gjo): 読み飛ばしどうする?
        else:
            kwargs[k] = Spec(v)  # TODO(gjo): 読み飛ばしどうする?

    return (
        _AsyncFactory(info.callable_, kwargs) if iscoroutine(info.callable_) else _SyncFactory(info.callable_, kwargs)
    )


# TODO(gjo): 取ってつけた感が強いので後で作り直す
def _from_settings(registry: Registry, inject: FromSettings) -> Any:
    if inject.default is _UNDEFINED:
        raw = registry.settings[inject.key]
    else:
        raw = registry.settings.get(inject.key, inject.default)
    if isinstance(raw, inject.as_type):
        return raw
    if inject.as_type is bool:
        if isinstance(raw, str):
            return raw.lower() in {"true", "yes", "1"}
        return bool(raw)
    if inject.as_type is list and isinstance(raw, str):
        return raw.splitlines()
    return inject.as_type(raw)


class _SyncFactory[T]:
    def __init__(self, callable_: Callable[..., T], injects: dict[str, Any]) -> None:
        self.callable_ = callable_
        self.injects = injects

    def __call__(self, container: Container) -> T:
        kwargs: dict[str, Any] = {}
        for k, v in self.injects.items():
            if isinstance(v, Spec):
                kwargs[k] = container.find(v.provide, name=v.name)
            else:
                kwargs[k] = v
        return self.callable_(**kwargs)


class _AsyncFactory[T]:
    def __init__(self, callable_: Callable[..., Awaitable[T]], injects: dict[str, Any]) -> None:
        self.callable_ = callable_
        self.injects = injects

    async def __call__(self, container: Container) -> T:
        kwargs: dict[str, Any] = {}
        for k, v in self.injects.items():
            if isinstance(v, Spec):
                # TODO(gjo): gather
                kwargs[k] = await container.async_find(v.provide, name=v.name)
            else:
                kwargs[k] = v
        return await self.callable_(**kwargs)


global_instance = FactoryDecorator()
service = global_instance.service
