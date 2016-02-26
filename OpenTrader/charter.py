# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""chart
"""

SDOC = __doc__

import sys
import os
from optparse import make_option

from OpenTrader.doer import Doer

LOPTIONS = []

LCOMMANDS = []

class DoChart(Doer):
    __doc__ = SDOC
    # putting this as a module variable chart it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'chart')

    LCOMMANDS += ['list']
    def chart_list(self):
        """chart list
        """
        self.dhelp['list'] = __doc__

        # get the default chart to be published or subscribed to.
        # all the charts the listener has heard of,
        if self.ocmd2.oListenerThread is None:
            l = []
        else:
            l = self.ocmd2.oListenerThread.lCharts
        self.vOutput(repr(self.ocmd2.G(l)))
        return

    LCOMMANDS += ['get']
    def chart_get(self):
        """chart get
        """
        self.dhelp['get'] = __doc__
        # or (sDo == 'set' and len(lArgs) == 1):
        if self.ocmd2.sDefaultChart:
            self.vOutput("The default chart is: " +self.ocmd2.sDefaultChart)
        elif self.ocmd2.oListenerThread and self.ocmd2.oListenerThread.lCharts:
            self.ocmd2.sDefaultChart = self.ocmd2.G(self.ocmd2.oListenerThread.lCharts[-1])
            self.vOutput("The default chart is: " +self.ocmd2.sDefaultChart)
        else:
            self.vWarn("No default charts available; do 'sub run' first")
            return
        self.ocmd2.G(self.ocmd2.sDefaultChart)
        return

    LCOMMANDS += ['set']
    def chart_set(self):
        """chart list
        """
        self.dhelp['list'] = __doc__
        assert len(self.lArgs) > 1, \
            "ERROR: Commands to chart (and arguments) are required"
        self.ocmd2.sDefaultChart = self.ocmd2.G(self.lArgs[1])
        self.vOutput("The default chart is set to: " +self.lArgs[1])
        return

    def bexecute(self, lArgs, oValues):
        """bexecute executes the chart command.
        """
        self.lArgs = lArgs
        self.oValues = oValues

        self.vassert_args(lArgs, LCOMMANDS, imin=1)
        if self.bis_help(lArgs):
            return

        sDo = lArgs[0]
        if sDo in LCOMMANDS:
            oMeth = getattr(self, 'chart_' +sDo)
            oMeth()
            return

        self.poutput("ERROR: Unrecognized chart command: " + str(lArgs) +'\n' +__doc__)
        return

