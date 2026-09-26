from .interfaces import IBar, IBaz, IFoo
from .testing_decorators import service


@service(IFoo)
class Foo:
    pass


@service(IBar)
class Bar:
    pass


@service(IBaz)
class Baz:
    pass
