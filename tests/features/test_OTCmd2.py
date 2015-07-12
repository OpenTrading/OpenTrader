# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import os
import sys
import pdb

import pytest
from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import parse as p
from pytest_bdd.parsers import cfparse as cf

import OpenTrader
from OpenTrader import OTCmd2

@pytest.fixture(scope='session')
def oMain():
    sIni = os.path.join(os.path.dirname(OpenTrader.__file__), 'OTCmd2.ini')
    lCmdLine = ['-c', sIni]
    oMain = OTCmd2.oMain(lCmdLine)
    return oMain


lSHARE_EXAMPLES = None
sSHARE_EXAMPLES = ""
def vAddShareExamples(sStr):
    global lSHARE_EXAMPLES
    lSHARE_EXAMPLES += [sStr]

@given('Create the OTCmd2 instance')
def vTestCreated(oMain, capsys):
    # oMain.cmdqueue = ['help']
    oMain.onecmd('set echo True')
    sOut, sErr = capsys.readouterr()
    assert sOut
    assert 'True' in sOut
    #? should be sErr
    assert not sOut.startswith('ERR')

@then(p('The "{uCmd}" command stdout contains "{uStr}"'))
@then(p('The "{uCmd}" command output contains "{uStr}"'))
def vTestContains(oMain, capsys, uCmd, uStr):
    oMain.onecmd(uCmd)
    sOut, sErr = capsys.readouterr()
    assert sOut
    assert uStr in sOut
    #? should be sErr
    assert not sOut.startswith('ERR')

@then(p('The "{uCmd}" command stderr contains "{uStr}"'))
@then(p('The "{uCmd}" command error contains "{uStr}"'))
def vTestContains(oMain, capsys, uCmd, uStr):
    oMain.onecmd(uCmd)
    sOut, sErr = capsys.readouterr()
    assert sOut or sErr
    #? should be sErr
    assert uStr in sOut or uStr in sErr

@then(p('The "{uCmd}" command will {uStr}'))
def vTestWhen(oMain, capsys, uCmd, uStr):
    oMain.onecmd(uCmd)
    sOut, sErr = capsys.readouterr()
    if sOut: assert not sOut.startswith('ERR')
    if sErr: assert not sErr.startswith('ERR')
    vAddShareExamples('# ' +uStr)
    vAddShareExamples(uCmd)

@then('The result will be a not-null list')
def vThenNotNullList(oMain):
    assert len(oMain._G) > 0
    uStr = 'len(self._G) > 0'
    vAddShareExamples('py assert ' +uStr)

@then('The result will be a not-null string')
def vThenNotNullString(oMain):
    assert len(oMain._G) > 0
    uStr = 'len(self._G) > 0'
    vAddShareExamples('py assert ' +uStr)

@then(p('Comment {uStr}'))
def vComment(uStr):
    vAddShareExamples('# ' +uStr)

@then(p('Assert {uStr}'))
def vTestWhen(oMain, uStr):
    self = oMain
    assert eval(uStr)
    vAddShareExamples('py assert ' +uStr)

@given(p('Collect share/examples to file "{uFile}"'))
def vCollectShareExamples(uFile):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = uFile
    if lSHARE_EXAMPLES is None:
        lSHARE_EXAMPLES = ["# See the description in tests/features/OTCmd2.feature",]
    lSHARE_EXAMPLES += ['# echo the commands from the script so that we can watch the progress',
                       'set echo True']
#    pdb.set_trace()

@then(p('Write share/examples to "{uFile}"'))
def vWriteShareExamples(uFile):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    assert lSHARE_EXAMPLES and sSHARE_EXAMPLES
    lSHARE_EXAMPLES += ['exit']
    # FixMe: replace this with the tests/features directory
    with open(os.path.join('/tmp/', sSHARE_EXAMPLES), 'w') as oFd:
        oFd.write('\n'.join(lSHARE_EXAMPLES) +'\n')
    sys.stdout.write("Wrote share/examples to " +uFile +'\n')

@scenario('OTCmd2.feature', 'Load OTCmd2')
def test_scenario(capsys):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    lSHARE_EXAMPLES = []
    print ("hello")
    sys.stderr.write("world\n")
    out, err = capsys.readouterr()
    assert out == "hello\n"
    assert err == "world\n"
    print "next"
    out, err = capsys.readouterr()
    assert out == "next\n"

@given('Collect share/examples to "OTCmd2-backtest_omlette.txt"')
def vCollectShareExamplesOmlette():
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-backtest_omlette.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/OTCmd2.feature",
                      "# These tests will only work if you have pybacktest installed:",
                      "# https://github.com/ematvey/pybacktest",
                      "# You dont need to have a listener thread running",
                      '#',
                      '# These tests will only work if you have created a CSV file /tmp/EURUSD60-2014.csv']
    lSHARE_EXAMPLES += ['# echo the commands from the script so that we can watch the progress',
                       'set echo True']
#    pdb.set_trace()

@then('Write share/examples to "OTCmd2-backtest_omlette.txt"')
def vWriteShareExamples():
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    assert lSHARE_EXAMPLES and sSHARE_EXAMPLES
    lSHARE_EXAMPLES += ['exit']
    #? FixMe: replace this with the tests/features directory
    if not os.path.isdir('tmp'): os.mkdir('tmp')
    with open(os.path.join('tmp', sSHARE_EXAMPLES), 'w') as oFd:
        oFd.write('\n'.join(lSHARE_EXAMPLES) +'\n')
    sys.stdout.write("Wrote " +sSHARE_EXAMPLES +'\n')

@scenario('OTCmd2-backtest_omlette.feature', 'OTCmd2-backtest_omlette.txt')
def test_scenario_backtest_omlette(capsys):
    # FixMe: How do you get the arguments to @scenario in pytest_bdd
    pass

@given('Collect share/examples to "OTCmd2-backtest_recipe.txt"')
def vCollectShareExamplesRecipe():
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-backtest_recipe.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/OTCmd2-backtest_recipe.feature",
                      "# These tests will only work if you have pybacktest installed:",
                      "# https://github.com/ematvey/pybacktest",
                      "# You dont need to have a listener thread running",]
    lSHARE_EXAMPLES += ['# echo the commands from the script so that we can watch the progress',
                       'set echo True']

@then('Write share/examples to "OTCmd2-backtest_recipe.txt"')
def vWriteShareExamples():
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    assert lSHARE_EXAMPLES and sSHARE_EXAMPLES
    lSHARE_EXAMPLES += ['exit']
    #? FixMe: replace this with the tests/features directory
    if not os.path.isdir('tmp'): os.mkdir('tmp')
    with open(os.path.join('tmp', sSHARE_EXAMPLES), 'w') as oFd:
        oFd.write('\n'.join(lSHARE_EXAMPLES) +'\n')
    sys.stdout.write("Wrote " +sSHARE_EXAMPLES +'\n')


@scenario('OTCmd2-backtest_recipe.feature', 'OTCmd2-backtest_recipe.txt')
def test_scenario_backtest_recipe(capsys):
    """ BIZARRE SIDE EFFECT if you dont have capsys in the scenario function:

    tests/features/test_OTCmd2.py:69: in vTestWhen
        sOut, sErr = capsys.readouterr()
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    self = <_pytest.capture.CaptureFixture instance at 0xb0f66fcc>

        def readouterr(self):
            try:
                return self._capture.readouterr()
            except AttributeError:
    >           return self._outerr
    E           AttributeError: CaptureFixture instance has no attribute '_outerr'

    /usr/lib/python2.7/site-packages/_pytest/capture.py:198: AttributeError
    """
    pass
