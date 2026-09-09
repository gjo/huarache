from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import collections.abc
    import logging as lg
    import typing
    import unittest.mock as umock

    from . import first
    from . import sibling as sibling_mod
    from .first import second


def valiations(  # noqa: PLR0913, PLR0917
    p0: typing.Any,
    p1: lg.Logger,
    p2: collections.abc.Sized,
    p3: umock.Mock,
    p4: first.FooFirst,
    p5: sibling_mod.FooSibling,
    p6: second.FooSecond,
) -> None:
    return None  # pragma: no cover
