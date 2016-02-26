# -*-mode: python; py-indent-offset: 4; encoding: utf-8-dos; coding: utf-8 -*-

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
""" % ("|".join(['vhost_names', 'channels',
                      'connections', 'queues']),)

lRABBIT_GET_THUNKS = ['vhost_names', 'channels',
                      'connections', 'queues']

import sys
import os
import StringIO
from optparse import make_option

from doer import Doer

SDOC = __doc__

LOPTIONS = [make_option("-a", "--address",
                          dest="sHttpAddress",
                          default="127.0.0.1",
                          help="the TCP address of the HTTP rabbitmq_management  (default 127.0.0.1)"),
              make_option('-p', '--port', type="int",
                          dest="iHttpPort", default=15672,
                          help="the TCP port of the HTTP rabbitmq_management plugin (default 15672)"),]

LCOMMANDS = []


class DoRabbit(Doer):
    __doc__ = SDOC
    # putting this as a module variable makes it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'rabbit')

    LCOMMANDS += ['get']
    def rabbit_get(self):
        """
        """
        lArgs = self.lArgs
        sDo = self.lArgs[0]
        assert len(lArgs) > 1, "ERROR: one of: get " +",".join(lRABBIT_GET_THUNKS)
        oFun = getattr(self.ocmd2.oRabbit, sDo +'_' +lArgs[1])
        if lArgs[1] == 'queues':
            lRetval = oFun()
            # do we need a sub-command here?
            lRetval = [x['name'] for x in lRetval]
            self.ocmd2.vOutput(repr(self.ocmd2.G(lRetval)))
        elif lArgs[1] in lRABBIT_GET_THUNKS:
            lRetval = oFun()
            self.ocmd2.vOutput(repr(self.ocmd2.G(lRetval)))
        else:
            self.ocmd2.vError("Choose one of: get " +",".join(lRABBIT_GET_THUNKS))

    def bexecute(self, lArgs, oValues):
        """bexecute executes the rabbit command.
        """
        self.oValues = oValues
        self.lArgs = lArgs

        self.vassert_args(lArgs, LCOMMANDS, imin=1)
        if self.bis_help(lArgs):
            return

        try:
            import pyrabbit
        except ImportError:
            # sys.stdout.write("pyrabbit not installed: pip install pyrabbit\n")
            pyrabbit = None
        if not pyrabbit:
            self.ocmd2.vOutput("Install pyrabbit from http://pypi.python.org/pypi/pyrabbit")
            return
        if not oArgs:
            self.ocmd2.vOutput("Command required: get\n" + __doc__)
            return

        if self.ocmd2.oRabbit is None:
            sTo = oOpts.sHttpAddress +':' +str(oOpts.iHttpPort)
            sUser = self.ocmd2.oConfig['RabbitMQ']['sUsername']
            sPass = self.ocmd2.oConfig['RabbitMQ']['sPassword']
            self.ocmd2.oRabbit = pyrabbit.api.Client(sTo, sUser, sPass)
            vNullifyLocalhostProxy(oOpts.sHttpAddress)

        sdo = lArgs[0]
        if sDo == 'get':
            omethod = getattr(self, 'rabbit_' +sdo)
            omethod()
            return
        
        self.ocmd2.vError("Unrecognized rabbit command: " + str(oArgs) +'\n' +__doc__)

        return True
