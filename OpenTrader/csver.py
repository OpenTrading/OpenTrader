# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""Download, resample and convert CSV files into pandas:
{{{
csv url PAIRSYMBOL       - show a URL where you can download  1 minute Mt HST data
csv resample SRAW1MINFILE, SRESAMPLEDCSV, STIMEFRAME - Resample 1 minute CSV data,
                                                       to a new timeframe
                                                       and save it as CSV file
}}}
"""
SDOC = __doc__

import sys
import os
from optparse import make_option

from OpenTrader.doer import Doer

LOPTIONS = []

LCOMMANDS = []

class DoCsv(Doer):
    __doc__ = SDOC
    # putting this as a module variable csv it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'csv')

    LCOMMANDS += ['url']
    def csv_url(self):
        """csv url PAIRSYMBOL
        - show a URL where you can download  1 minute Mt HST data
        """
        self.dhelp['url'] = __doc__

        # see http://www.fxdd.com/us/en/forex-resources/forex-trading-tools/metatrader-1-minute-data/
        sSymbol =  self.lArgs[1].upper()
        self.vOutput("http://tools.fxdd.com/tools/M1Data/%s.zip" % (sSymbol,))
        return

    LCOMMANDS += ['resample']
    def csv_resample(self):
        """csv resample SRAW1MINFILE, SRESAMPLEDCSV, STIMEFRAME
        - Resample 1 minute CSV data, to a new timeframe and save it as CSV file
        """
        self.dhelp['resample'] = __doc__
        sDo = 'csv resample'

        # o oConfig sHistoryDir:

        # csv resample SRAW1MINFILE, SRESAMPLEDCSV, STIMEFRAME -
        # Resample 1 minute CSV data, to a new timeframe
        # Resample 1 minute data to new period, using pandas resample, how='ohlc'
        from PandasMt4 import vResample1Min
        assert len(self.lArgs) > 3, "ERROR: " +sDo +" SRAW1MINFILE, SRESAMPLEDCSV, STIMEFRAME"
        sRaw1MinFile = self.lArgs[1]
        assert os.path.exists(sRaw1MinFile)

        sResampledCsv = self.lArgs[2]
        if os.path.isabs(sResampledCsv):
            assert os.path.isdir(os.path.dirname(sResampledCsv)), "ERROR: directory not found"

        sTimeFrame = self.lArgs[3]
        oFd = sys.stdout
        vResample1Min(sRaw1MinFile, sResampledCsv, sTimeFrame, oFd)
        return

    def bexecute(self, lArgs, oValues):
        """bexecute executes the csv command.
        """
        _lCmds = LCOMMANDS
        self.lArgs = lArgs
        self.oValues = oValues

        self.vassert_args(lArgs, LCOMMANDS, imin=1)
        if self.bis_help(lArgs):
            return

        sDo = lArgs[0]
        if sDo in LCOMMANDS:
            oMeth = getattr(self, 'csv_' +sDo)
            oMeth()
            return

        self.poutput("ERROR: Unrecognized csv command: " + str(lArgs) +'\n' +__doc__)
        return


