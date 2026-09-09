from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import collections.abc
    import logging as lg
    import typing
    import unittest.mock as umock


def valiations(
    p0: typing.Any,
    p1: lg.Logger,
    p2: collections.abc.Sized,
    p3: umock.Mock,
) -> None:
    return None  # pragma: no cover
