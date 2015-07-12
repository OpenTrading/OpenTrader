# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import os
import sys
import pdb

import OpenTrader
from OpenTrader import OTCmd2

from support import tools

oMAIN = None
lSHARE_EXAMPLES = None
sSHARE_EXAMPLES = ""
def vAddShareExamples(sStr):
    global lSHARE_EXAMPLES
    lSHARE_EXAMPLES += [sStr]

iLEN_STDOUT = 0
iLEN_STDERR = 0
def lCheckStdoutStdErr(oCtx):
    """
    Checks stdout and stderr for error markers.
    Just check and return the stdout/err from this step.
    Raises AssertionError if it finds them.
    Returns a tuple of strings (sOut, sErr,)
    """
    global iLEN_STDOUT
    sOut = ""
    if hasattr(oCtx, 'stdout_capture'):
        sOut = oCtx.stdout_capture.getvalue().strip()
        iLen = len(sOut)
        #? should be sErr
        if sOut and iLen > iLEN_STDOUT:
            sOut = sOut[iLEN_STDOUT:]
            iLEN_STDOUT = iLen
            assert 'Traceback (most recent call last):' not in sOut
            assert not sOut.startswith('ERR')
            
    sErr = ""
    global iLEN_STDERR
    if hasattr(oCtx, 'stderr_capture'):
        sErr = oCtx.stderr_capture.getvalue().strip()
        iLen = len(sErr)
        if sErr and iLen > iLEN_STDERR:
            sOut = sOut[iLEN_STDERR:]
            iLEN_STDERR = iLen
            assert 'Traceback (most recent call last):' not in sErr
            assert not sErr.startswith('ERR')
    return (sOut, sErr,)

@step('Create the OTCmd2 instance')
def vTestCreated(oCtx):
    global oMAIN
    sIni = os.path.join(os.path.dirname(OpenTrader.__file__), 'OTCmd2.ini')
    lCmdLine = ['-c', sIni]
    oMAIN = OTCmd2.oMain(lCmdLine)
    # oMAIN.cmdqueue = ['help']
    oMAIN.onecmd('set echo True')
    sOut, sErr = lCheckStdoutStdErr(oCtx)
    assert sOut
    assert 'True' in sOut

@step('Destroy the OTCmd2 instance')
def vTestCreated(oCtx):
    global oMAIN
    oMAIN.vAtexit()
    
@step('The "{uCmd}" command stdout contains "{uStr}"')
@step('The "{uCmd}" command output contains "{uStr}"')
def vTestContains(oCtx, uCmd, uStr):
    oMAIN.onecmd(uCmd)
    sOut, sErr = lCheckStdoutStdErr(oCtx)
    assert sOut
    assert uStr in sOut
    
@step('The "{uCmd}" command stderr contains "{uStr}"')
@step('The "{uCmd}" command error contains "{uStr}"')
def vTestContains(oCtx, uCmd, uStr):
    oMAIN.onecmd(uCmd)
    sOut, sErr = lCheckStdoutStdErr(oCtx)
    assert sErr
    assert uStr in sErr
    
@step('The "{uCmd}" command will {uStr}')
def vCommandWill(oCtx, uCmd, uStr):
    oMAIN.onecmd(uCmd)
    sOut, sErr = lCheckStdoutStdErr(oCtx)
    if sOut and bool(oCtx.config.verbose):
        tools.puts(oCtx, *sOut.split('\n'))
    vAddShareExamples('# ' +uStr)
    vAddShareExamples(uCmd)

@step('The result will be a not-null list')
def vThenNotNullList(oCtx):
    assert len(oMAIN._G) > 0
    uStr = 'len(self._G) > 0'
    vAddShareExamples('py assert ' +uStr)

@step('The result will be a not-null string')
def vThenNotNullString(oCtx):
    assert len(oMAIN._G) > 0
    uStr = 'len(self._G) > 0'
    vAddShareExamples('py assert ' +uStr)

@step('Comment {uStr}')
def vComment(oCtx, uStr):
    vAddShareExamples('# ' +uStr)

@step('Assert {uStr}')
def vTestAssert(oCtx, uStr):
    self = oMAIN
    if not uStr: return
    assert eval(uStr)
    vAddShareExamples('py assert ' +uStr)

@step('Collect share/examples to file "{uFile}"')
def vCollectShareExamples(oCtx, uFile):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = uFile
    if lSHARE_EXAMPLES is None:
        lSHARE_EXAMPLES = ["# See the description in tests/features/OTCmd2.feature",]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']
#    pdb.set_trace()
    
@step('Write the share/examples file')
def vWriteShareExamples(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    assert lSHARE_EXAMPLES and sSHARE_EXAMPLES
    if lSHARE_EXAMPLES[-1] != 'exit':
        lSHARE_EXAMPLES += ['exit']
    # FixMe: replace this with the tests/features directory
    if not os.path.isdir('tmp'): os.mkdir('tmp')
    sFile = os.path.join('tmp', sSHARE_EXAMPLES)
    with open(sFile, 'w') as oFd:
        oFd.write('\n'.join(lSHARE_EXAMPLES) +'\n')
    sys.stdout.write('\n' +"Wrote share/examples to " +sFile +'\n')
    
@step('Collect share/examples to "OTCmd2-backtest_omlette.txt"')
def vCollectShareExamplesOmlette(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-backtest_omlette.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests will only work if you have pybacktest installed:",
                       "# https://github.com/ematvey/pybacktest",
                       "# You dont need to have a listener thread running",
                       '#',
                       "# These tests will only work if you have created a CSV file /tmp/EURUSD60-2014.csv"]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']

# FixMe: under behave it's easy to coalesce these
@step('Collect share/examples to "OTCmd2-backtest_recipe.txt"')
def vCollectShareExamplesRecipe(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-backtest_recipe.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests will only work if you have pybacktest installed:",
                       "# https://github.com/ematvey/pybacktest",
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']

@step('Collect share/examples to "OTCmd2-rabbit.txt"')
def vCollectShareExamplesRabbit(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-rabbit.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests will only work if you have pyrabbit installed:",
                       '# http://pypi.python.org/pypi/pyrabbit',
                       "# and have the 'rabbitmq_management' plugin to rabbitmq enabled.",
                       "# See the OS command 'rabbitmq-plugins list' and make sure",
                       "# the 'rabbitmq_management' and 'rabbitmq_web_dispatch' plugins are enabled.",
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']

@step('Collect share/examples to "OTCmd2-backtest_feed_plot.txt"')
def vCollectShareExamplesFeedPlot(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-backtest_feed_plot.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests require matplotlib be installed, AND REQUIRE HUMAN INTERACTION",
                       "# to close the plot once it is displayed.",
                       "# These tests will only work if you have pybacktest installed:",
                       "# https://github.com/ematvey/pybacktest",
                       "# ",
                       "# These tests will only work if you have created a CSV file tmp/EURUSD60-2014.csv",
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']

@step('Collect share/examples to "OTCmd2-ord.txt"')
def vCollectShareExamplesOrd(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-ord.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests will only work if you have an OTMql4AMQP enabled Metatrader running,",
                       "# the Experts/OTMql4/OTPyTestPikaEA.mq4 attached to a chart in it, and",
                       "# the RabbitMQ server configured and running."
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']

@step('Collect share/examples to "OTCmd2-sub.txt"')
def vCollectShareExamplesSub(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-sub.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests will only work if you have an OTMql4AMQP enabled Metatrader running,",
                       "# the Experts/OTMql4/OTPyTestPikaEA.mq4 attached to a chart in it, and",
                       "# the RabbitMQ server configured and running."
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']

@step('Collect share/examples to "OTCmd2-pub_wait.txt"')
def vCollectShareExamplesPubWait(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-pub_wait.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests will only work if you have an OTMql4AMQP enabled Metatrader running,",
                       "# the Experts/OTMql4/OTPyTestPikaEA.mq4 attached to a chart in it, and",
                       "# the RabbitMQ server configured and running."
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']


@step('Collect share/examples to "OTCmd2-pub_wait-jOT.txt"')
def vCollectShareExamplesPubWaitJOT(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-pub_wait-jOT.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These are some simple examples of commands that dont need any",
                       "# arguments, and return their results in JSON",
                       "# These tests will only work if you have an OTMql4AMQP enabled Metatrader running,",
                       "# the Experts/OTMql4/OTPyTestPikaEA.mq4 attached to a chart in it, and",
                       "# the RabbitMQ server configured and running."
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']

@step('Collect share/examples to "OTCmd2-pub_wait-Accounts.txt"')
def vCollectShareExamplesPubWaitAccounts(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = 'OTCmd2-pub_wait-Accounts.txt'
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests will only work if you have an OTMql4AMQP enabled Metatrader running,",
                       "# the Experts/OTMql4/OTPyTestPikaEA.mq4 attached to a chart in it, and",
                       "# the RabbitMQ server configured and running."
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']


@step('Collect share/examples to "OTCmd2-chart.txt"')
def vCollectShareExamplesChart(oCtx):
    global lSHARE_EXAMPLES, sSHARE_EXAMPLES
    sSHARE_EXAMPLES = "OTCmd2-chart.txt"
    lSHARE_EXAMPLES = ["# See the description in tests/features/" +sSHARE_EXAMPLES,
                       "# These tests will only work if you have an OTMql4AMQP enabled Metatrader running,",
                       "# the Experts/OTMql4/OTPyTestPikaEA.mq4 attached to a chart in it, and",
                       "# the RabbitMQ server configured and running."
                       ]
    lSHARE_EXAMPLES += ["# echo the commands from the script so that we can watch the progress",
                       'set echo True']

