from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import BarForAnnotaion as ParentBar  # noqa: TID252
    from .. import FooForAnnotaion  # noqa: TID252
    from . import Bar as MyBar
    from . import Foo
    from .first import BarFirst as Bar1
    from .first import FooFirst
    from .first.second import BarSecond as Bar2
    from .first.second import FooSecond
    from .sibling import BarSibling as BarS
    from .sibling import FooSibling


def valiations(  # noqa: PLR0913, PLR0917
    p0: FooForAnnotaion,
    p1: ParentBar,
    p2: Foo,
    p3: MyBar,
    p4: FooFirst,
    p5: Bar1,
    p6: FooSecond,
    p7: Bar2,
    p8: FooSibling,
    p9: BarS,
) -> None:
    return None  # pragma: no cover
