from typing import Protocol


class IFoo(Protocol): ...


class IBar(Protocol): ...


class IBaz(Protocol): ...


class ITarget1(Protocol):
    foo: IFoo
    bar: IBar
    baz: IBaz
