import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "tests.fixtures.blank_activator",
        "tests.fixtures.less_activator",
    ],
)
def test_config(module_name: str) -> None:
    from huarache.config import Configurator
    from huarache.exceptions import AlreadyCommitedError

    config = Configurator()
    assert len(config._included) == 0
    config.include(module_name)
    assert len(config._included) == 1
    config.include(module_name)
    assert len(config._included) == 1
    config.commit()
    with pytest.raises(AlreadyCommitedError):
        config.include(module_name)
