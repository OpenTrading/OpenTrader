# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

sUSAGE__doc__ = """
This script can be run from the command line to send commands
to a OTMql4Pika enabled Metatrader. It will start a command loop to
listen, send commands, based on the cmd2 REPL, or take commands from
the standard input, or take commands ascommand-line arguments.

Type help at the command prompt to get more help, or
call the script with --help to see the script options.
"""
# This assumes post processing by cmd2help_to_creole.sh
sUSAGE_EPILOG__doc__ = """

The subcommands are:
* subscribe - Subscribe to messages from RabbitMQ on a given topic (sub)
* publish   - Publish a message to a given chart on a OTMql4Py enabled terminal (pub)
* chart     - Set and query the chart in Metatrdaer that the messages are sent to
* order     - Manage orders in an OTMql4AQMp enabled Metatrader (ord)
* csv       - Download, resample and convert CSV files into pandas
* backtest  - Backtest recipes with chefs, and serve the results as metrics or plots (back)
* rabbit    - Introspect some useful information from the RabbitMQ server

Useful cmd2 subcommands are:
* history     - show the command history; rereun commands with: run.
* load FILE   - load a script of commands from FILE.
* save * FILE - save a script of commands to FILE; use * for all commands,
                a number for that command, or nothing for the last command.
* edit        - edit the previous command in an editor, or edit *, or edit FILE;
                commands are run after editor is closed; used EDITOR environment var.
* py [CMD]    - execute a Python command CMD, or with no arguments, enter a Python loop:
                In the loop: self = CMD2 object, self.oOm = Omellete, self.oOm.oBt = Oven
* help [SUB]  - help, or help on subcommand SUB.
"""
sUSAGE_MAYBE__doc__ = """
The normal usage is:
{{{
sub get                   - get the current target to publish to; defaults to:
                            the first value of default['lOnlineTargets'] in OTCmd2.ini
sub run [timer# ...]      - start a thread listening for messages: defaults to:
                          all messages, or use: timer.# and/or bar.# tick.# retval.#
pub wait AccountBalance    - to send a command such as AccountBalance to OTMql4Pika,
                           the return will be a retval message on the listener
sub hide timer            - stop seeing timer messages (just see the retval.#)
order list                - list your open order tickets
}}}
"""

import sys
import os
import traceback
import threading
import time
import unittest
from optparse import OptionParser, make_option

if hasattr(sys, 'frozen') and sys.frozen:
    __file__ = sys.executable
else:
    try:
        import OpenTrader
    except ImportError:
        # FixMe: name == '__main__'
        # support running from source
        sDIR = os.path.dirname(os.path.dirname(__file__))
        if sDIR not in sys.path:
            sys.path.insert(0, sDIR)
        del sDIR

from OpenTrader.deps.cmd2plus import Cmd, Cmd2TestCase
from OpenTrader.PLogMixin import PLogMixin

try:
    from OpenTrader.deps import tabview
except ImportError:
    # depends on curses
    tabview = None

from OpenTrader import csver
from OpenTrader import charter
from OpenTrader import subscriber
from OpenTrader import publisher
from OpenTrader import orderer
from OpenTrader import backtester
from OpenTrader import rabbiter
from OpenTrader import maker

from OTCmd2_utils import options

class Mt4Timeout(RuntimeError):
    pass

class CmdLineApp(Cmd, PLogMixin):
    multilineCommands = []
    testfiles = ['exampleSession.txt']

    oMixin = None
    oListenerThread = None
    oRabbit = None

    def __init__(self, oConfig, lArgs):
        Cmd.__init__(self)
        self.oConfig = oConfig
        self.lArgs = lArgs
        self.lTopics = ['#']
        self.sDefaultChart = ""
        self.oCurrentSubTarget = None
        self.oCurrentPubTarget = None
        # FixMe: refactor for multiple charts
        self.dCharts = {}
        # Keep a copy of what goes out;
        # I'm not sure how these will be used yet.
        self.dLastCmd = {}
        self.dLastEval = {}
        self.dLastJson = {}
        self.oBt = None
        self._G = None

        if hasattr(sys, 'frozen') and sys.frozen:
            self.sRoot = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
            self.prompt = 'OT11> '
        else:
            self.sRoot = os.path.dirname(os.path.dirname(__file__))
            self.prompt = 'OTPy> '
        
        sRecipesDir = oConfig['OTCmd2']['sRecipesDir']
        if not sRecipesDir:
            sRecipesDir = os.path.join(self.sRoot, 'share', 'recipes')
        elif not os.path.isabs(sRecipesDir):
            sRecipesDir = os.path.join(self.sRoot, sRecipesDir)
        else:
            sRecipesDir = os.path.expanduser(os.path.expandvars(sRecipesDir))
        if not os.path.isdir(sRecipesDir):
            self.vWarn("sRecipesDir not found: " + sRecipesDir)
        else:
            oConfig['OTCmd2']['sRecipesDir'] = sRecipesDir
            if sRecipesDir not in sys.path:
                sys.path.insert(0, sRecipesDir)
            
        sMt4Dir = oConfig['OTCmd2']['sMt4Dir']
        if sMt4Dir:
            sMt4Dir = os.path.expanduser(os.path.expandvars(sMt4Dir))
            if not os.path.isdir(sMt4Dir):
                self.vWarn("sMt4Dir not found: " + sMt4Dir)
            elif not hasattr(sys, 'frozen') or not sys.frozen:
                # we will need to add to import PikaChart or ZmqChart
                sMt4Dir = os.path.join(sMt4Dir, 'MQL4', 'Python')
                if not os.path.isdir(os.path.join(sMt4Dir, 'OTMql427')):
                    self.vWarn("MQL4/Python/OTMql427 not found in: " + sMt4Dir)
                elif sMt4Dir not in sys.path:
                    sys.path.insert(0, sMt4Dir)

    def G(self, gVal=None):
        if gVal is not None:
            self._G = gVal
        return self._G

    def vConfigOp(self, lArgs, dConfig):
        from OpenTrader.OTUtils import lConfigToList

        if len(lArgs) == 2:
            self.vOutput(pformat(self.G(dConfig())))
        elif len(lArgs) == 3 and tabview and str(lArgs[2]) == 'tabview':
            l = lConfigToList(dConfig())
            tabview.view(l, column_width=max)
        elif len(lArgs) == 3:
            sSect = str(lArgs[2])
            self.vOutput(repr(self.G(dConfig(sSect))))
        elif len(lArgs) == 4:
            sSect = str(lArgs[2])
            sKey = str(lArgs[3])
            self.vOutput(repr(self.G(dConfig(sSect, sKey))))
        elif len(lArgs) == 5:
            sSect = str(lArgs[2])
            sKey = str(lArgs[3])
            sVal = str(lArgs[5])
            oType = type(dConfig(sSect, sKey))
            gRetval = dConfig(sSect, sKey, oType(sVal))
            self.vOutput(repr(self.G(gRetval)))

    def eSendOnSpeaker(self, sChartId, sMsgType, sMsg):
        if sMsgType == 'cmd' and self.oListenerThread is None:
            self.vWarn("ListenerThread not started; you will not see the retval")
        if self.oCurrentPubTarget is None:
            sErr = "PubTarget not set; use \"pub set\""
            self.vError(sErr)
            return sErr

        # self.oCurrentPubTarget is a ConfigObj section: dictionary-like
        assert 'sOnlineRouting' in self.oCurrentPubTarget
        assert self.oCurrentPubTarget['sOnlineRouting']
        sOnlineRouting = self.oCurrentPubTarget['sOnlineRouting']
        if not self.oMixin:
            if sOnlineRouting == 'RabbitMQ':
                from OTMql427 import PikaListener
                # FixMe: refactor for multiple charts
                self.oMixin = PikaListener.PikaMixin(sChartId, **self.oCurrentPubTarget)
            elif sOnlineRouting == 'ZeroMQ':
                from OTMql427 import ZmqListener
                # FixMe: refactor for multiple charts
                self.oMixin = ZmqListener.ZmqMixin(sChartId, **self.oCurrentPubTarget)
                self.oMixin.eConnectToReq()
            else:
                raise RuntimeError("sOnlineRouting value in %s section of Cmd2.ini not supported" % (
                    sOnlineRouting,))

        self.vInfo("Publishing via " +sOnlineRouting +": " +sMsg)
        if sOnlineRouting == 'RabbitMQ':
            return(self.oMixin.eSendOnSpeaker(sMsgType, sMsg))
        elif sOnlineRouting == 'ZeroMQ':
            return(self.oMixin.eSendOnReqRep(sMsgType, sMsg))
        return ""

    def eSendMessage(self, sMsgType, sChartId, sMark, *lArgs):
        from OTMql427.SimpleFormat import sFormatMessage
        sMsg = sFormatMessage(sMsgType, sChartId, sMark, *lArgs)
        e = self.eSendOnSpeaker(sChartId, sMsgType, sMsg)
        self.dLastCmd[sChartId] = sMsg
        return e

    def gWaitForMessage(self, sMsgType, sChartId, sMark, *lArgs):
        """
        Raises a Mt4Timeout error if there is no answer in
        oOptions['OTCmd2']['iRetvalTimeout'] seconds.

        Raising an error lets us return None as a return value.
        The protocol talking to Mt4 has the void return type,
        which gRetvalToPython returns as None.
        """
        from OTMql427.SimpleFormat import gRetvalToPython, lUnFormatMessage
        self.eSendMessage(sMsgType, sChartId, sMark, *lArgs)
        i = 0
        iTimeout = self.oConfig['OTCmd2']['iRetvalTimeout']
        self.vDebug("Waiting for: " +sMsgType +" " +sMark)
        while i < int(iTimeout):
            if sMsgType == 'exec':
                s = self.oMixin.sRecvReply()
                if s != "":
                    gRetval = gRetvalToPython(lUnFormatMessage(s))
                    return self.G(gRetval)
                # drop through
            elif sMsgType == 'cmd':
                if sMark in self.oListenerThread.dRetvals.keys():
                    gRetval = self.oListenerThread.dRetvals[sMark]
                    del self.oListenerThread.dRetvals[sMark]
                    return self.G(gRetval)
            else:
                self.vError("Unrecognized sMsgType: " +sMsgType)
                return None
            i += 5
            self.vDebug("Waiting: " +repr(i))
            time.sleep(5.0)
        self._G = None
        raise Mt4Timeout("No retval returned in " +str(iTimeout) +" seconds")

    ## csv
    @options(csver.LOPTIONS,
             arg_desc='|'.join(csver.LCOMMANDS),
             usage=csver.__doc__,
             )
    def do_csv(self, oArgs, oOpts=None):
        if not hasattr(self, 'oCsver'):
            self.oCsver = csver.DoCsv(self)
        largs = oArgs.split()
        bretval = self.oCsver.bexecute(largs, oOpts)

    ## chart
    @options(charter.LOPTIONS,
             arg_desc='|'.join(charter.LCOMMANDS),
             usage=charter.__doc__,
             )
    def do_chart(self, oArgs, oOpts=None):
        if not hasattr(self, 'oCharter'):
            self.oCharter = charter.DoChart(self)
        largs = oArgs.split()
        bretval = self.oCharter.bexecute(largs, oOpts)

    ## subscribe
    @options(subscriber.LOPTIONS,
             arg_desc='|'.join(subscriber.LCOMMANDS),
             usage=subscriber.__doc__,
             )
    def do_subscribe(self, oArgs, oOpts=None):
        if not hasattr(self, 'oSubscriber'):
            self.oSubscriber = subscriber.DoSubscribe(self)
        largs = oArgs.split()
        bretval = self.oSubscriber.bexecute(largs, oOpts)

    do_sub = do_subscribe

    ## publish
    @options(publisher.LOPTIONS,
             arg_desc='|'.join(publisher.LCOMMANDS),
             usage=publisher.__doc__,
             )
    def do_publish(self, oArgs, oOpts=None):
        if not hasattr(self, 'oPublisher'):
            self.oPublisher = publisher.DoPublish(self)
        largs = oArgs.split()
        bretval = self.oPublisher.bexecute(largs, oOpts)

    do_pub = do_publish

    ## order
    @options(orderer.LOPTIONS,
             arg_desc='|'.join(orderer.LCOMMANDS),
             usage=orderer.__doc__,
             )
    def do_order(self, oArgs, oOpts=None):
        if not hasattr(self, 'orderer'):
            self.orderer = orderer.DoOrder(self)
        largs = oArgs.split()
        bretval = self.orderer.bexecute(largs, oOpts)

    do_ord = do_order

    # backtest
    @options(backtester.LOPTIONS,
             arg_desc='|'.join(backtester.LCOMMANDS),
             usage=backtester.__doc__,
             )
    def do_backtest(self, oArgs, oOpts=None):
        # might let it import to list recipes and chefs?
        try:
            import pybacktest
        except ImportError as e:
            self.vError("pybacktest not installed: " +str(e))
            return
        if not hasattr(self, 'oBacktester'):
            self.oBacktester = backtester.DoBacktest(self)
        largs = oArgs.split()
        bretval = self.oBacktester.bexecute(largs, oOpts)


    do_back = do_backtest
    do_bac = do_backtest

    ## make
    @options(maker.LOPTIONS,
             arg_desc='|'.join(maker.LCOMMANDS),
             usage=maker.__doc__,
             )
    def do_make(self, oArgs, oOpts=None):
        if not hasattr(self, 'oMaker'):
            self.oMaker = maker.DoMake(self)
        largs = oArgs.split()
        bretval = self.oMaker.bexecute(largs, oOpts)

    ## rabbit
    @options(rabbiter.LOPTIONS,
             arg_desc='|'.join(rabbiter.LCOMMANDS),
             usage=rabbiter.__doc__,
             )
    def do_rabbit(self, oArgs, oOpts=None):
        if not hasattr(self, 'rabbiter'):
            self.rabbiter = rabbiter.DoRabbit(self)
        largs = oArgs.split()
        bretval = self.rabbiter.bexecute(largs, oOpts)


    def vAtexit(self):
        self.vDebug("atexit")
        if self.oListenerThread is not None:
            if True:
                # new code
                self.oListenerThread.stop()
                self.oListenerThread.join()
            else:
                # RuntimeError: concurrent poll() invocation
                self.vDebug("oListenerThread.bCloseConnectionSockets")
                self.oListenerThread.bCloseConnectionSockets()
                self.oListenerThread = None
        if hasattr(self, 'oMixin') and self.oMixin:
            # Ive seen it hang here - maybe fixed now
            # FixMe: refactor for multiple charts
            try:
                sys.stdout.write("DEBUG: Waiting for message queues to flush...\n")
                self.oMixin.bCloseConnectionSockets()
                self.oMixin = None
                time.sleep(1.0)
            except (KeyboardInterrupt,):
                # impatient
                pass

# FixMe: should do_exit call vAtexit ?

def vNullifyLocalhostProxy(sHost):
    """
    We probably dont want to go via a proxy to localhost.
    """
    if sHost not in ['localhost', "127.0.0.1"]: return
    for sElt in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY',]:
        if sElt in os.environ: del os.environ[sElt]

# legacy - reuse?
class TestMyAppCase(Cmd2TestCase):
    CmdApp = CmdLineApp
    transcriptFileName = 'exampleSession.txt'

def oParseOptions():
    """
    Look at the bottom of PikaListener.py and PikaChart.py for iMain
    functions that use the oParseOptions that is returned here.
    This function returns an ArgumentParser instance, so that you
    can override it before you call it to parse_args.
    """
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    oArgParser = ArgumentParser(description=sUSAGE__doc__ + sUSAGE_EPILOG__doc__,
#                                epilog=sUSAGE_EPILOG__doc__.strip(),
                                formatter_class=RawDescriptionHelpFormatter)

    oArgParser.add_argument("-v", "--verbose", action="store",
                            dest="iVerbose", type=int, default=4,
                            help="the verbosity, 0 for silent 4 max (default 4)")
    oArgParser.add_argument('-t', '--test',
                            dest='bUnittests', action='store_true', default=False,
                            help='Run unit test suite')
    oArgParser.add_argument('-s', '--set',
                            dest='lSet', action='append', nargs=2,
                            help='Set cmd2 settables, followed by name and value - repeat if needed')
    oArgParser.add_argument('-c', '--config',
                            dest='sConfigFile', default="OTCmd2.ini",
                            help='Config file for OTCmd2 options')
    #? as a convenience we let arguments from the [default] section
    #? of the ini file be overridden from the command line
    #? we default these to "" so that the config file takes precedence
    oArgParser.add_argument('-P', "--mt4dir", action="store",
                            dest="sMt4Dir", default="",
                            help="directory for the installed Metatrader")
    oArgParser.add_argument("-T", "--target", action="store",
                            dest="sOnlineTarget", default="",
                            help="ini section name with the routing and target")
    oArgParser.add_argument("-R", "--timeout", action="store",
                            dest="iRetvalTimeout", type=int, default=0,
                            help="Timeout for waiting for a retval from publishing to Mt4")
    #? sOmlettesDir
    #? matplotlib_use?
    oArgParser.add_argument('lArgs', action="store",
                            nargs="*",
                            help="command line arguments (optional)")
    return(oArgParser)

def oParseConfig(sConfigFile):
    from configobj import ConfigObj
    if not os.path.isabs(sConfigFile):
        sConfigFile = os.path.join(os.path.dirname(__file__), sConfigFile)
        assert os.path.isfile(sConfigFile), "Missing configuration file: " + sConfigFile
    else:
        sConfigFile = os.path.expanduser(os.path.expandvars(sConfigFile))
        assert os.path.isfile(sConfigFile), "Configuration file not found: " + sConfigFile
    return ConfigObj(sConfigFile, unrepr=True)

def oMergeConfig(oConfig, oOptions):
    """
    # FixMe: merge the arguments into the [OTCmd2] section of the configFile
    #? If so use update on the config object with the options.__dict__
    """
    # do it manually for now
    for sKey in ['sMt4Dir', 'sOnlineTarget', 'iRetvalTimeout']:
        if hasattr(oOptions, sKey):
            gValue = getattr(oOptions, sKey)
            # skip null values for now
            if not gValue: continue
            if sKey == 'sOnlineTarget':
                oConfig['OTCmd2']['lOnlineTargets'] = [gValue]
            else:
                oConfig['OTCmd2'][sKey] = gValue
            # del?
        else:
            print "WARN: unrecognized oConfig key: " +sKey
    return oConfig

def iMain(lCmdLine):

    if '--test' in lCmdLine:
        # legacy - unused
        sys.argv = [sys.argv[0]]  # the --test argument upsets unittest.main()
        unittest.main()
        return 0

    oApp = None
    try:
        oArgParser = oParseOptions()
        oOptions = oArgParser.parse_args(lCmdLine)

        sConfigFile = oOptions.sConfigFile
        oConfig = oParseConfig(sConfigFile)
        oConfig = oMergeConfig(oConfig, oOptions)

        oApp = CmdLineApp(oConfig, oOptions.lArgs)

        if oOptions.lArgs:
            oApp.onecmd_plus_hooks(' '.join(oOptions.lArgs) +'\n')
        else:
            oApp._cmdloop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print traceback.format_exc(10)
    # always reached
    if oApp:
        oApp.vAtexit()

        l = threading.enumerate()
        if len(l) > 1:
            print "WARN: Threads still running: %r" % (l,)

if __name__ == '__main__':
    iMain(sys.argv[1:])

# grep '//0' ../../Libraries/OTMql4/OTLibMt4ProcessCmd.mq4 |sed -e 's/.*== "/pub /' -e 's/".*//' > OTCmd2-0.test
