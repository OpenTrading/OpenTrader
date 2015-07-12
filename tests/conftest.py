# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
Configuration for pytest runner.
"""

import sys, os
import pytest

# we may need this to run the tests in the source directory uninstalled
sRootDir = os.path.dirname(os.path.dirname(__file__))
if sRootDir not in sys.path:
    sys.path.insert(0, sRootDir)
del sRootDir

# what does , 'capturemanager' do? It's undocumented.
pytest_plugins = ('pytest_bdd',)

@pytest.fixture(scope='session')
def splinter_webdriver():
    """Override splinter webdriver name."""
    return 'firefox'


