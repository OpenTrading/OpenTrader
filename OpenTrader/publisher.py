# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
Publish a message via RabbitMQ to a given chart on a OTMql4Py enabled terminal:
{{{
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
SDOC = __doc__

import sys
import os
import json
from optparse import make_option

from OpenTrader.doer import Doer

LOPTIONS = [make_option("-c", "--chart",
                          dest="sChartId",
                          help="the target chart to publish to (or: ANY ALL NONE)"),
              ]

LCOMMANDS = []

class DoPublish(Doer):
    __doc__ = SDOC
    # putting this as a module variable publish it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'publish')

    LCOMMANDS += ['get']
    def publish_get(self):
        """pub get                   - get the current target for publish; defaults to:
                            the first value of default['lOnlineTargets'] in OTCmd2.ini
        """
        self.dhelp['url'] = __doc__

        if self.ocmd2.oCurrentPubTarget is None:
            l = self.ocmd2.oConfig['OTCmd2']['lOnlineTargets']
            for sElt in l:
                assert sElt in self.ocmd2.oConfig.keys(), \
                       "ERROR: ini section not found for: " + self.ocmd2.sCurrentPubTarget
            if len(l) > 1:
                self.vOutput("The publish online targets available are: " +repr(l))
                return
            sCurrentPubTarget = l[0]
            self.ocmd2.oCurrentPubTarget = self.ocmd2.oConfig[sCurrentPubTarget]
            self.ocmd2.oCurrentPubTarget.name = sCurrentPubTarget
        else:
            sCurrentPubTarget = self.ocmd2.oCurrentPubTarget.name
        self.vOutput("The current publish online target is: " +sCurrentPubTarget)
        return

    LCOMMANDS += ['config']
    def publish_config(self):
        """pub config                - configure the current target for publish: [KEY [VAL]]
        """
        self.dhelp['config'] = __doc__
        if self.ocmd2.oCurrentPubTarget is None:
            assert self.ocmd2.oConfig['OTCmd2']['lOnlineTargets'], \
                   "ERROR: empty self.ocmd2.oConfig['OTCmd2']['lOnlineTargets']"
            l = self.ocmd2.oConfig['OTCmd2']['lOnlineTargets']
            self.vError("Use \"pub set\" to set the current target to one of: " + repr(l))
            return
        # do I need to dict this or make an ConfigObj version?
        self.ocmd2.vConfigOp(self.lArgs, self.ocmd2.oCurrentPubTarget)
        return

    LCOMMANDS += ['set']
    def publish_set(self):
        """  pub set TARGET            - set the target for publish,
        """
        self.dhelp['set'] = __doc__
        sTarget = self.lArgs[1]
        assert sTarget in self.ocmd2.oConfig['OTCmd2']['lOnlineTargets'], \
               "ERROR: " +sTarget +" not in OTCmd2.ini['OTCmd2']['lOnlineTargets']: " \
               +repr(self.ocmd2.oConfig['OTCmd2']['lOnlineTargets'])
        assert sTarget in self.ocmd2.oConfig.keys(), \
               "ERROR: sTarget not in self.ocmd2.oConfig.keys()"
        self.ocmd2.oCurrentPubTarget = self.ocmd2.oConfig[sTarget]
        self.ocmd2.oCurrentPubTarget.name = sTarget
        self.vOutput("Set publish target to: " + repr(self.ocmd2.G(sTarget)))
        return

    LCOMMANDS += ['wait', 'exec', 'sync']
    def publish_wait(self, sChartId, sMark):
        """pub wait COMMAND ARG1 ... - publish a Mql command to Mt4 and wait for the result,
      the command should be a single string, with a space seperating arguments.
        """
        self.dhelp['wait'] = __doc__
        self.dhelp['exec'] = __doc__
        self.dhelp['sync'] = __doc__
        sMsgType = 'exec' # Mt4 command
        # Raises a Mt4Timeout error if there is no answer in 60 seconds
        gRetval = self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, *self.lArgs[1:])

        self.vOutput("Returned: " +repr(self.ocmd2.G(gRetval)))
        return
    publish_exec = publish_wait
    publish_sync = publish_wait

    LCOMMANDS += ['cmd', 'async']
    def publish_cmd(self, sChartId, sMark):
        """pub wait COMMAND ARG1 ... - publish a Mql command to Mt4 asyncronsly,
      the command should be a single string, with a space seperating arguments.
        """
        self.dhelp['cmd'] = __doc__
        self.dhelp['async'] = __doc__
        # I dont think this works, at least under ZeroMQ
        # There is not handling of the null return message
        sMsgType = 'cmd' # Mt4 command
        e = self.ocmd2.eSendMessage(sMsgType, sChartId, sMark, *self.lArgs[1:])
        return
    publish_async = publish_cmd

    # not ready
    LCOMMANDS += ['eval']
    def publish_eval(self, sChartId, sMark):
        """pub eval COMMAND ARG1 ... - publish a Python command to the OTMql4Py,
the command should be a single string, with a space seperating arguments.
        """
        self.dhelp['eval'] = __doc__
        sMsgType = 'eval'
        sInfo = str(self.lArgs[1]) # FixMe: how do we distinguish variable or thunk?
        if len(self.lArgs) > 2:
            sInfo += '(' +str(','.join(self.lArgs[2:])) +')'
        gRetval = self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
        self.vOutput("Returned: " +repr(self.ocmd2.G(gRetval)))
        return

    # not ready
    LCOMMANDS += ['json']
    def publish_json(self, sChartId, sMark):
        """
        """
        self.dhelp['json'] = __doc__
        sMsgType = 'json'
        # FixMe: broken but unused
        sInfo = json.dumps(str(' '.join(self.lArgs[1:])))
        gRetval = self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
        self.vOutput("Returned: " +repr(self.ocmd2.G(gRetval)))
        return

    def bexecute(self, lArgs, oValues):
        """bexecute executes the publish command.
        """
        from OTMql427.SimpleFormat import sMakeMark

        _lCmds = LCOMMANDS
        self.lArgs = lArgs
        self.oValuesb = oValues

        self.vassert_args(lArgs, LCOMMANDS, imin=1)
        if self.bis_help(lArgs):
            return

        if self.ocmd2.oCurrentPubTarget is None:
            assert self.ocmd2.oConfig['OTCmd2']['lOnlineTargets'], \
                "ERROR: empty self.ocmd2.oConfig['OTCmd2']['lOnlineTargets']"

        sDo = lArgs[0]
        oMeth = getattr(self, 'publish_' +sDo)
        # Set the target for subscribe - call without args to see the current target
        if sDo in ['get', 'config'] or (sDo == 'set' and len(lArgs) == 1):
            oMeth()
            return

        # everything beyond here requires an argument
        self.vassert_args(lArgs, LCOMMANDS, imin=2)

        if sDo in ['set']:
            oMeth()
            return

        # sMark is a simple timestamp: unix time with msec.
        sMark = sMakeMark()
        if oValues and oValues.sChartId:
            sChartId = oValues.sChartId
        else:
            sChartId = self.ocmd2.sDefaultChart
        if not sChartId:
            sChartId = 'oChart_ANY_0_FFFFFFFF_1'
            self.ocmd2.vWarn("No default chart set; using: " +sChartId)

        if sDo in ['wait', 'exec', 'sync']:
            oMeth(sChartId, sMark)
            return

        if self.ocmd2.oListenerThread is None:
            self.vWarn("ListenerThread not started; do 'sub run retval.#'")

        if sDo in ['cmd', 'async', 'eval', 'json']:
            oMeth(sChartId, sMark)
            return

        self.poutput("ERROR: Unrecognized publish command: " + str(lArgs) +'\n' +__doc__)
        return
