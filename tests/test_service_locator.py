from typing import TYPE_CHECKING, Protocol

import pytest

if TYPE_CHECKING:
    from huarache.interfaces import Container


class Foo(Protocol):
    some: str


class FooImpl(Foo):
    some = "some"

    @classmethod
    def factory(cls, container: Container) -> Foo:
        return cls()


def foo_factory(container: Container) -> Foo:
    return FooImpl()


async def async_foo_factory(container: Container) -> Foo:
    return FooImpl()


class FooImpl2:
    def __init__(self, container: Container) -> None:
        self.some = "some"


def test_explicit_container_factory() -> None:
    from huarache.service_locator import Container, Registry

    if TYPE_CHECKING:
        from huarache.interfaces import Container as ContainerProto
        from huarache.interfaces import Registry as RegistryProto

    ct: Container | None = None

    def container_factory(registry: RegistryProto) -> ContainerProto:
        nonlocal ct
        ct = Container(registry=registry)
        return ct

    registry = Registry(container_factory=container_factory)
    assert registry.create_container() is ct


def test_factory() -> None:
    from huarache.service_locator import Registry

    registry = Registry()
    registry.register_factory(foo_factory, Foo)
    fac = registry.find_factory(Foo)
    assert fac is foo_factory
    names = registry.find_names(Foo)
    assert names == [""]

    container = registry.create_container()
    ins = container.find(Foo)
    assert isinstance(ins, FooImpl)

    ins2 = container.find(Foo)
    assert isinstance(ins2, FooImpl)
    assert ins is ins2


def test_factory_named() -> None:
    from huarache.service_locator import Registry

    registry = Registry()
    registry.register_factory(foo_factory, Foo, name="name")
    fac = registry.find_factory(Foo, name="name")
    assert fac is foo_factory
    names = registry.find_names(Foo)
    assert names == ["name"]

    container = registry.create_container()
    ins = container.find(Foo, name="name")
    assert isinstance(ins, FooImpl)

    with pytest.raises(KeyError):
        container.find(Foo)


def test_factory_named_multiple() -> None:
    from huarache.service_locator import Registry

    registry = Registry()
    registry.register_factory(FooImpl2, Foo, name="scond")
    registry.register_factory(foo_factory, Foo, name="first")
    assert registry.find_names(Foo) == ["first", "scond"]
    container = registry.create_container()
    ins1 = container.find(Foo, name="first")
    ins2 = container.find(Foo, name="scond")
    assert ins1 is not ins2


@pytest.mark.asyncio
async def test_factory_async() -> None:
    from huarache.service_locator import Registry

    registry = Registry()
    registry.register_factory(async_foo_factory, Foo)
    fac = registry.find_factory(Foo)
    assert fac is async_foo_factory
    names = registry.find_names(Foo)
    assert names == [""]

    container = registry.create_container()
    ins = await container.async_find(Foo)
    assert isinstance(ins, FooImpl)

    ins2 = await container.async_find(Foo)
    assert isinstance(ins2, FooImpl)
    assert ins is ins2


def test_factory_async_from_normal() -> None:
    from huarache.service_locator import Registry

    registry = Registry()
    registry.register_factory(async_foo_factory, Foo)
    fac = registry.find_factory(Foo)
    assert fac is async_foo_factory

    container = registry.create_container()
    ins = container.find(Foo)
    assert isinstance(ins, FooImpl)


@pytest.mark.asyncio
async def test_factory_await_no_async() -> None:
    from huarache.service_locator import Registry

    registry = Registry()
    registry.register_factory(foo_factory, Foo)
    fac = registry.find_factory(Foo)
    assert fac is foo_factory
    names = registry.find_names(Foo)
    assert names == [""]

    container = registry.create_container()
    ins = await container.async_find(Foo)
    assert isinstance(ins, FooImpl)


def test_factory_method() -> None:
    from huarache.service_locator import Registry

    registry = Registry()
    registry.register_factory(FooImpl.factory, Foo)
    fac = registry.find_factory(Foo)
    assert fac == FooImpl.factory  # FIXME(gjo): actual is bounded
    names = registry.find_names(Foo)
    assert names == [""]

    container = registry.create_container()
    ins = container.find(Foo)
    assert isinstance(ins, FooImpl)


def test_raises_already_registered() -> None:
    from huarache.exceptions import AlreadyRegisteredError
    from huarache.service_locator import Registry

    registry = Registry()
    registry.register_factory(foo_factory, Foo)
    with pytest.raises(AlreadyRegisteredError):
        registry.register_factory(foo_factory, Foo)


def test_raises_does_not_registered() -> None:
    from huarache.service_locator import Registry

    registry = Registry()
    with pytest.raises(KeyError):
        registry.find_factory(Foo)

    with pytest.raises(KeyError):
        registry.find_names(Foo)
