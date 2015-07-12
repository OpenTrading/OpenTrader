# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import sys
import os
import json
from pprint import pprint, pformat
import threading
import traceback

from OTMql427 import PikaListener

from ListenerThread import gRetvalToPython, ListenerThread

class PikaListenerThread(ListenerThread, PikaListener.PikaMixin):

    def __init__(self, sChartId, lTopics, **dArgs):
        if not lTopics or lTopics == ['']:
            self.lTopics = ['#']
        else:
            self.lTopics = lTopics
        self.sQueueName = dArgs['sQueueName']
        
        PikaListener.PikaMixin.__init__(self, sChartId, **dArgs)
        ListenerThread.__init__(self, sChartId, **dArgs)
        dThreadArgs = {'name': sChartId, 'target': self.run}
        threading.Thread.__init__(self, **dThreadArgs)

    def run(self):
        from pika import exceptions

        sys.stdout.write("Starting Pika ListenerThread listening to: " + repr(self.lTopics) +"\n")
        # eBindBlockingListener
        self.vPyRecvOnListener(self.sQueueName, self.lTopics)
        self._running.set()
        while self._running.is_set() and len(self.oListenerChannel._consumers):
            try:
                self.oListenerChannel.connection.process_data_events()
            except exceptions.ConnectionClosed, e:
                sys.stdout.write("DEBUG: stopping due to ConnectionClosed " +str(e) +"\n")
                self.stop()
            except (exceptions.ConsumerCancelled, KeyboardInterrupt,), e:
                # Basic.Cancel
                sys.stdout.write("DEBUG: stopping listener thread " +str(e) +"\n")
                self.stop()
            except Exception, e:
                sys.stdout.write("WARN: unhandled error - stopping listener thread " +str(e) +"\n")
                #? raise
                self.stop()
        try:
            self.oListenerChannel.connection.close()
        except Exception, e:
            sys.stdout.write("WARN: error closing listener thread connection" +str(e) +"\n")
        self.oListenerChannel = None

    def stop(self):
        self._running.clear()
        #? self.oListenerChannel.stop_consuming()

    def vPyCallbackOnListener(self, oChannel, oMethod, oProperties, sBody):
        # dir(oProperties) = [app_id', 'cluster_id', 'content_encoding', 'content_type', 'correlation_id', 'decode', 'delivery_mode', 'encode', 'expiration', 'headers', 'message_id', 'priority', 'reply_to', 'timestamp', 'type', 'user_id']

        oChannel.basic_ack(delivery_tag=oMethod.delivery_tag)
        self.vCallbackOnListener(sBody)

        
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
        print threading.enumerate()
