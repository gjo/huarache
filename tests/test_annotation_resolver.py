from collections.abc import Collection, Mapping
from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, Any

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


def test_annotation_variation_absolute() -> None:
    from huarache.annotation_resolver import AnnotationResolver
    from tests.fixtures.annotations.variations_absolute import valiations

    resolver = AnnotationResolver()
    result = resolver(valiations)
    assert list(result.keys()) == ["p0", "p1", "p2", "p3", "p4", "p5", "p6", "return"]


def test_annotation_variation_relative() -> None:
    from huarache.annotation_resolver import AnnotationResolver
    from tests.fixtures.annotations.variations_relative import valiations

    resolver = AnnotationResolver()
    result = resolver(valiations)
    assert list(result.keys()) == ["p0", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "return"]


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
