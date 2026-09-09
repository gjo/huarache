class HuaracheError(Exception):
    pass


class LocatorError(HuaracheError):
    pass


class AlreadyRegisteredError(LocatorError):
    pass


class AlreadyCommitedError(LocatorError):
    pass


class AnnotaionResolverError(HuaracheError):
    pass


class DoesNotGetModuleError(AnnotaionResolverError):
    pass
