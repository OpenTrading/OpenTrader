# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import sys
import os
import json
from pprint import pprint, pformat
import threading
import traceback

from pika import exceptions

from OTMql427 import PikaListener
from OTMql427 import SimpleFormat

class PikaListenerThread(threading.Thread, PikaListener.PikaMixin):

    def __init__(self, sChartId, lTopics, **dArgs):
        dThreadArgs = {'name': sChartId, 'target': self.run}
        PikaListener.PikaMixin.__init__(self, sChartId, **dArgs)
        threading.Thread.__init__(self, **dThreadArgs)
        self.oLocal = threading.local()
        self.lCharts = []
        self.jLastRetval = []
        self.jLastTick = []
        self.jLastBar = []
        self.gLastTimer = []
        self._running = threading.Event()
        self.dRetvals = {}
        if not lTopics:
            self.lTopics = ['#']
        else:
            self.lTopics = lTopics
        self.bPprint = False
        self.lHide = []
        # eBindBlockingListener
        self.vPyRecvOnListener('listen-for-ticks', self.lTopics)
        self._running.set()

    def run(self):
        while self._running.is_set() and len(self.oListenerChannel._consumers):
            try:
                self.oListenerChannel.connection.process_data_events()
            except exceptions.ConnectionClosed, e:
                #? are these spurious
                #? should we look at self.oListenerChannel.connection
                sys.stdout.write("DEBUG: stopping due to exception " +str(e) +"\n")
                self.stop()
            except (exceptions.ConsumerCancelled, KeyboardInterrupt,), e:
                sys.stdout.write("DEBUG: stopping listener thread " +str(e) +"\n")
                self.stop()
            except Exception, e:
                sys.stdout.write("WARN: unhandled error - stopping listener thread " +str(e) +"\n")
                #? raise
                self.stop()

    def stop(self):
        self._running.clear()
        #? self.oListenerChannel.stop_consuming()

    def vPprint(self, sMsgType, sMsg=None, sPrefix="INFO: "):
        if sMsgType == 'get':
            sys.stdout.write("INFO: bPprint" +repr(self.bPprint) + "\n")
        elif sMsgType == 'set':
            self.bPprint = bool(sMsg)
        elif sMsgType in self.lHide:
            pass
        elif self.bPprint and sMsg:
            # may need more info here - chart and sMark
            sys.stdout.write(sPrefix +sMsgType +" = " +pformat(sMsg) +"\n")
        else:
            sys.stdout.write(sPrefix +sMsgType +" = " +repr(sMsg) +"\n")

    def vHide(self, sMsgType=None):
        if not sMsgType:
            sys.stdout.write("INFO: hiding " +repr(self.lHide) + "\n")
            return
        if sMsgType not in self.lHide:
            self.lHide.append(sMsgType)

    def vShow(self, sMsgType=None):
        if not sMsgType:
            sys.stdout.write("INFO: hiding " +repr(self.lHide) + "\n")
            return
        if sMsgType in self.lHide:
            self.lHide.remove(sMsgType)

    def vPyCallbackOnListener(self, oChannel, oMethod, oProperties, sBody):
        # dir(oProperties) = [app_id', 'cluster_id', 'content_encoding', 'content_type', 'correlation_id', 'decode', 'delivery_mode', 'encode', 'expiration', 'headers', 'message_id', 'priority', 'reply_to', 'timestamp', 'type', 'user_id']

        oChannel.basic_ack(delivery_tag=oMethod.delivery_tag)
        lArgs = SimpleFormat.lUnFormatMessage(sBody)
        sMsgType = lArgs[0]
        sChart = lArgs[1]
        sIgnore = lArgs[2] # should be a hash on the payload
        sMark = lArgs[3]
        sPayloadType = lArgs[4]
        gPayload = lArgs[4:] # overwritten below

        try:
            # sys.stdout.write("INFO: sChart: " +repr(sChart) +'\n')

            if sChart not in self.lCharts:
                # keep a list of charts that we have seen for "chart list"
                self.lCharts.append(sChart)

            if sMsgType == 'retval':
                try:
                    gPayload = gRetvalToPython(lArgs)
                except Exception, e:
                    sys.stdout.write("WARN: vPyCallbackOnListener error decoding to Python: %s\n%r" % (str(e), sBody, ))
                    return

                self.jLastRetval = gPayload
                self.dRetvals[sMark] = gPayload

            elif sMsgType == 'bar':
                assert sPayloadType == 'json', \
                    sMsgType +" sPayloadType expected 'json' not " \
                    +sPayloadType +"\n" +sBody
                # can use this to find the current bid and ask
                gPayload =json.loads(lArgs[5])
                self.jLastBar = gPayload

            elif sMsgType == 'tick':
                assert sPayloadType == 'json', \
                    sMsgType +" sPayloadType expected 'json' not " \
                    +sPayloadType +"\n" +sBody
                # can use this to find the current bid and ask
                gPayload =json.loads(lArgs[5])
                self.jLastTick = gPayload

            elif sMsgType == 'timer':
                assert sPayloadType == 'json', \
                    sMsgType +" sPayloadType expected 'json'" +"\n" +sBody
                # can use this to find if we are currently connected
                gPayload = json.loads(lArgs[5])
                self.gLastTimer = gPayload
            else:
                sys.stdout.write("WARN: vPyCallbackOnListener unrecognized sMsgType: %r\n" % (sBody, ))
                return

            # may need more info here - chart and sMark
            if sMsgType == 'retval':
                # you really need sMark for retval
                self.vPprint(sMsgType, gPayload, "INFO: [" +sMark +"] ")
            else:
                self.vPprint(sMsgType, gPayload)
        except Exception, e:
            sys.stderr.write(traceback.format_exc(10) +"\n")

def gRetvalToPython(lElts):
    # raises MqlError
    global dPENDING

    sType = lElts[4]
    sVal = lElts[5]
    if sVal == "":
        return ""
    if sType == 'string':
        gRetval = sVal
    elif sType == 'error':
        #? should I raise an error?
        raise MqlError(sVal)
    elif sType == 'datetime':
        #? how do I convert this
        # I think it's epoch seconds as an int
        # but what TZ? TZ of the server?
        # I'll treat it as a float like time.time()
        # but probably better to convert it to datetime
        gRetval = float(sVal)
    elif sType == 'bool':
        gRetval = bool(sVal)
    elif sType == 'int':
        gRetval = int(sVal)
    elif sType == 'json':
        gRetval = json.loads(sVal)
    elif sType == 'double':
        gRetval = float(sVal)
    elif sType == 'none':
        gRetval = None
    elif sType == 'void':
        gRetval = None
    else:
        sys.stdout.write("WARN: unknown type %s in %r\n" % (sType, lElts,))
        gRetval = None
    return gRetval


if __name__ == '__main__':
    o = None
    try:
        o = PikaListenerThread('test', 'timer.#')
        print threading.enumerate()
        o.run()
    except KeyboardInterrupt:
        if o:
            o.stop()
            o.join()
