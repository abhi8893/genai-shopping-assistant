import time
import pytest
from importlib.metadata import distribution
from importlib.metadata import packages_distributions

import dummy_pkg


# TODO: Refactor out utils / common tests in a common package
def get_distribution_name(module):
    return packages_distributions()[module.__name__][0]

def is_editable_install(pkg_name: str) -> bool:
    dist = distribution(pkg_name)
    for file in dist.files or []:
        if str(file).endswith(".pth"):
            return True
    return False

DISTRIBUTION_NAME = get_distribution_name(dummy_pkg)

@pytest.mark.ci
def test_not_editable_install():
    assert not is_editable_install(DISTRIBUTION_NAME)

def test_small():
    assert True


@pytest.mark.slow
def test_long_running():
    time.sleep(0.1)
    assert True
