# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import sys
import os
import json
from pprint import pprint, pformat
import threading
import time
import traceback

import zmq

from OTMql427.ZmqListener import ZmqMixin
from OTMql427.SimpleFormat import gRetvalToPython

from ListenerThread import ListenerThread

class ZmqListenerThread(ListenerThread, ZmqMixin):

    def __init__(self, sChartId, lTopics, **dArgs):
        if not lTopics or lTopics == ['#']:
            self.lTopics = ['']
        else:
            self.lTopics = lTopics

        ZmqMixin.__init__(self, sChartId, **dArgs)
        ListenerThread.__init__(self, sChartId, **dArgs)
        dThreadArgs = {'name': sChartId, 'target': self.run}
        threading.Thread.__init__(self, **dThreadArgs)

    def run(self):

        sys.stdout.write("Starting Zmq ListenerThread listening to: " + repr(self.lTopics) +"\n")
        if self.oSubPubSocket is None:
            try:
                self.eConnectToSub(self.lTopics)
            except Exception as e:
                sys.stdout.write("ERROR: starting listener thread eConnectToSub " +str(e))
                sys.stderr.write(traceback.format_exc(10) +"\n")
                return
            
        self._running.set()
        while self._running.is_set():
            try:
                #? 0 is blocking
                sString = self.sRecvOnSubPub(iFlags=0)
                if sString == "": continue
                self.vCallbackOnListener(sString)
            except zmq.ZMQError as e:
                # zmq4: iError = zmq.zmq_errno()
                iError = e.errno
                if iError == zmq.EAGAIN:
                    #? This should only occur if iFlags are zmq.NOBLOCK
                    time.sleep(1.0)
                else:
                    sys.stdout.write("WARN: run ZMQError in Recv listener: %d %s" % (
                        iError, zmq.strerror(iError),))
                    sys.stdout.flush()
                sRetval = ""
            except (KeyboardInterrupt,) as e:
                # Basic.Cancel
                sys.stdout.write("DEBUG: stopping listener thread " +str(e) +"\n")
                self.stop()
            except Exception as e:
                sys.stdout.write("WARN: unhandled error - stopping listener thread " +str(e) +"\n")
                #? raise
                self.stop()
        try:
            if self.oSubPubSocket:
                self.oSubPubSocket.setsockopt(zmq.LINGER, 0)
                time.sleep(0.1)
                self.oSubPubSocket.close()
                self.oSubPubSocket = None
        except Exception as e:
            sys.stdout.write("WARN: error closing listener thread connection" +str(e) +"\n")
            sys.stdout.flush()

    def stop(self):
        self._running.clear()


if __name__ == '__main__':
    o = None
    try:
        o = ZmqListenerThread('test', 'timer')
        print threading.enumerate()
        o.run()
    except KeyboardInterrupt:
        if o:
            o.stop()
            o.join()
        print threading.enumerate()
