# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
This script can be run from the command line to send commands
to a OTMql4Pika enabled Metatrader. It will start a command loop to
listen, send commands, or query the RabbitMQ management interface, based
on the cmd2 REPL: see cmd2plus.py in https://github.com/OpenTrading/OTMql4Lib

Type help at the command prompt to get more help.

Call the script with --help to see the script options.

The normal usage is:

sub run timer# retval.#  - start a thread listening for messages: timer,tick,retval
pub cmd AccountBalance   - to send a command to OTMql4Pika,
                         the return will be a retval message on the listener
sub hide timer           - stop seeing timer messages (just see the retval.#)
order list               - list your open order tickets
"""

sCSV__doc__ = """
Download, resample and convert CSV files into pandas:

"""

sCHART__doc__ = """
Set and query the chart used for messages to and from RabbitMQ:
  list   - all the charts the listener has heard of,
           iff you have already started a listener with "sub run"
  get    - get the default chart to be published or subscribed to.
  set ID - set the default chart ID to be published or subscribed to.
  set    - set the default chart to be the last chart the listener has heard of,
           iff you have already started a listener with "sub run"

The chart ID will look something like: oChart_EURGBP_240_93ACD6A2_1
"""

sSUB__doc__ = """
Subscribe to messages from RabbitMQ on a given topic:
  sub topics            - shows topics subscribed to.
  sub run TOPIC1 ...    - start a thread to listen for messages,
                          TOPIC is one or more Rabbit topic patterns.
  sub hide TOPIC        - stop seeing TOPIC messages (e.g. tick - not a pattern)
  sub show              - list the message topics that are being hidden
  sub show TOPIC        - start seeing TOPIC messages (e.g. tick - not a pattern)
  sub pprint ?0|1       - seeing TOPIC messages with pretty-printing,
                          with 0 - off, 1 - on, no argument - current value
  sub thread info       - info on the thread listening for messages.
  sub thread stop       - stop a thread listening for messages.

Common RabbitMQ topic patterns are: # for all messages, tick.# for ticks,
timer.# for timer events, retval.# for return values.
You can choose as specific chart with syntax like:
    tick.oChart.EURGBP.240.93ACD6A2.#

The RabbitMQ host and login information is set in the `[RabbitMQ]`
section of the `OTCmd2.ini` file; see the `-c/--config` command-line options.
"""

sPUB__doc__ = """
Publish a message via RabbitMQ to a given chart on a OTMql4Py enabled terminal:
  pub cmd  COMMAND ARG1 ... - publish a Mql command to Mt4,
      the command should be a single string, with a space seperating arguments.
  pub wait COMMAND ARG1 ... - publish a Mql command to Mt4 and wait for the result,
      the command should be a single string, with a space seperating arguments.
  pub eval COMMAND ARG1 ... - publish a Python command to the OTMql4Py,
      the command should be a single string, with a space seperating arguments.

You wont see the return value unless you have already done a:
  sub run retval.#

The RabbitMQ host and login information is set in the `[RabbitMQ]`
section of the `OTCmd2.ini` file; see the `-c/--config` command-line options.
"""

# should these all be of chart ANY
sORD__doc__ = """
  ord list          - list the ticket numbers of current orders.
  ord info iTicket  - list the current order information about iTicket.
  ord trades        - list the details of current orders.
  ord history       - list the details of closed orders.
  ord close iTicket [fPrice iSlippage]            - close an order;
                    Without the fPrice and iSlippage it will be a market order.
  ord buy|sell sSymbol fVolume [fPrice iSlippage] - send an order to open;
                    Without the fPrice and iSlippage it will be a market order.
  ord stoploss
  ord trail
  ord exposure      - total exposure of all orders, worst case scenario

"""

lRABBIT_GET_THUNKS = ['vhost_names', 'channels',
                      'connections', 'queues']
sRABBIT__doc__ = """
If we have pyrabbit installed, and iff the rabbitmq_management plugin
has been installed in your server, we can introspect some useful
information if the HTTP interface is enabled. Commands include:
    get %s

The RabbitMQ host and login information is set in the `[RabbitMQ]`
section of the `OTCmd2.ini` file; see the `-c/--config` command-line options.
""" % ("|".join(lRABBIT_GET_THUNKS),)

import sys
import os
import json
import traceback
import threading
import time
import unittest
from argparse import ArgumentParser

from configobj import ConfigObj
from pika import exceptions

try:
    import OpenTrader
except ImportError:
    # support running from source
    sDir = os.path.dirname(os.path.dirname(__file__))
    if sDir not in sys.path:
        sys.path.insert(0, sDir)
    del sDir
import OpenTrader
from OpenTrader.cmd2plus import Cmd, options, make_option, Cmd2TestCase

pybacktest = None
sBAC__doc__ = ""
try:
    import OpenTrader.OTBackTest as pybacktest
    from OpenTrader.BacktestCmd import sBAC__doc__
except ImportError, e:
    sys.stdout.write("pybacktest not installed: " +str(e) +"\n" )
try:
    import pyrabbit
except ImportError:
    # sys.stdout.write("pyrabbit not installed: pip install pyrabbit\n")
    pyrabbit = None

class MqlError(Exception):
    pass

class Mt4Timeout(RuntimeError):
    pass

# FixMe:
# The messaging to and from OTMql4Py is still being done with a
# very simple format:
#       sMsgType|sChartId|sIgnored|sMark|sPayload
# where sMsgType is one of: cmd eval (outgoing), timer tick retval (incoming);
#       sChartId is the Mt4 chart sChartId the message is to or from;
#       sMark is a simple floating point timestamp, with milliseconds;
# and   sPayload is command|arg1|arg2... (outgoing) or type|value (incoming),
#       where type is one of: bool int double string json.
# This breaks if the sPayload args or value contain a | -
# we will probably replace this with json or pickled serialization, or kombu.
def sFormatMessage(sMsgType, sMark, sChartId, *lArgs):
    """
    Just a very simple message format for now:
    We are moving over to JSON so *lArgs will be replaced by sJson,
    a single JSON list of [command, arg1, arg2,...]
    """

    # iIgnore is reserved for being a hash on the payload
    iIgnore = 0
    # We are moving over to JSON - for now a command is separated by |
    sInfo = '|'.join(lArgs)
    sMsg = "%s|%s|%d|%s|%s" % (sMsgType, sChartId, iIgnore, sMark, sInfo,)
    return sMsg

def lUnFormatMessage(sBody):
    lArgs = sBody.split('|')
    sCmd = lArgs[0]
    sChart = lArgs[1]
    sIgnore = lArgs[2]
    sMark = lArgs[3]
    return lArgs

# should do something better if there are multiple clients
def sMakeMark():
    return "%15.5f" % time.time()

class CmdLineApp(Cmd):
    multilineCommands = []
    testfiles = ['exampleSession.txt']

    oChart = None
    oListenerThread = None
    oRabbit = None
    prompt = 'OTPy> '

    def __init__(self, oConfig, oOptions, lArgs):
        Cmd.__init__(self)
        self.oConfig = oConfig
        self.oOptions = oOptions
        self.lArgs = lArgs
        self.lTopics = ['#']
        self.sDefaultChart = ""
        # FixMe: refactor for multiple charts
        self.dCharts = {}
        # Keep a copy of what goes out;
        # I'm not sure how these will be used yet.
        self.dLastCmd = {}
        self.dLastEval = {}
        self.dLastJson = {}
        self.oBt = None
        self._G = None

        # we may need to add to import PikaChart
        if self.oOptions.sMt4Dir:
            sMt4Dir = os.path.expanduser(os.path.expandvars(self.oOptions.sMt4Dir))
            if not os.path.isdir(sMt4Dir):
                self.vWarn("sMt4Dir not found: " + sMt4Dir)
            else:
                sMt4Dir = os.path.join(sMt4Dir, 'MQL4', 'Python')
                if not os.path.isdir(os.path.join(sMt4Dir, 'OTMql427')):
                    self.vWarn("sMt4Dir/MQL4/Python/OTMql427 not found: " + sMt4Dir)
                elif sMt4Dir not in sys.path:
                    sys.path.insert(0, sMt4Dir)

    def G(self, gVal=None):
        if gVal is not None:
            self._G = gVal
        return self._G

    def gWaitForMessage(self, sMsgType, sMark, sChartId, *lArgs):
        """
        Raises a Mt4Timeout error if there is no answer in
        oOptions['OTCmd2']['iRetvalTimeout'] seconds.

        Raising an error lets us return None as a return value.
        The protocol talking to Mt4 has the void return type,
        which gRetvalToPython in PikaListenerThread.py returns as None.
        """
        sMsg = sFormatMessage(sMsgType, sMark, sChartId, *lArgs)
        self.vInfo("Publishing: " +sMsg)
        self.eSendOnSpeaker(sChartId, sMsgType, sMsg)
        self.dLastCmd[sChartId] = sMsg
        i = 0
        iTimeout = self.oConfig['OTCmd2']['iRetvalTimeout']
        while i < int(iTimeout):
            # do I need a thread lock?
            if sMark in self.oListenerThread.dRetvals.keys():
                gRetval = self.oListenerThread.dRetvals[sMark]
                del self.oListenerThread.dRetvals[sMark]
                return self.G(gRetval)
            i += 5
            self.vDebug("Waiting: " +repr(i))
            time.sleep(5.0)
        self._G = None
        raise Mt4Timeout("No retval returned in " +str(iTimeout) +" seconds")

    def eSendOnSpeaker(self, sChartId, sMsgType, sMsg):
        from OTMql427 import PikaListener
        if self.oListenerThread is None:
            self.vWarn("PikaListenerThread not started; you wont see the retval")
        if not self.oChart:
            # FixMe: refactor for multiple charts
            self.oChart = PikaListener.PikaMixin(sChartId, **self.oConfig['RabbitMQ'])
        # if sMsgType == 'cmd': warn if not Mt4 connected?
        return(self.oChart.eSendOnSpeaker(sMsgType, sMsg))

    ## charts
    @options([],
             arg_desc="command",
             usage=sCHART__doc__,
    )
    def do_chart(self, oArgs, oOpts=None):
        __doc__ = sCHART__doc__
        if not oArgs:
            self.poutput("Chart operations are required\n" + __doc__)
            return
        lArgs = oArgs.split()
        if lArgs[0] == 'get':
            self.poutput(self.G(self.sDefaultChart))
            return

        if lArgs[0] == 'set':
            if len(lArgs) > 1:
                self.sDefaultChart = self.G(lArgs[1])
            elif self.oListenerThread.lCharts:
                self.sDefaultChart = self.G(self.oListenerThread.lCharts[-1])
            else:
                self.vWarn("No default charts available; try 'sub run'")
            return

        if lArgs[0] == 'list':
            if self.oListenerThread is None:
                self.poutput(repr(self.G([])))
            else:
                self.poutput(repr(self.G(self.oListenerThread.lCharts)))
            return
        self.vError("Unrecognized chart command: " + str(oArgs) +'\n' +__doc__)

    ## subscribe
    @options([make_option("-c", "--chart",
                            dest="sChartId",
                            help="the target chart to subscribe to"),
    ],
               arg_desc="command",
               usage=sSUB__doc__,
    )
    def do_sub(self, oArgs, oOpts=None):
        __doc__ = sSUB__doc__
        lArgs = oArgs.split()
        try:
            # PikaListenerThread needs PikaMixin
            from OpenTrader import PikaListenerThread
        except ImportError:
            self.vError("Cant import PikaChart: add the MQL4/Python directory to PYTHONPATH")
            raise
        except Exception, e:
            self.vError(traceback.format_exc(10))
            raise

        if oOpts and oOpts.sChartId:
            sChartId = oOpts.sChartId
        else:
            sChartId = self.sDefaultChart

        if lArgs[0] == 'topics':
            # what if self.oListenerThread is not None:
            assert len(lArgs) > 1, "ERROR: sub topics TOPIC1..."
            self.lTopics = lArgs[1:]
            self.vInfo("Set topics to: " + repr(self.G(self.lTopics)))
            return

        if lArgs[0] == 'clear':
            # what if self.oListenerThread is not None:
            # do we dynamically change the subsciption or terminate the thread?
            self.lTopics = []
            return

        if lArgs[0] == 'topics':
            if self.oListenerThread:
                self.poutput("oListenerThread.lTopics: " + repr(self.G(self.oListenerThread.lTopics)))
            else:
                self.poutput("Default lTopics: " + repr(self.G(self.lTopics)))
            return

        if lArgs[0] == 'run':
            if self.oListenerThread is not None:
                self.vWarn("PikaListenerThread already listening to: " + repr(self.oListenerThread.lTopics))
                return
            try:
                if len(lArgs) > 1:
                    self.lTopics = lArgs[1:]
                self.vInfo("Starting PikaListenerThread listening to: " + repr(self.lTopics))
                self.oListenerThread = PikaListenerThread.PikaListenerThread(sChartId, self.lTopics,
                                                          **self.oConfig['RabbitMQ'])
                self.oListenerThread.start()
            except Exception, e:
                self.vError(traceback.format_exc(10))
                raise
            return

        if lArgs[0] == 'thread':
            _lCmds = ['info', 'stop', 'enumerate']
            assert len(lArgs) > 1, "ERROR: sub thread " +str(lCmds)
            assert lArgs[1] in _lCmds, "ERROR: " +lArgs[0] +" " +str(_lCmds)
            sSubCmd = lArgs[1]

            oT = self.oListenerThread
            if sSubCmd == 'enumerate':
                self.vInfo("Threads %r" % (threading.enumerate(),))
                return
            if sSubCmd == 'info':
                if not oT:
                    self.vInfo("Listener Thread not started")
                else:
                    # len(lArgs) > 2
                    lNames = [x.name for x in threading.enumerate()]
                    if oT.name not in lNames:
                        self.vWarn("Listener Thread DIED - you must \"sub run\": " + repr(lNames))
                        self.oListenerThread = None
                    else:
                        self.vInfo("Listener Thread %r" % (oT.name,))
                return
            if sSubCmd == 'stop':
                if not self.oListenerThread:
                    self.vWarn("PikaListenerThread not already started")
                    return
                self.pfeedback("oListenerThread.stop()")
                self.oListenerThread.stop()
                self.oListenerThread.join()
                self.oListenerThread = None
                return
            self.vError("Unrecognized subscribe thread command: " + str(lArgs) +'\n' +__doc__)
            return

        if lArgs[0] == 'hide':
            if not self.oListenerThread:
                self.vWarn("PikaListenerThread not already started")
                return
            if len(lArgs) == 1:
                self.oListenerThread.vHide()
            else:
                for sElt in lArgs[1:]:
                    self.oListenerThread.vHide(sElt)
            return

        if lArgs[0] == 'show':
            if not self.oListenerThread:
                self.vWarn("PikaListenerThread not already started")
                return
            if len(lArgs) == 1:
                self.oListenerThread.vShow()
            else:
                for sElt in lArgs[1:]:
                    self.oListenerThread.vShow(sElt)
            return

        if lArgs[0] == 'pprint':
            if not self.oListenerThread:
                self.vWarn("PikaListenerThread not already started")
                return
            if len(lArgs) == 1:
                self.oListenerThread.vPprint('get')
            else:
                self.oListenerThread.vPprint('set', bool(lArgs[1]))
            return

        self.vError("Unrecognized subscribe command: " + str(oArgs) +'\n' +__doc__)

    do_subscribe = do_sub

    ## publish
    @options([make_option("-c", "--chart",
                            dest="sChartId",
                            help="the target chart to publish to (or: ANY ALL NONE)"),
    ],
               arg_desc="command",
               usage=sPUB__doc__,
    )
    def do_pub(self, oArgs, oOpts=None):
        __doc__ = sPUB__doc__
        if not oArgs:
            self.poutput("Commands to publish (and arguments) are required\n" + __doc__)
            return
        if oOpts and oOpts.sChartId:
            sChartId = oOpts.sChartId
        else:
            sChartId = self.sDefaultChart
        if self.oListenerThread is None:
            self.vWarn("PikaListenerThread not started; do 'sub run retval.#'")
        # sMark is a simple timestamp: unix time with msec.
        sMark = sMakeMark()

        lArgs = oArgs.split()
        if lArgs[0] == 'wait' or lArgs[0] == 'sync':
            sMsgType = 'cmd' # Mt4 command
            assert len(lArgs) > 1, "ERROR: pub cmd COMMAND ARG1..."
            # Raises a Mt4Timeout error if there is no answer in 60 seconds
            gRetval = self.gWaitForMessage(sMsgType, sMark, sChartId, *lArgs[1:])

            self.vInfo("Returned: " +repr(self.G(gRetval)))
            return

        if lArgs[0] == 'cmd' or lArgs[0] == 'async':
            sMsgType = 'cmd' # Mt4 command
            assert len(lArgs) > 1, "ERROR: pub cmd COMMAND ARG1..."
            gRetval = self.gWaitForMessage(sMsgType, sMark, sChartId, *lArgs[1:])
            self.vInfo("Returned: " +repr(self.G(gRetval)))
            return

        if lArgs[0] == 'eval':
            sMsgType = 'eval'
            assert len(lArgs) > 1, "ERROR: pub eval COMMAND ARG1..."
            sInfo = str(lArgs[1]) # FixMe: how do we distinguish variable or thunk?
            if len(lArgs) > 2:
                sInfo += '(' +str(','.join(lArgs[2:])) +')'
            gRetval = self.gWaitForMessage(sMsgType, sMark, sChartId, sInfo)
            self.vInfo("Returned: " +repr(self.G(gRetval)))
            return

        if lArgs[0] == 'json':
            sMsgType = 'json'
            assert len(lArgs) > 1, "ERROR: pub eval COMMAND ARG1..."
            # FixMe: broken but unused
            sInfo = json.dumps(str(' '.join(lArgs[1:])))
            gRetval = self.gWaitForMessage(sMsgType, sMark, sChartId, sInfo)
            self.vInfo("Returned: " +repr(self.G(gRetval)))
            return

        self.vError("Unrecognized publish command: " + str(oArgs) +'\n' +__doc__)

    do_publish = do_pub

    ## order
    @options([make_option("-c", "--chart",
                            dest="sChartId",
                            help="the target chart to order with (or: ANY ALL NONE)"),
    ],
               arg_desc="command",
               usage=sORD__doc__,
    )
    def do_ord(self, oArgs, oOpts=None):
        __doc__ = sORD__doc__
        if not oArgs:
            self.poutput("Commands to order (and arguments) are required\n" + __doc__)
            return
        if self.oListenerThread is None:
            self.vError("PikaListenerThread not started; use 'sub run ...'")
            return

        if oOpts and oOpts.sChartId:
            sChartId = oOpts.sChartId
        else:
            sChartId = self.sDefaultChart
        # sMark is a simple timestamp: unix time with msec.
        sMark = sMakeMark()

        lArgs = oArgs.split()
        if lArgs[0] == 'list' or lArgs[0] == 'tickets':
            sMsgType = 'cmd' # Mt4 command
            # FixMe: trailing |
            sInfo='jOTOrdersTickets'
            self.gWaitForMessage(sMsgType, sMark, sChartId, sInfo)
            return

        if lArgs[0] == 'trades':
            sMsgType = 'cmd' # Mt4 command
            # FixMe: trailing |
            sInfo='jOTOrdersTrades'
            self.gWaitForMessage(sMsgType, sMark, sChartId, sInfo)
            return

        if lArgs[0] == 'history':
            sMsgType = 'cmd' # Mt4 command
            # FixMe: trailing |
            sInfo='jOTOrdersHistory'
            self.gWaitForMessage(sMsgType, sMark, sChartId, sInfo)
            return

        if lArgs[0] == 'info':
            sMsgType = 'cmd' # Mt4 command
            sCmd='jOTOrderInformationByTicket'
            assert len(lArgs) > 1, "ERROR: orders info iTicket"
            sInfo = str(lArgs[1])
            self.gWaitForMessage(sMsgType, sMark, sChartId, sCmd, sInfo)
            return

        if lArgs[0] == 'exposure':
            sMsgType = 'cmd' # Mt4 command
            sCmd='fOTExposedEcuInMarket'
            sInfo = str(0)
            self.gWaitForMessage(sMsgType, sMark, sChartId, sCmd, sInfo)
            return

        if lArgs[0] == 'close':
            sMsgType = 'cmd' # Mt4 command
            assert len(lArgs) >= 2, "ERROR: order close iTicket [fPrice iSlippage}"
            sTicket = lArgs[1]
            if len(lArgs) >= 3:
                sPrice = lArgs[2]
                sSlippage = lArgs[3]
                sCmd='iOTOrderCloseFull'
                self.gWaitForMessage(sMsgType, sMark, sChartId, sCmd, sTicket, sPrice, sSlippage)
            else:
                sCmd='iOTOrderCloseMarket'
                self.gWaitForMessage(sMsgType, sMark, sChartId, sCmd, sTicket)

            return

        if lArgs[0] == 'buy' or lArgs[0] == 'sell':
            sMsgType = 'cmd' # Mt4 command
            if lArgs[0] == 'buy':
                iCmd = 0
            else:
                iCmd = 1 # Sell 1
            assert len(lArgs) >= 3, "ERROR: order buy|sell sSymbol fVolume [fPrice iSlippage]"
            # double stoploss, double takeprofit,
            # string comment="", int magic=0
            sArg1 = str(iCmd)
            sSymbol = lArgs[1]
            sVolume = lArgs[2]
            if len(lArgs) >= 5:
                sPrice = lArgs[3]
                sSlippage = lArgs[4]
                sCmd='iOTOrderSend'
                self.gWaitForMessage(sMsgType, sMark, sChartId, sCmd, sSymbol, sArg1, sVolume, sPrice, sSlippage)
            else:
                sCmd='iOTOrderSendMarket'
                self.gWaitForMessage(sMsgType, sMark, sChartId, sCmd, sSymbol, sArg1, sVolume)
            return

        # (int iTicket, double fPrice, int iSlippage, color cColor=CLR_NONE)
        self.vError("Unrecognized order command: " + str(oArgs) +'\n' +__doc__)

    do_order = do_ord

    # backtest
    @options([make_option("-C", "--chef",
                          dest="sChef",
                          # no default here - we want it to come from the ini
                          default="",
                          help="the backtest package (one of: PybacktestChef)"),
              make_option("-R", "--recipe",
                          dest="sRecipe",
                          # no default here - we want it to come from the ini
                          default="",
                          help="recipe to backtest (one of SMARecipe")

              ],
             arg_desc="command",
             usage=sBAC__doc__
             )
    def do_back(self, oArgs, oOpts=None):
        __doc__ = sBAC__doc__
        if not pybacktest:
            self.poutput("Install pybacktest from git://github.com/ematvey/pybacktest/")
            return
        try:
            from OpenTrader.BacktestCmd import vDoBacktestCmd
        except ImportError, e:
            self.vError("backtest unfinished at the moment: " +str(e))
            return

        if not oArgs:
            self.poutput("Commands to backtest (and arguments) are required\n" + __doc__)
            return
        try:
            if oOpts.sRecipe:
                self.sRecipe = oOpts.sRecipe
            elif not hasattr(self, 'sRecipe') or not self.sRecipe:
                self.sRecipe = self.oConfig['backtest']['sRecipe']
            if oOpts.sChef:
                self.sChef = oOpts.sChef
            elif not hasattr(self, 'sChef') or not self.sChef:
                self.sChef = self.oConfig['backtest']['sChef']
            vDoBacktestCmd(self, oArgs, oOpts)
        except KeyboardInterrupt:
            pass
        except Exception, e:
            # This is still in the process of getting wired up and tested
            print(traceback.format_exc(10))

    do_bac = do_back
    do_backtest = do_back

    ## rabbit
    @options([make_option("-a", "--address",
                            dest="sHttpAddress",
                            default="127.0.0.1",
                            help="the TCP address of the HTTP rabbitmq_management  (default 127.0.0.1)"),
                make_option('-p', '--port', type="int",
                            dest="iHttpPort", default=15672,
                            help="the TCP port of the HTTP rabbitmq_management plugin (default 15672)"),],
               arg_desc="command",
               usage=sRABBIT__doc__
    )
    def do_rabbit(self, oArgs, oOpts=None):
        __doc__ = sRABBIT__doc__
        if not pyrabbit:
            self.poutput("Install pyrabbit from http://pypi.python.org/pypi/pyrabbit")
            return
        if not oArgs:
            self.poutput("Command required: get\n" + __doc__)
            return

        if self.oRabbit is None:
            sTo = oOpts.sHttpAddress +':' +str(oOpts.iHttpPort)
            sUser = self.oConfig['RabbitMQ']['sUsername']
            sPass = self.oConfig['RabbitMQ']['sPassword']
            self.oRabbit = pyrabbit.api.Client(sTo, sUser, sPass)
            vNullifyLocalhostProxy(oOpts.sHttpAddress)

        lArgs = oArgs.split()
        if lArgs[0] == 'get':
            assert len(lArgs) > 1, "ERROR: one of: get " +",".join(lRABBIT_GET_THUNKS)
            oFun = getattr(self.oRabbit, lArgs[0] +'_' +lArgs[1])
            if lArgs[1] == 'queues':
                lRetval = oFun()
                # do we need a sub-command here?
                lRetval = [x['name'] for x in lRetval]
                self.poutput(repr(self.G(lRetval)))
            elif lArgs[1] in lRABBIT_GET_THUNKS:
                lRetval = oFun()
                self.poutput(repr(self.G(lRetval)))
            else:
                self.vError("Choose one of: get " +",".join(lRABBIT_GET_THUNKS))
            return
        self.vError("Unrecognized rabbit command: " + str(oArgs) +'\n' +__doc__)

    def postloop(self):
        self.vDebug("atexit")
        if self.oListenerThread is not None:
            # for sub
            self.vInfo("oListenerThread.bCloseConnectionSockets")
            self.oListenerThread.bCloseConnectionSockets()
            self.oListenerThread = None
        if self.oChart is not None:
            # for pub
            self.vInfo("oChart.bCloseConnectionSockets")
            # FixMe: refactor for multiple charts
            self.oChart.bCloseConnectionSockets()
            self.oChart = None

    def vError(self, sMsg):
        self.poutput("ERROR: " +sMsg)

    def vWarn(self, sMsg):
        self.poutput("WARN: " +sMsg)

    def vInfo(self, sMsg):
        self.pfeedback("INFO: " +sMsg)

    def vDebug(self, sMsg):
        self.pfeedback("DEBUG: " +sMsg)

def vNullifyLocalhostProxy(sHost):
    """
    We probably dont want to go via a proxy to localhost.
    """
    if sHost not in ['localhost', "127.0.0.1"]: return
    for sElt in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY',]:
        if sElt in os.environ: del os.environ[sElt]

class TestMyAppCase(Cmd2TestCase):
    CmdApp = CmdLineApp
    transcriptFileName = 'exampleSession.txt'

def oParseOptions(sUsage):
    """
    Look at the bottom of PikaListener.py and PikaChart.py for iMain
    functions that use the oParseOptions that is returned here.
    This function returns an ArgumentParser instance, so that you
    can override it before you call it to parse_args.
    """
    oArgParser = ArgumentParser(description=sUsage)
    oArgParser.add_argument("-v", "--verbose", action="store",
                            dest="iVerbose", type=int, default=4,
                            help="the verbosity, 0 for silent 4 max (default 4)")
    oArgParser.add_argument('-t', '--test',
                            dest='bUnittests', action='store_true', default=False,
                            help='Run unit test suite')
    oArgParser.add_argument('-c', '--config',
                            dest='sConfigFile', default="OTCmd2.ini",
                            help='Config file for OTCmd2 options')
    oArgParser.add_argument("-P", "--mt4dir", action="store",
                            dest="sMt4Dir", default="",
                            help="directory for the installed Metatrader")
    #? sOmlettesDir
    #? matplotlib_use?
    oArgParser.add_argument('lArgs', action="store",
                            nargs="*",
                            help="command line arguments (optional)")
    return(oArgParser)

def oParseConfig(sConfigFile):
    if not os.path.isabs(sConfigFile):
        sConfigFile = os.path.join(os.path.dirname(__file__), sConfigFile)
        assert os.path.isfile(sConfigFile), "Missing configuration file: " + sConfigFile
    else:
        sConfigFile = os.path.expanduser(os.path.expandvars(sConfigFile))
        assert os.path.isfile(sConfigFile), "Configuration file not found: " + sConfigFile
    return ConfigObj(sConfigFile, unrepr=True)

def iMain():
#    from PikaArguments import oParseOptions

    sUsage = __doc__.strip()
    oArgParser = oParseOptions(sUsage)
    oOptions = oArgParser.parse_args()
    lArgs = oOptions.lArgs

    if oOptions.bUnittests:
        sys.argv = [sys.argv[0]]  # the --test argument upsets unittest.main()
        unittest.main()
        return 0

    # FixMe: merge the arguments into the [OTCmd2] section of the configFile
    sConfigFile = oOptions.sConfigFile

    oApp = None
    try:
        oConfig = oParseConfig(sConfigFile)
        oApp = CmdLineApp(oConfig, oOptions, lArgs)
        if lArgs:
            initial_command = ' '.join(lArgs)
            oApp.onecmd_plus_hooks(initial_command + '\n')
            return 0
        else:
            oApp._cmdloop()
            return 0
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print(traceback.format_exc(10))

    if oApp and hasattr(oApp, 'oChart') and oApp.oChart:
        # failsafe
        try:
            sys.stdout.write("DEBUG: Waiting for message queues to flush...\n")
            oApp.oChart.bCloseConnectionSockets()
            time.sleep(1.0)
        except (KeyboardInterrupt, exceptions.ConnectionClosed):
            # impatient
            pass

if __name__ == '__main__':
    iMain()

# grep '//0' ../../Libraries/OTMql4/OTLibMt4ProcessCmd.mq4 |sed -e 's/.*== "/pub /' -e 's/".*//' > OTCmd2-0.test
