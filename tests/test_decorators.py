from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


def test_autowire() -> None:
    from huarache.service_locator import Registry

    from .fixtures.decorators.impls import Bar, Baz, Foo
    from .fixtures.decorators.interfaces import ITarget1
    from .fixtures.decorators.target1 import Target1
    from .fixtures.decorators.testing_decorators import testing_instance

    settings: dict[str, Any] = {}
    registry = Registry(settings=settings)
    testing_instance.activate(registry, "tests.fixtures.decorators.impls")
    testing_instance.activate(registry, "tests.fixtures.decorators.target1")
    assert "tests.fixtures.decorators.impls" in testing_instance._registered
    assert len(testing_instance._registered["tests.fixtures.decorators.impls"]) == 3
    assert "tests.fixtures.decorators.target1" in testing_instance._registered
    assert len(testing_instance._registered["tests.fixtures.decorators.target1"]) == 1

    container = registry.create_container()
    target = container.find(ITarget1)
    assert isinstance(target, Target1)
    assert isinstance(target.foo, Foo)
    assert isinstance(target.bar, Bar)
    assert isinstance(target.baz, Baz)
