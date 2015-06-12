# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import parse as p
from pytest_bdd.parsers import cfparse as cf

import OpenTrader
from OpenTrader import OTCmd2

@scenario('OTCmd2_ini.feature', 'Settings for OTCmd2 are in a configobj .ini file')
def test_configobj():
    pass

sIniFile = ""
@given('The configobj OTCmd2.ini exists')
def vIniFileExists():
    global sIniFile
    import os
    sIniFile = os.path.join(os.path.dirname(OTCmd2.__file__), 'OTCmd2.ini')
    assert sIniFile and os.path.exists(sIniFile)

oConfig = None
@given('The configobj OTCmd2.ini is parseable')
def vIniParseable():
    global oConfig
    from configobj import ConfigObj
    oConfig = ConfigObj(sIniFile, unrepr=True)
    assert oConfig

@given(p('The configobj has keys:\n{sKeys}'))
def vIniHasKey(sKeys):
    for sKey in sKeys.split():
        assert sKey in oConfig.keys()

@given(p('The configobj Section "{sSection}" has keys:\n{sKeys}'))
def vSectionHasKey(sSection, sKeys):
    for sKey in sKeys.split():
        assert sKey in oConfig[sSection].keys()

@then('Life is Good!')
def vLifeIsGood():
    pass
