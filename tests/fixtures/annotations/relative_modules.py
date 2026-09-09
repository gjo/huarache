from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import first
    from . import sibling as sibling_mod
    from .first import second


def valiations(
    p0: first.FooFirst,
    p1: sibling_mod.FooSibling,
    p2: second.FooSecond,
) -> None:
    return None  # pragma: no cover
