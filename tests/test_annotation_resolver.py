from collections.abc import Collection, Mapping, Sized
from importlib import import_module
from logging import Logger
from types import ModuleType
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


def _expected_tests_fixtures_blank_activator_includeme() -> dict[str, Any]:
    from huarache.interfaces import Configurator

    return {"config": Configurator, "return": None}


def _expected_huarache_config_configurator() -> dict[str, Any]:
    from huarache.interfaces import ContainerFactory, RegistryFactory

    return {
        "registry_factory": RegistryFactory | None,
        "container_factory": ContainerFactory | None,
        "settings": Mapping[str, Any] | None,
        "return": None,
    }


def _expected_huarache_locator_registry() -> dict[str, Any]:
    from huarache.interfaces import ContainerFactory

    return {"container_factory": ContainerFactory | None, "return": None, "settings": Mapping[str, Any] | None}


def _expected_huarache_locator_container() -> dict[str, Any]:
    from huarache.interfaces import Registry

    return {"registry": Registry, "return": None}


@pytest.mark.parametrize(
    ("module_name", "callable_name", "expected"),
    [
        ("tests.fixtures.blank_activator", "includeme", _expected_tests_fixtures_blank_activator_includeme),
        ("huarache.annotation_resolver", "AnnotationResolver", {"return": None}),
        (
            "huarache.annotation_resolver",
            "get_type_checking_imports",
            {"module": ModuleType, "return": dict[str, Any]},
        ),
        (
            "huarache.annotation_resolver",
            "resolve_forwardref_recursive",
            {"annotation": Any, "globals_": dict[str, Any], "module": ModuleType, "return": Any},
        ),
        ("huarache.config", "Configurator", _expected_huarache_config_configurator),
        ("huarache.locator", "Registry", _expected_huarache_locator_registry),
        ("huarache.locator", "Container", _expected_huarache_locator_container),
    ],
)
def test_annotation_resolver_dogfooding(
    module_name: str, callable_name: str, expected: dict[str, Any] | Callable[[], dict[str, Any]]
) -> None:
    from huarache.annotation_resolver import AnnotationResolver

    module = import_module(module_name)
    callable_ = getattr(module, callable_name)
    if not isinstance(expected, dict):
        expected = expected()

    resolver = AnnotationResolver()
    actual = resolver(callable_)
    assert actual == expected


def test_annotation_old_style() -> None:
    from huarache.annotation_resolver import AnnotationResolver
    from tests.fixtures.annotations.old_styles import (
        comment_annotation,
        no_annotation,
        normal_annotation,
        string_annotation,
    )

    resolver = AnnotationResolver()
    assert resolver(no_annotation) == {}
    assert resolver(comment_annotation) == {}
    assert resolver(string_annotation) == {"param1": Any, "param2": Any, "return": Collection[Any]}
    assert resolver(normal_annotation) == {"param1": Any, "param2": Any, "return": Collection[Any]}


def test_annotation_absolute() -> None:
    from huarache.annotation_resolver import AnnotationResolver
    from tests.fixtures.annotations.absolute import valiations

    resolver = AnnotationResolver()
    result = resolver(valiations)
    assert result == {"p0": Any, "p1": Logger, "p2": Sized, "p3": Mock, "return": None}


def test_annotation_relative_modules() -> None:
    from huarache.annotation_resolver import AnnotationResolver
    from tests.fixtures.annotations.first import FooFirst
    from tests.fixtures.annotations.first.second import FooSecond
    from tests.fixtures.annotations.relative_modules import valiations
    from tests.fixtures.annotations.sibling import FooSibling

    resolver = AnnotationResolver()
    result = resolver(valiations)
    assert result == {"p0": FooFirst, "p1": FooSibling, "p2": FooSecond, "return": None}


def test_annotation_relative_vars() -> None:
    from huarache.annotation_resolver import AnnotationResolver
    from tests.fixtures import BarForAnnotation, FooForAnnotation
    from tests.fixtures.annotations import Bar, Foo
    from tests.fixtures.annotations.first import BarFirst, FooFirst
    from tests.fixtures.annotations.first.second import BarSecond, FooSecond
    from tests.fixtures.annotations.relative_vars import valiations
    from tests.fixtures.annotations.sibling import BarSibling, FooSibling

    resolver = AnnotationResolver()
    result = resolver(valiations)
    assert result == {
        "p0": FooForAnnotation,
        "p1": BarForAnnotation,
        "p2": Foo,
        "p3": Bar,
        "p4": FooFirst,
        "p5": BarFirst,
        "p6": FooSecond,
        "p7": BarSecond,
        "p8": FooSibling,
        "p9": BarSibling,
        "return": None,
    }


def test_annotation_cached() -> None:
    from huarache.annotation_resolver import AnnotationResolver
    from tests.fixtures.annotations.old_styles import normal_annotation

    resolver = AnnotationResolver()
    assert resolver._module_cache == {}
    assert resolver._object_cache == {}
    assert resolver(normal_annotation) == {"param1": Any, "param2": Any, "return": Collection[Any]}
    assert list(resolver._module_cache.keys()) == ["tests.fixtures.annotations.old_styles"]
    assert list(resolver._object_cache.keys()) == [normal_annotation]
    assert resolver(normal_annotation) == {"param1": Any, "param2": Any, "return": Collection[Any]}
