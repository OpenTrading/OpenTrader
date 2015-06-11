"""Configuration for pytest runner."""
pytest_plugins = 'pytest_bdd'

# we may need this to run the tests in the source directory uninstalled
import sys, os
sRootDir = os.path.dirname(os.path.dirname(__file__))
if sRootDir not in sys.path:
    sys.path.insert(0, sRootDir)
del sRootDir

import pytest

@pytest.fixture(scope='session')
def splinter_webdriver():
    """Override splinter webdriver name."""
    return 'firefox'


