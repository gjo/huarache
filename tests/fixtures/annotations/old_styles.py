from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import collections.abc as ca
    import typing
    from collections.abc import Collection as MyCollection
    from typing import Any as MyAny


def no_annotation(param1, param2):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    return [param1, param2]  # pragma: no cover


def comment_annotation(param1, param2):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    # (int, int) -> list[int]
    return [param1, param2]  # pragma: no cover


def string_annotation(param1: "MyAny", param2: "typing.Any") -> "MyCollection[MyAny]":  # noqa: UP037
    return [param1, param2]  # pragma: no cover


def normal_annotation(param1: MyAny, param2: typing.Any) -> ca.Collection[MyAny]:
    return [param1, param2]  # pragma: no cover
