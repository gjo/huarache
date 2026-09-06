class HuaracheError(Exception):
    pass


class AlreadyRegisteredError(HuaracheError):
    pass


class AlreadyCommitedError(HuaracheError):
    pass
