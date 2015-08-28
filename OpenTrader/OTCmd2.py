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

sCSV__doc__ = """
Download, resample and convert CSV files into pandas:
{{{
csv url PAIRSYMBOL       - show a URL where you can download  1 minute Mt HST data
csv resample SRAW1MINFILE, SRESAMPLEDCSV, STIMEFRAME - Resample 1 minute CSV data,
                                                       to a new timeframe
                                                       and save it as CSV file
}}}
"""

sCHART__doc__ = """
Set and query the chart in Metatrader that the messages are sent to:
{{{
  list   - all the charts the listener has heard of,
           iff you have already started a listener with "sub run"
  get    - get the default chart to be published or subscribed to; defaults to:
           the last chart the listener has heard of.
  set ID - set the default chart ID to be published or subscribed to.
  set    - set the default chart to be the last chart the listener has heard of,
           iff you have already started a listener with "sub run"

The chart ID will look something like: oChart_EURGBP_240_93ACD6A2_1
}}}
"""

sSUB__doc__ = """
Subscribe to messages from RabbitMQ on a given topic:
{{{
  sub get               - get the current target for subscribe; defaults to:
                        the first value of default['lOnlineTargets'] in OTCmd2.ini
  sub set TARGET        - set the target for subscribe, must be one of:
                        the values of default['lOnlineTargets'] in OTCmd2.ini
  sub config            - configure the current target for subscribe: [KEY [VAL]]
  sub run TOPIC1 ...    - start a thread to listen for messages,
                          TOPIC is one or more Rabbit topic patterns.
  sub topics            - shows topics subscribed to.
  sub hide TOPIC        - stop seeing TOPIC messages (e.g. tick - not a pattern)
  sub show              - list the message topics that are being hidden
  sub show TOPIC        - start seeing TOPIC messages (e.g. tick - not a pattern)
  sub pprint ?0|1       - seeing TOPIC messages with pretty-printing,
                          with 0 - off, 1 - on, no argument - current value
  sub thread info       - info on the thread listening for messages.
  sub thread stop       - stop a thread listening for messages.
  sub thread enumerate  - enumerate all threads
}}}

Common RabbitMQ topic patterns are:
* {{{#}}} for all messages,
* {{{tick.#}}} for ticks,
* {{{timer.#}}} for timer events,
* {{{retval.#}}} for return values.

You can choose as specific chart with syntax like:
{{{
    tick.oChart.EURGBP.240.93ACD6A2.#
}}}
The RabbitMQ host and login information is set in the {{{[RabbitMQ]}}}
section of the {{{OTCmd2.ini}}} file; see the {{{-c/--config}}} command-line options.
"""

sPUB__doc__ = """
Publish a message via RabbitMQ to a given chart on a OTMql4Py enabled terminal:
{{{
  pub get                   - get the current target for publish; defaults to:
                            the first value of default['lOnlineTargets'] in OTCmd2.ini
  pub set TARGET            - set the target for publish,
  pub config                - configure the current target for publish: [KEY [VAL]]
  pub wait COMMAND ARG1 ... - publish a Mql command to Mt4 and wait for the result,
      the command should be a single string, with a space seperating arguments.
  pub eval COMMAND ARG1 ... - publish a Python command to the OTMql4Py,
      the command should be a single string, with a space seperating arguments.
}}}
You wont see the return value unless you have already done a:
{{{
  sub run retval.#
}}}
The RabbitMQ host and login information is set in the {{{[RabbitMQ]}}}
section of the {{{OTCmd2.ini}}} file; see the {{{-c/--config}}} command-line options.
"""
#   pub cmd  COMMAND ARG1 ... - publish a Mql command to Mt4,
#      the command should be a single string, with a space seperating arguments.

# should these all be of chart ANY
sORD__doc__ = """
Manage orders in an OTMql4AQMp enabled Metatrader:
{{{
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
}}}
"""

lRABBIT_GET_THUNKS = ['vhost_names', 'channels',
                      'connections', 'queues']
sRABBIT__doc__ = """
Introspect some useful information from the RabbitMQ server:
if we have pyrabbit installed, and iff the rabbitmq_management plugin has been
installed in your server, we can query the  HTTP interface if it is enabled.
Commands include:
{{{
  rabbit get %s
}}}
The RabbitMQ host and login information is set in the {{{[RabbitMQ]}}}
section of the {{{OTCmd2.ini}}} file; see the {{{-c/--config}}} command-line options.
""" % ("|".join(lRABBIT_GET_THUNKS),)

import sys
import os
import json
from pprint import pprint, pformat
import traceback
import threading
import time
import unittest

if hasattr(sys, 'frozen') and sys.frozen:
    __file__ = sys.executable
else:
    try:
        import OpenTrader
    except ImportError:
        # support running from source
        sDIR = os.path.dirname(os.path.dirname(__file__))
        if sDIR not in sys.path:
            sys.path.insert(0, sDIR)
        del sDIR
from OpenTrader.cmd2plus import Cmd, options, make_option, Cmd2TestCase

try:
    import tabview
except ImportError:
    # depends on curses
    tabview = None

pybacktest = None
sBAC__doc__ = ""
try:
    import OpenTrader.OTBackTest as pybacktest
    from OpenTrader.BacktestCmd import sBAC__doc__
except ImportError as e:
    sys.stdout.write("pybacktest not installed: " +str(e) +"\n")

class MqlError(Exception):
    pass

class Mt4Timeout(RuntimeError):
    pass

class CmdLineApp(Cmd):
    multilineCommands = []
    testfiles = ['exampleSession.txt']

    oMixin = None
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

        # we will need to add to import PikaChart or ZmqChart
        sMt4Dir = oConfig['default']['sMt4Dir']
        if sMt4Dir:
            sMt4Dir = os.path.expanduser(os.path.expandvars(sMt4Dir))
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

    def vConfigOp(self, lArgs, dConfig):
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
            self.vOutput(repr(setf.G(gRetval)))

    def eSendOnSpeaker(self, sChartId, sMsgType, sMsg):
        if sMsgType == 'cmd' and self.oListenerThread is None:
            self.vWarn("ListenerThread not started; you will not see the retval")
        if self.oCurrentPubTarget is None:
            sErr = "PubTarget not set; use \"pub set\""
            self.vError(sErr)
            return sErr

        # self.oCurrentPubTarget is a ConfigObj section: disctionary-like
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
        from OTMql427.SimpleFormat import sFormatMessage, sMakeMark
        sMsg = sFormatMessage(sMsgType, sChartId, sMark, *lArgs)
        e = self.eSendOnSpeaker(sChartId, sMsgType, sMsg)
        self.dLastCmd[sChartId] = sMsg
        return e

    def gWaitForMessage(self, sMsgType, sChartId, sMark, *lArgs):
        """
        Raises a Mt4Timeout error if there is no answer in
        oOptions['default']['iRetvalTimeout'] seconds.

        Raising an error lets us return None as a return value.
        The protocol talking to Mt4 has the void return type,
        which gRetvalToPython returns as None.
        """
        from OTMql427.SimpleFormat import gRetvalToPython, lUnFormatMessage
        self.eSendMessage(sMsgType, sChartId, sMark, *lArgs)
        i = 0
        iTimeout = self.oConfig['default']['iRetvalTimeout']
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
    @options([],
             arg_desc="command",
             usage=sCSV__doc__,
             )
    def do_csv(self, oArgs, oOpts=None):
        __doc__ = sCSV__doc__

        _lCmds = ['url', 'resample'] # read plot?
        lArgs = oArgs.split()
        sDo = lArgs[0]
        assert len(lArgs) > 1 and sDo in _lCmds, \
               "ERROR: " +sDo +" choose one of: " +str(_lCmds)

        # o oConfig sHistoryDir:

        # show a URL where you can download  1 minute Mt HST data
        if sDo == 'url':
            # see http://www.fxdd.com/us/en/forex-resources/forex-trading-tools/metatrader-1-minute-data/
            sSymbol =  lArgs[1].upper()
            self.vOutput("http://tools.fxdd.com/tools/M1Data/%s.zip" % (sSymbol,))
            return

        # csv resample SRAW1MINFILE, SRESAMPLEDCSV, STIMEFRAME -
        # Resample 1 minute CSV data, to a new timeframe
        if sDo == 'resample':
            # Resample 1 minute data to new period, using pandas resample, how='ohlc'
            from PandasMt4 import vResample1Min
            assert len(lArgs) > 3, "ERROR: " +sDo +" SRAW1MINFILE, SRESAMPLEDCSV, STIMEFRAME"
            sRaw1MinFile = lArgs[1]
            assert os.path.exists(sRaw1MinFile)
            sResampledCsv = lArgs[2]
            if os.path.isabs(sResampledCsv):
                assert os.path.isdir(os.path.dirname(sResampledCsv)), "ERROR: directory not found"
            sTimeFrame = lArgs[3]
            iTimeFrame = int(sTimeFrame)
            oFd = sys.stdout
            vResample1Min(sRaw1MinFile, sResampledCsv, sTimeFrame, oFd)
            return

        self.vError("Unrecognized csv command: " + str(oArgs) +'\n' +__doc__)
        return

    ## charts
    @options([],
             arg_desc="command",
             usage=sCHART__doc__,
             )
    def do_chart(self, oArgs, oOpts=None):
        __doc__ = sCHART__doc__

        _lCmds = ['get', 'set', 'list']
        if not oArgs:
            self.vOutput("Chart operations are required\n" + __doc__)
            return
        lArgs = oArgs.split()
        sDo = lArgs[0]

        # get the default chart to be published or subscribed to.
        # all the charts the listener has heard of,
        if sDo == 'list':
            if self.oListenerThread is None:
                l = []
            else:
                l = self.oListenerThread.lCharts
            self.vOutput(repr(self.G(l)))
            return

        if sDo == 'get' or (sDo == 'set' and len(lArgs) == 1):
            if self.sDefaultChart:
                self.vOutput("The default chart is: " +self.sDefaultChart)
            elif self.oListenerThread and self.oListenerThread.lCharts:
                self.sDefaultChart = self.G(self.oListenerThread.lCharts[-1])
                self.vOutput("The default chart is: " +self.sDefaultChart)
            else:
                self.vWarn("No default charts available; do 'sub run' first")
                return
            self.G(self.sDefaultChart)
            return

        assert len(lArgs) > 1, \
            "ERROR: Commands to chart (and arguments) are required"

        # set the default chart ID to be published or subscribed to.
        if sDo == 'set':
            self.sDefaultChart = self.G(lArgs[1])
            self.vOutput("The default chart is set to: " +lArgs[1])
            return

        self.vError("Unrecognized chart command: " + str(oArgs) +'\n' +__doc__)

    ## subscribe
    @options([],
             arg_desc="command",
             usage=sSUB__doc__,
             )
    def do_subscribe(self, oArgs, oOpts=None):
        __doc__ = sSUB__doc__
        _lCmds = ['get', 'set', 'config', 'topics', 'run', 'thread'', hide', 'show', 'pprint']

        if not oArgs:
            self.vOutput("Commands to subscribe (and arguments) are required\n")
            return

        lArgs = oArgs.split()
        sDo = lArgs[0]

        # set the target for subscribe, or to see the current target
        if self.oCurrentSubTarget is None:
            assert self.oConfig['default']['lOnlineTargets'], \
                   "ERROR: empty self.oConfig['default']['lOnlineTargets']"

        if sDo == 'get' or (sDo == 'set' and len(lArgs) == 1):
            if self.oCurrentSubTarget is None:
                l = self.oConfig['default']['lOnlineTargets']
                for sElt in l:
                    assert sElt in self.oConfig.keys(), \
                           "ERROR: ini section not found: " + sCurrentSubTarget
                if len(l) > 1:
                    self.vOutput("The subscribe online targets available are: " +repr(l))
                    return
                sCurrentSubTarget = l[0]
                self.oCurrentSubTarget = self.oConfig[sCurrentSubTarget]
                self.oCurrentSubTarget.name = sCurrentSubTarget
            else:
                sCurrentSubTarget = self.oCurrentSubTarget.name
            self.vOutput("The current subscribe online target is: " +sCurrentSubTarget)
            return

        # configure the current target for subscribe: [KEY [VAL]]
        if sDo == 'config':
            # configure the current target for subscribe:  [KEY [VAL]]
            if self.oCurrentSubTarget is None:
                assert self.oConfig['default']['lOnlineTargets'], \
                       "ERROR: empty self.oConfig['default']['lOnlineTargets']"
                l = self.oConfig['default']['lOnlineTargets']
                self.vError("Use \"sub set\" to set the current target to one of: " + repr(l))
                return
            self.vConfigOp(lArgs, self.oCurrentSubTarget)
            return

        # shows topics subscribed to.
        if sDo == 'topics':
            if self.oListenerThread:
                self.vOutput("oListenerThread.lTopics: " + repr(self.G(self.oListenerThread.lTopics)))
            else:
                self.vOutput("Default lTopics: " + repr(self.G(self.lTopics)))
            return

        if sDo == 'set':
            assert len(lArgs) > 1, \
                   "ERROR: " +"Commands to subscribe (and arguments) are required"
            sTarget = lArgs[1]
            assert sTarget in self.oConfig['default']['lOnlineTargets'], \
                  "ERROR: " +sTarget +" not in " +repr(self.oConfig['default']['lOnlineTargets'])
            assert sTarget in self.oConfig.keys(), \
                   "ERROR: " +sTarget +" not in " +repr(self.oConfig.keys())
            self.oCurrentSubTarget = self.oConfig[sTarget]
            self.oCurrentSubTarget.name = sTarget
            self.vOutput("Set target to: " + repr(self.G(sTarget)))
            return

        # thread info       - info on the thread listening for messages.
        # thread stop       - stop a thread listening for messages.
        if sDo == 'thread':
            _lCmds = ['info', 'stop', 'enumerate']
            assert len(lArgs) > 1, "ERROR: sub thread " +str(_lCmds)
            assert lArgs[1] in _lCmds, "ERROR: " +sDo +" " +str(_lCmds)
            sSubCmd = lArgs[1]

            oT = self.oListenerThread
            if sSubCmd == 'enumerate':
                self.vOutput("Threads %r" % (threading.enumerate(),))
                return
            if sSubCmd == 'info':
                if not oT:
                    self.vOutput("Listener Thread not started")
                else:
                    # len(lArgs) > 2
                    lNames = [x.name for x in threading.enumerate()]
                    if oT.name not in lNames:
                        self.vWarn("Listener Thread DIED - you must \"sub run\": " + repr(lNames))
                        self.oListenerThread = None
                    else:
                        self.vOutput("Listener Thread %r" % (oT.name,))
                return
            if sSubCmd == 'stop':
                if not self.oListenerThread:
                    self.vWarn("ListenerThread not already started")
                    return
                self.pfeedback("oListenerThread.stop()")
                self.oListenerThread.stop()
                self.oListenerThread.join()
                self.oListenerThread = None
                return
            self.vError("Unrecognized subscribe thread command: " + str(lArgs) +'\n' +__doc__)
            return

        # stop seeing TOPIC messages (e.g. tick - not a pattern)
        if sDo == 'hide':
            if not self.oListenerThread:
                self.vWarn("ListenerThread not already started")
                return
            if len(lArgs) == 1:
                self.oListenerThread.vHide()
            else:
                for sElt in lArgs[1:]:
                    self.oListenerThread.vHide(sElt)
            return

        # list the message topics that are being hidden
        # start seeing TOPIC messages (e.g. tick - not a pattern)
        if sDo == 'show':
            if not self.oListenerThread:
                self.vWarn("ListenerThread not already started")
                return
            if len(lArgs) == 1:
                self.oListenerThread.vShow()
            else:
                for sElt in lArgs[1:]:
                    self.oListenerThread.vShow(sElt)
            return

        # seeing TOPIC messages with pretty-printing,
        # with 0 - off, 1 - on, no argument - current value
        if sDo == 'pprint':
            if not self.oListenerThread:
                self.vWarn("ListenerThread not already started")
                return
            if len(lArgs) == 1:
                self.oListenerThread.vPprint('get')
            else:
                self.oListenerThread.vPprint('set', bool(lArgs[1]))
            return

        if self.oCurrentSubTarget is None:
            self.vError("Use \"sub set\" to set the current target")
            return

        assert 'sOnlineRouting' in self.oCurrentSubTarget.keys(), \
               "ERROR: " +sOnlineRouting + " not in " +repr(self.oCurrentSubTarget.keys())
        assert self.oCurrentSubTarget['sOnlineRouting']
        sOnlineRouting = self.oCurrentSubTarget['sOnlineRouting']
        sChartId = self.sDefaultChart
        if sOnlineRouting == 'RabbitMQ':
            try:
                # PikaListenerThread needs PikaMixin
                import PikaListenerThread as ListenerThread
            except ImportError as e:
                self.vError("Cant import PikaListenerThread: add the MQL4/Python directory to PYTHONPATH? " +str(e))
                self.vError("sys.path is: " +repr(sys.path))
                raise
            except Exception as e:
                self.vError(traceback.format_exc(10))
                raise
            sQueueName = self.oCurrentSubTarget['sQueueName']
        elif sOnlineRouting == 'ZeroMQ':
            try:
                import ZmqListenerThread as ListenerThread
            except ImportError as e:
                self.vError("Cant import ZmqListenerThread: add the MQL4/Python directory to PYTHONPATH? " +str(e))
                raise
            except Exception as e:
                self.vError(traceback.format_exc(10))
                raise
        else:
            raise RuntimeError("sOnlineRouting value in %s section of Cmd2.ini not supported" % (
                        sOnlineRouting,))

        # start a thread to listen for messages,
        if sDo == 'run':

            if self.oListenerThread is not None:
                self.vWarn("ListenerThread already listening to: " + repr(self.oListenerThread.lTopics))
                return
            if len(lArgs) > 1:
                self.lTopics = lArgs[1:]
            else:
                self.lTopics = ['']
            if sOnlineRouting == 'RabbitMQ':
                from pika import exceptions
                try:
                    dConfig = self.oConfig['RabbitMQ']
                    assert 'sQueueName' in dConfig, \
                           "ERROR: sQueueName not in dConfig"
                    self.oListenerThread = ListenerThread.PikaListenerThread(sChartId,
                                                                             self.lTopics,
                                                                             **dConfig)
                    self.oListenerThread.start()
                except exceptions.AMQPConnectionError as e:
                    self.vError("Is the RabbitMQ server running?\n" +str(e))
                    raise
                except Exception as e:
                    self.vError(traceback.format_exc(10))
                    raise
            elif sOnlineRouting == 'ZeroMQ':
                import zmq
                try:
                    dConfig = self.oConfig['ZeroMQ']
                    self.oListenerThread = ListenerThread.ZmqListenerThread(sChartId,
                                                                             self.lTopics,
                                                                             **dConfig)
                    self.oListenerThread.start()
                except zmq.ZMQError as e:
                    # zmq4: iError = zmq.zmq_errno()
                    iError = e.errno
                    self.vWarn("run ZMQError in oListenerThread.start : %d %s" % (
                        iError, zmq.strerror(iError),))
                except Exception as e:
                    self.vError(traceback.format_exc(10))
                    raise
            return

        self.vError("Unrecognized subscribe command: " + str(oArgs) +'\n' +__doc__)

    do_sub = do_subscribe

    ## publish
    @options([make_option("-c", "--chart",
                          dest="sChartId",
                          help="the target chart to publish to (or: ANY ALL NONE)"),
              ],
             arg_desc="command",
             usage=sPUB__doc__,
             )
    def do_publish(self, oArgs, oOpts=None):
        from OTMql427.SimpleFormat import sFormatMessage, sMakeMark
        __doc__ = sPUB__doc__
        _lCmds = ['get', 'set', 'config', 'wait',] # , 'cmd' 'eval', 'json'
        if not oArgs:
            self.vOutput("Commands to publish (and arguments) are required\n" + __doc__)
            return

        lArgs = oArgs.split()
        sDo = lArgs[0]

        if self.oCurrentPubTarget is None:
            assert self.oConfig['default']['lOnlineTargets'], \
                "ERROR: empty self.oConfig['default']['lOnlineTargets']"

        # Set the target for subscribe - call without args to see the current target
        if sDo == 'get' or (sDo == 'set' and len(lArgs) == 1):
            if self.oCurrentPubTarget is None:
                l = self.oConfig['default']['lOnlineTargets']
                for sElt in l:
                    assert sElt in self.oConfig.keys(), \
                           "ERROR: ini section not found: " + sCurrentPubTarget
                if len(l) > 1:
                    self.vOutput("The publish online targets available are: " +repr(l))
                    return
                sCurrentPubTarget = l[0]
                self.oCurrentPubTarget = self.oConfig[sCurrentPubTarget]
                self.oCurrentPubTarget.name = sCurrentPubTarget
            else:
                sCurrentPubTarget = self.oCurrentPubTarget.name
            self.vOutput("The current publish online target is: " +sCurrentPubTarget)
            return

        # configure the current target for subscribe:  [KEY [VAL]]
        if sDo == 'config':
            if self.oCurrentPubTarget is None:
                assert self.oConfig['default']['lOnlineTargets'], \
                       "ERROR: empty self.oConfig['default']['lOnlineTargets']"
                l = self.oConfig['default']['lOnlineTargets']
                self.vError("Use \"pub set\" to set the current target to one of: " + repr(l))
                return
            # do I need to dict this or make an ConfigObj version?
            self.vConfigOp(lArgs, self.oCurrentPubTarget)
            return

        # everything beyond here requires an argument
        assert len(lArgs) > 1, \
            "ERROR: pub " +sDo +" COMMAND ARG1..."

        if sDo == 'set':
            sTarget = lArgs[1]
            assert sTarget in self.oConfig['default']['lOnlineTargets'], \
                   "ERROR: " +sTarget +" not in OTCmd2.ini['default']['lOnlineTargets']: " \
                   +repr(self.oConfig['default']['lOnlineTargets'])
            assert sTarget in self.oConfig.keys(), \
                   "ERROR: sTarget not in self.oConfig.keys()"
            self.oCurrentPubTarget = self.oConfig[sTarget]
            self.oCurrentPubTarget.name = sTarget
            self.vOutput("Set publish target to: " + repr(self.G(sTarget)))
            return

        # sMark is a simple timestamp: unix time with msec.
        sMark = sMakeMark()
        if oOpts and oOpts.sChartId:
            sChartId = oOpts.sChartId
        else:
            sChartId = self.sDefaultChart
        if not sChartId:
            sChartId = 'oChart_ANY_0_FFFFFFFF_1'
            self.vWarn("No default chart set; using: " +sChartId)

        if sDo == 'wait' or sDo == 'exec' or sDo == 'sync':
            sMsgType = 'exec' # Mt4 command
            # Raises a Mt4Timeout error if there is no answer in 60 seconds
            gRetval = self.gWaitForMessage(sMsgType, sChartId, sMark, *lArgs[1:])

            self.vOutput("Returned: " +repr(self.G(gRetval)))
            return

        if self.oListenerThread is None:
            self.vWarn("ListenerThread not started; do 'sub run retval.#'")

        if sDo == 'cmd' or sDo == 'async':
            # I dont think this works, at least under ZeroMQ
            # There is not handling of the null return message
            sMsgType = 'cmd' # Mt4 command
            e = self.eSendMessage(sMsgType, sChartId, sMark, *lArgs[1:])
            return

        # not ready
        if sDo == 'eval':
            sMsgType = 'eval'
            sInfo = str(lArgs[1]) # FixMe: how do we distinguish variable or thunk?
            if len(lArgs) > 2:
                sInfo += '(' +str(','.join(lArgs[2:])) +')'
            gRetval = self.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
            self.vOutput("Returned: " +repr(self.G(gRetval)))
            return

        # not ready
        if sDo == 'json':
            sMsgType = 'json'
            # FixMe: broken but unused
            sInfo = json.dumps(str(' '.join(lArgs[1:])))
            gRetval = self.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
            self.vOutput("Returned: " +repr(self.G(gRetval)))
            return

        self.vError("Unrecognized publish command: " + str(oArgs) +'\n' +__doc__)

    do_pub = do_publish

    ## order
    @options([],
             arg_desc="command",
             usage=sORD__doc__,
             )
    def do_order(self, oArgs, oOpts=None):
        from OTMql427.SimpleFormat import sFormatMessage, sMakeMark
        __doc__ = sORD__doc__
        _lCmds = ['list', 'trades', 'history', 'info', 'exposure', 'close', 'but', 'sell']
        if not oArgs:
            self.vOutput("Commands to order (and arguments) are required\n" + _lCmds)
            return

        if self.oListenerThread is None:
            self.vError("ListenerThread not started; use 'sub run retval.#'")
            return

        sChartId = self.sDefaultChart
        # sMark is a simple timestamp: unix time with msec.
        sMark = sMakeMark()

        lArgs = oArgs.split()
        sDo = lArgs[0]
        assert sDo in _lCmds, \
               "ERROR: choose one of: " +str(_lCmds)

        if sDo == 'list' or sDo == 'tickets':
            sMsgType = 'exec' # Mt4 command
            # FixMe: trailing |
            sInfo = 'jOTOrdersTickets'
            j = self.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
            # jOTOrdersTickets
            # pprint the json?
            self.vOutput(sInfo +": " +str(j))
            return

        if sDo == 'trades':
            sMsgType = 'exec' # Mt4 command
            # FixMe: trailing |
            sInfo = 'jOTOrdersTrades'
            j = self.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
            self.vOutput(sInfo +": " +str(j))
            return

        if sDo == 'history':
            sMsgType = 'exec' # Mt4 command
            # FixMe: trailing |
            sInfo = 'jOTOrdersHistory'
            j = self.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
            self.vOutput(sInfo +": " +str(j))
            return

        if sDo == 'info':
            sMsgType = 'exec' # Mt4 command
            sCmd = 'jOTOrderInformationByTicket'
            assert len(lArgs) > 1, "ERROR: orders info iTicket"
            sInfo = str(lArgs[1])
            j = self.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sInfo)
            self.vOutput(sInfo +": " +str(j))
            return

        if sDo == 'exposure':
            sMsgType = 'exec' # Mt4 command
            sCmd = 'fOTExposedEcuInMarket'
            sInfo = str(0)
            f = self.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sInfo)
            self.vOutput(sInfo +": " +str(f))
            return

        if sDo == 'close':
            sMsgType = 'exec' # Mt4 command
            assert len(lArgs) >= 2, "ERROR: order close iTicket [fPrice iSlippage}"
            sTicket = lArgs[1]
            if len(lArgs) >= 3:
                sPrice = lArgs[2]
                sSlippage = lArgs[3]
                sCmd = 'iOTOrderCloseFull'
                self.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sTicket, sPrice, sSlippage)
            else:
                sCmd = 'iOTOrderCloseMarket'
                self.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sTicket)

            return

        if sDo == 'buy' or sDo == 'sell':
            sMsgType = 'exec' # Mt4 command
            if sDo == 'buy':
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
                sCmd = 'iOTOrderSend'
                self.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sSymbol, sArg1, sVolume, sPrice, sSlippage)
            else:
                sCmd = 'iOTOrderSendMarket'
                self.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sSymbol, sArg1, sVolume)
            return

        # (int iTicket, double fPrice, int iSlippage, color cColor=CLR_NONE)
        self.vError("Unrecognized order command: " + str(oArgs) +'\n' +__doc__)

    do_ord = do_order

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
    def do_backtest(self, oArgs, oOpts=None):
        __doc__ = sBAC__doc__
        _lCmds = ['omlette', 'feed', 'recipe', 'chef', 'servings', 'plot']

        # might let it import to list recipes and chefs?
        try:
            import pybacktest
        except ImportError as e:
            self.vError("pybacktest not installed: " +str(e))
            return
        from OpenTrader.BacktestCmd import vDoBacktestCmd

        if not oArgs:
            self.vOutput("Commands to backtest (and arguments) are required\n" + __doc__)
            return
        lArgs = oArgs.split()
        sDo = lArgs[0]
        assert len(lArgs) > 1 and sDo in _lCmds, \
               "ERROR: " +sDo +" choose one of: " +str(_lCmds)

        try:
            # use ConfigObj update
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
        except Exception as e:
            # This is still in the process of getting wired up and tested
            print(traceback.format_exc(10))

    do_back = do_backtest
    do_bac = do_backtest

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
        try:
            import pyrabbit
        except ImportError:
            # sys.stdout.write("pyrabbit not installed: pip install pyrabbit\n")
            pyrabbit = None
        if not pyrabbit:
            self.vOutput("Install pyrabbit from http://pypi.python.org/pypi/pyrabbit")
            return
        if not oArgs:
            self.vOutput("Command required: get\n" + __doc__)
            return

        if self.oRabbit is None:
            sTo = oOpts.sHttpAddress +':' +str(oOpts.iHttpPort)
            sUser = self.oConfig['RabbitMQ']['sUsername']
            sPass = self.oConfig['RabbitMQ']['sPassword']
            self.oRabbit = pyrabbit.api.Client(sTo, sUser, sPass)
            vNullifyLocalhostProxy(oOpts.sHttpAddress)

        lArgs = oArgs.split()
        sDo = lArgs[0]
        if sDo == 'get':
            assert len(lArgs) > 1, "ERROR: one of: get " +",".join(lRABBIT_GET_THUNKS)
            oFun = getattr(self.oRabbit, sDo +'_' +lArgs[1])
            if lArgs[1] == 'queues':
                lRetval = oFun()
                # do we need a sub-command here?
                lRetval = [x['name'] for x in lRetval]
                self.vOutput(repr(self.G(lRetval)))
            elif lArgs[1] in lRABBIT_GET_THUNKS:
                lRetval = oFun()
                self.vOutput(repr(self.G(lRetval)))
            else:
                self.vError("Choose one of: get " +",".join(lRABBIT_GET_THUNKS))
            return
        self.vError("Unrecognized rabbit command: " + str(oArgs) +'\n' +__doc__)

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

    def vOutput(self, sMsg):
        self.poutput("OTPy: " +sMsg)

    def vError(self, sMsg):
        self.poutput("ERR!: " +sMsg)

    def vWarn(self, sMsg):
        self.poutput("WARN: " +sMsg)

    def vInfo(self, sMsg):
        self.pfeedback("INFO: " +sMsg)

    def vDebug(self, sMsg):
        self.pfeedback("DEBUG: " +sMsg)

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
    ## oArgParser.add_argument('-i', '--interactive',
    ##                         dest='bInteractive', action='store_true', default=False,
    ##                         help='Run the interactive command loop after command line args')
    oArgParser.add_argument('-t', '--test',
                            dest='bUnittests', action='store_true', default=False,
                            help='Run unit test suite')
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
                oConfig['default']['lOnlineTargets'] = [gValue]
            else:
                oConfig['default'][sKey] = gValue
            # del?
        else:
            print "WARN: unrecognized oConfig key: " +sKey
    return oConfig

def oMain(lCmdLine):
    oArgParser = oParseOptions()
    oOptions = oArgParser.parse_args(lCmdLine)
    lArgs = oOptions.lArgs

    sConfigFile = oOptions.sConfigFile
    oConfig = oParseConfig(sConfigFile)
    oConfig = oMergeConfig(oConfig, oOptions)
    oApp = CmdLineApp(oConfig, oOptions, lArgs)
    return oApp

def iMain(lCmdLine):

    if '--test' in lCmdLine:
        # legacy - unused
        sys.argv = [sys.argv[0]]  # the --test argument upsets unittest.main()
        unittest.main()
        return 0

    oApp = None
    try:
        oApp = oMain(lCmdLine)
        if oApp.oOptions.lArgs:
            oApp.onecmd_plus_hooks(' '.join(oApp.oOptions.lArgs) +'\n')
        else:
            oApp._cmdloop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(traceback.format_exc(10))
    # always reached
    if oApp:
        oApp.vAtexit()

        l = threading.enumerate()
        if len(l) > 1:
            print "WARN: Threads still running: %r" % (l,)

if __name__ == '__main__':
    iMain(sys.argv[1:])

# grep '//0' ../../Libraries/OTMql4/OTLibMt4ProcessCmd.mq4 |sed -e 's/.*== "/pub /' -e 's/".*//' > OTCmd2-0.test
