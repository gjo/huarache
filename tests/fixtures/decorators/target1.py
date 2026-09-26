from .interfaces import IBar, IBaz, IFoo, ITarget1
from .testing_decorators import service


@service(ITarget1)
class Target1:
    def __init__(self, foo: IFoo, bar: IBar, baz: IBaz) -> None:
        self.foo = foo
        self.bar = bar
        self.baz = baz
