# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
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

SDOC = __doc__

import sys
import os
import threading
import traceback
from optparse import make_option

from OpenTrader.doer import Doer

LOPTIONS = []

LCOMMANDS = []

class DoSubscribe(Doer):
    __doc__ = SDOC
    # putting this as a module variable subscribe it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'subscribe')

    LCOMMANDS += ['get']
    def subscribe_get(self):
        """subscribe get
        """
        self.dhelp['get'] = __doc__
        if self.ocmd2.oCurrentSubTarget is None:
            l = self.ocmd2.oConfig['OTCmd2']['lOnlineTargets']
            for sElt in l:
                assert sElt in self.ocmd2.oConfig.keys(), \
                       "ERROR: ini section not found: " + self.ocmd2.sCurrentSubTarget
            if len(l) > 1:
                self.vOutput("The subscribe online targets available are: " +repr(l))
                return
            sCurrentSubTarget = l[0]
            self.ocmd2.oCurrentSubTarget = self.ocmd2.oConfig[sCurrentSubTarget]
            self.ocmd2.oCurrentSubTarget.name = sCurrentSubTarget
        else:
            sCurrentSubTarget = self.ocmd2.oCurrentSubTarget.name
        self.vOutput("The current subscribe online target is: " +sCurrentSubTarget)
        return

    LCOMMANDS += ['config']
    def subscribe_config(self):
        """subscribe config - configure the current target for subscribe:  [KEY [VAL]]
        """
        self.dhelp['config'] = __doc__
        #? Off by one
        lArgs = self.lArgs
        if self.ocmd2.oCurrentSubTarget is None:
            assert self.ocmd2.oConfig['OTCmd2']['lOnlineTargets'], \
                   "ERROR: empty self.ocmd2.oConfig['OTCmd2']['lOnlineTargets']"
            l = self.ocmd2.oConfig['OTCmd2']['lOnlineTargets']
            self.ocmd2.vError("Use \"sub set\" to set the current target to one of: " + repr(l))
            return
        self.ocmd2.vConfigOp(lArgs, self.ocmd2.oCurrentSubTarget)
        return

    LCOMMANDS += ['topics']
    #? list the message topics that are being hidden
    def subscribe_topics(self):
        """subscribe topics: shows topics subscribed to
        """
        self.dhelp['topics'] = __doc__
        if self.ocmd2.oListenerThread:
            self.vOutput("oListenerThread.lTopics: " + repr(self.ocmd2.G(self.ocmd2.oListenerThread.lTopics)))
        else:
            self.vOutput("Default lTopics: " + repr(self.ocmd2.G(self.ocmd2.lTopics)))
        return


    LCOMMANDS += ['set']
    def subscribe_set(self):
        """subscribe set
        """
        self.dhelp['set'] = __doc__

        #? Off by one
        lArgs = self.lArgs
        assert len(lArgs) > 1, \
               "ERROR: " +"Commands to subscribe (and arguments) are required"
        sTarget = lArgs[1]
        assert sTarget in self.ocmd2.oConfig['OTCmd2']['lOnlineTargets'], \
              "ERROR: " +sTarget +" not in " +repr(self.ocmd2.oConfig['OTCmd2']['lOnlineTargets'])
        assert sTarget in self.ocmd2.oConfig.keys(), \
               "ERROR: " +sTarget +" not in " +repr(self.ocmd2.oConfig.keys())
        self.ocmd2.oCurrentSubTarget = self.ocmd2.oConfig[sTarget]
        self.ocmd2.oCurrentSubTarget.name = sTarget
        self.vOutput("Set target to: " + repr(self.ocmd2.G(sTarget)))
        return

    LCOMMANDS += ['thread']
    def subscribe_thread(self):
        """thread info       - info on the thread listening for messages.
thread stop       - stop a thread listening for messages."""
        self.dhelp['thread'] = __doc__

        sDo = 'thread'
        _lCmds = ['info', 'stop', 'enumerate']
        #? Off by one
        lArgs = self.lArgs
        assert len(lArgs) > 1, "ERROR: sub thread " +str(_lCmds)
        assert lArgs[1] in _lCmds, "ERROR: " +sDo +" " +str(_lCmds)
        sSubCmd = lArgs[1]

        oT = self.ocmd2.oListenerThread
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
                    self.ocmd2.oListenerThread = None
                else:
                    self.vOutput("Listener Thread %r" % (oT.name,))
            return
        if sSubCmd == 'stop':
            if not self.ocmd2.oListenerThread:
                self.vWarn("ListenerThread not already started")
                return
            self.ocmd2.pfeedback("oListenerThread.stop()")
            self.ocmd2.oListenerThread.stop()
            self.ocmd2.oListenerThread.join()
            self.ocmd2.oListenerThread = None
            return
        self.vError("Unrecognized subscribe thread command: " + str(lArgs) +'\n' +__doc__)
        return


    LCOMMANDS += ['hide']
    def subscribe_hide(self):
        """subscribe hide: stop seeing TOPIC messages (e.g. tick - not a pattern)
        """
        self.dhelp['hide'] = __doc__
        if not self.ocmd2.oListenerThread:
            self.vWarn("ListenerThread not already started")
            return
        #? Off by one
        lArgs = self.lArgs
        if len(lArgs) == 1:
            self.ocmd2.oListenerThread.vHide()
        else:
            for sElt in lArgs[1:]:
                self.ocmd2.oListenerThread.vHide(sElt)
        return

    LCOMMANDS += ['show']
    def subscribe_show(self):
        """subscribe show
start seeing TOPIC messages (e.g. tick - not a pattern)
        """
        self.dhelp['show'] = __doc__
        if not self.ocmd2.oListenerThread:
            self.vWarn("ListenerThread not already started")
            return
        #? Off by one
        lArgs = self.lArgs
        if len(lArgs) == 1:
            self.ocmd2.oListenerThread.vShow()
        else:
            for sElt in lArgs[1:]:
                self.ocmd2.oListenerThread.vShow(sElt)
        return

    LCOMMANDS += ['pprint']
    def subscribe_pprint(self):
        """subscribe pprint:
- seeing TOPIC messages with pretty-printing,
- with 0 - off, 1 - on, no argument - current value"""

        self.dhelp['pprint'] = __doc__
        if not self.ocmd2.oListenerThread:
            self.vWarn("ListenerThread not already started")
            return
        #? Off by one
        lArgs = self.lArgs
        if len(lArgs) == 1:
            self.ocmd2.oListenerThread.vPprint('get')
        else:
            self.ocmd2.oListenerThread.vPprint('set', bool(lArgs[1]))
        return

    LCOMMANDS += ['run']
    def subscribe_run(self):
        """subscribe run: start a thread to listen for messages,
        """
        self.dhelp['run'] = __doc__
        assert 'sOnlineRouting' in self.ocmd2.oCurrentSubTarget.keys(), \
               "ERROR: " +'sOnlineRouting' + " not in " +repr(self.ocmd2.oCurrentSubTarget.keys())
        assert self.ocmd2.oCurrentSubTarget['sOnlineRouting']
        sOnlineRouting = self.ocmd2.oCurrentSubTarget['sOnlineRouting']
        sChartId = self.ocmd2.sDefaultChart
        if sOnlineRouting == 'RabbitMQ':
            try:
                # PikaListenerThread needs PikaMixin
                import OpenTrader.PikaListenerThread as ListenerThread
            except ImportError as e:
                self.vError("Cant import PikaListenerThread: add the MQL4/Python directory to PYTHONPATH? " +str(e))
                self.vError("sys.path is: " +repr(sys.path))
                raise
            except Exception as e:
                self.vError(traceback.format_exc(10))
                raise
            sQueueName = self.ocmd2.oCurrentSubTarget['sQueueName']
        elif sOnlineRouting == 'ZeroMQ':
            try:
                import OpenTrader.ZmqListenerThread as ListenerThread
            except ImportError as e:
                self.vError("Cant import ZmqListenerThread: add the MQL4/Python directory to PYTHONPATH? " +str(e))
                raise
            except Exception as e:
                self.vError(traceback.format_exc(10))
                raise
        else:
            raise RuntimeError("sOnlineRouting value in %s section of Cmd2.ini not supported" % (
                sOnlineRouting,))

        if self.ocmd2.oListenerThread is not None:
            self.vWarn("ListenerThread already listening to: " + repr(self.ocmd2.oListenerThread.lTopics))
            return
        #? Off by one
        lArgs = self.lArgs
        if len(lArgs) > 1:
            self.ocmd2.lTopics = lArgs[1:]
        else:
            self.ocmd2.lTopics = ['']
        if sOnlineRouting == 'RabbitMQ':
            from pika import exceptions
            try:
                dConfig = self.ocmd2.oConfig['RabbitMQ']
                assert 'sQueueName' in dConfig, \
                       "ERROR: sQueueName not in dConfig"
                self.ocmd2.oListenerThread = ListenerThread.PikaListenerThread(sChartId,
                                                                         self.ocmd2.lTopics,
                                                                         **dConfig)
                self.ocmd2.oListenerThread.start()
            except exceptions.AMQPConnectionError as e:
                self.vError("Is the RabbitMQ server running?\n" +str(e))
                raise
            except Exception as e:
                self.vError(traceback.format_exc(10))
                raise
        elif sOnlineRouting == 'ZeroMQ':
            import zmq
            try:
                dConfig = self.ocmd2.oConfig['ZeroMQ']
                self.ocmd2.oListenerThread = ListenerThread.ZmqListenerThread(sChartId,
                                                                         self.ocmd2.lTopics,
                                                                         **dConfig)
                self.ocmd2.oListenerThread.start()
            except zmq.ZMQError as e:
                # zmq4: iError = zmq.zmq_errno()
                iError = e.errno
                self.vWarn("run ZMQError in oListenerThread.start : %d %s" % (
                    iError, zmq.strerror(iError),))
            except Exception as e:
                self.vError(traceback.format_exc(10))
                raise
        return

    LCOMMANDS += ['foo']
    def subscribe_foo(self):
        """subscribe foo
        """
        self.dhelp['foo'] = __doc__


    def bexecute(self, lArgs, oValues):
        """bexecute executes the subscribe command.
        """
        _lCmds = LCOMMANDS
        self.lArgs = lArgs
        self.oValues = oValues

        self.vassert_args(lArgs, LCOMMANDS, imin=1)
        if self.bis_help(lArgs):
            return

        # set the target for subscribe, or to see the current target
        if self.ocmd2.oCurrentSubTarget is None:
            assert self.ocmd2.oConfig['OTCmd2']['lOnlineTargets'], \
                   "ERROR: empty self.ocmd2.oConfig['OTCmd2']['lOnlineTargets']"

        sDo = lArgs[0]
        oMeth = getattr(self, 'subscribe_' +sDo)

        if sDo == 'get' or (sDo == 'set' and len(lArgs) == 1) or \
          sDo in ['config', 'topics', 'set', 'thread', 'hide', 'show', 'pprint']:
            oMeth()
            return

        if self.ocmd2.oCurrentSubTarget is None:
            self.vError("Use \"sub set\" to set the current target")
            return

        if sDo == 'run':
            oMeth()
            return

        self.vError("Unrecognized subscribe command: " + str(lArgs) +'\n' +__doc__)
