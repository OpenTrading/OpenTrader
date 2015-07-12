# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

from OpenTrader import OTCmd2

sIniFile = ""

@given('The configobj OTCmd2.ini exists')
def vIniFileExists(oCtx):
    global sINI_FILE
    import os
    sINI_FILE = os.path.join(os.path.dirname(OTCmd2.__file__), 'OTCmd2.ini')
    assert sINI_FILE and os.path.exists(sINI_FILE)

oConfig = None
@given('The configobj OTCmd2.ini is parseable')
def vIniParseable(oCtx):
    global oConfig
    from configobj import ConfigObj
    oConfig = ConfigObj(sINI_FILE, unrepr=True)
    assert oConfig

@given('The configobj has keys:\n{sKeys}')
def vIniHasKey(oCtx, sKeys):
    for sKey in sKeys.split():
        assert sKey in oConfig.keys()

@given('The configobj Section "{sSection}" has keys:\n{sKeys}')
def vSectionHasKey(oCtx, sSection, sKeys):
    for sKey in sKeys.split():
        assert sKey in oConfig[sSection].keys()

@then('Life is Good!')
def vLifeIsGood(oCtx):
    pass
