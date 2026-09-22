import asyncio
from inspect import isawaitable
from logging import getLogger
from typing import TYPE_CHECKING, Any

from .exceptions import AlreadyRegisteredError

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .interfaces import Container as ContainerProto
    from .interfaces import ContainerFactory, Factory, Provide, T
    from .interfaces import Registry as RegistryProto


logger = getLogger(__name__)


class Registry:
    def __init__(
        self, *, container_factory: ContainerFactory | None = None, settings: Mapping[str, Any] | None = None
    ) -> None:
        self.settings = settings or {}
        self._container_factory = container_factory or Container
        self._factories: dict[type, dict[str, Factory[Any]]] = {}

    def create_container(self) -> ContainerProto:
        return self._container_factory(self)

    def register_factory(self, factory: Factory[T], provide: Provide[T], *, name: str = "") -> None:
        assert provide is not None  # noqa: S101
        assert isinstance(name, str)  # noqa: S101
        names = self._factories.setdefault(provide, {})
        if name in names:
            raise AlreadyRegisteredError(provide, name)
        names[name] = factory

    def find_names(self, provide: type) -> Sequence[str]:
        return sorted(self._factories[provide].keys())

    def find_factory(self, provide: Provide[T], *, name: str = "") -> Factory[T]:
        assert provide is not None  # noqa: S101
        assert isinstance(name, str)  # noqa: S101
        return self._factories[provide][name]


class Container:
    def __init__(self, registry: RegistryProto) -> None:
        self.registry = registry
        self._cache: dict[tuple[type, str], Any] = {}
        self._cache_lock = asyncio.Lock()

    def find(self, provide: Provide[T], *, name: str = "") -> T:
        assert provide is not None  # noqa: S101
        assert isinstance(name, str)  # noqa: S101
        spec = provide, name
        instance = self._cache.get(spec, None)
        if instance is None:
            factory = self.registry.find_factory(provide, name=name)
            maybe_instance = factory(self)
            if isawaitable(maybe_instance):
                logger.info("Resolving awaitable: %r:%s", provide, name)
                instance = asyncio.run(maybe_instance)
            else:
                instance = maybe_instance
            self._cache[spec] = instance
        return instance

    async def async_find(self, provide: Provide[T], *, name: str = "") -> T:
        assert provide is not None  # noqa: S101
        assert isinstance(name, str)  # noqa: S101
        spec = provide, name
        async with self._cache_lock:
            instance = self._cache.get(spec, None)
        if instance is None:
            factory = self.registry.find_factory(provide, name=name)
            maybe_instance = factory(self)
            if isawaitable(maybe_instance):
                instance = await maybe_instance
            else:
                instance = maybe_instance
            async with self._cache_lock:
                self._cache[spec] = instance
        return instance
