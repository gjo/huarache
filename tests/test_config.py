import pytest


def test_config() -> None:
    from huarache.config import Configurator
    from huarache.exceptions import AlreadyCommitedError

    config = Configurator()
    assert len(config._included) == 0
    config.include("tests.fixtures.blank_activator")
    assert len(config._included) == 1
    config.include("tests.fixtures.blank_activator")
    assert len(config._included) == 1
    config.commit()
    with pytest.raises(AlreadyCommitedError):
        config.include("tests.fixtures.blank_activator")
