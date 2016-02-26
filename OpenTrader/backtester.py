# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
Backtest recipes with chefs, and serve the results as metrics and plots.

The subcommands are:
* omlette   - An omlette is an HDF5 file that saves all the data from a backtest
* feed      - Create feeds (pandas DataFrames) from CSV OHLCV files
* recipe    - Set the recipe that the chef will use, and make the ingredients from the feeds
* chef      - Set the chef that we will use, and cook from the ingredients and the feeds
* servings  - List the servings the chef has cooked, and dish out the servings
* plot      - Plot the servings the chef has cooked, using matplotlib
"""

SDOC = __doc__

import sys
import os
import traceback
from optparse import make_option
from pprint import pprint, pformat

try:
    from OpenTrader.deps import tabview
except ImportError:
    # depends on curses
    tabview = None

from OpenTrader.OTUtils import sStripCreole, lConfigToList
from OpenTrader.doer import Doer

sCURRENT_OMLETTE_DIR = ""

LOPTIONS = [make_option("-C", "--chef",
                          dest="sChef",
                          # no default here - we want it to come from the ini
                          default="",
                          help="the backtest package (one of: PybacktestChef)"),
              make_option("-R", "--recipe",
                          dest="sRecipe",
                          # no default here - we want it to come from the ini
                          default="",
                          help="recipe to backtest (one of SMARecipe"),
              make_option("-H", "--history_dir",
                          dest="sHistoryDir",
                          # no default here
                          default="",
                          help="directory for creating Create feeds from CSV OHLCV files")
              ]

LCOMMANDS = []

#? feed rename delete

dFEED_CACHE = {}
sFEED_CACHE_KEY = ""

def oEnsureOmlette(ocmd2, _oValues, sNewOmlette=""):
    from OpenTrader.Omlettes import Omlette
    if not sNewOmlette and hasattr(ocmd2, 'oOm') and ocmd2.oOm:
        return ocmd2.oOm
    oOm = Omlette.Omlette(oFd=sys.stdout)
    if sNewOmlette:
        # The default is no HDF file - it's not in ocmd2.oOptions.sOmlette
        oOm.oAddHdfStore(sNewOmlette)

    ocmd2.oOm = oOm
    return oOm

def oEnsureRecipe(ocmd2, oValues, sNewRecipe=""):
    oOm = oEnsureOmlette(ocmd2, oValues)
    if not sNewRecipe and hasattr(oOm, 'oRecipe') and oOm.oRecipe:
        return oOm.oRecipe
    if not sNewRecipe:
        # The are set earlier in the call to do_back
        sNewRecipe = ocmd2.sRecipe
    if hasattr(oOm, 'oRecipe') and oOm.oRecipe:
        sOldName = oOm.oRecipe.sName
    else:
        sOldName = ""
    oRecipe = oOm.oAddRecipe(sNewRecipe)
    if sOldName and sOldName != sNewRecipe:
        #? do we invalidate the current servings if the recipe changed?
        vClearOven(ocmd2, oValues)
    return oRecipe

def oEnsureChef(ocmd2, oValues, sNewChef=""):
    oOm = oEnsureOmlette(ocmd2, oValues)
    if not sNewChef and hasattr(oOm, 'oChefModule') and oOm.oChefModule:
        return oOm.oChefModule
    if not sNewChef:
        # The are set earlier in the call to do_back
        sNewChef = ocmd2.sChef
    if hasattr(oOm, 'oChefModule') and oOm.oChefModule and oOm.oChefModule.sChef:
        sOldName = oOm.oChefModule.sChef
    else:
        sOldName = ""
    oChefModule = oOm.oAddChef(sNewChef)
    if sOldName and sOldName != sNewChef:
        #? do we invalidate the current servings if the chef changed?
        vClearOven(ocmd2, oValues)
    return oOm.oChefModule

def vClearOven(ocmd2, oValues):
    oOm = oEnsureOmlette(ocmd2, oValues)
    oOm.oBt = None

class DoBacktest(Doer):
    __doc__ = SDOC
    # putting this as a module variable backtest it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'backtest')
        self._G = self.ocmd2._G

    LCOMMANDS += ['omlette']
    def backtest_omlette(self):
        """backtest omlette

An omlette is an HDF5 file that saves all the information from a backtest,
including the metadata: all of parameter values that were used in the recipe,
the parameters used by the cook, and the servings results.

You should open an omlette before you backtest giving it a filename,
and close it after the 'chef cook' and 'servings'.
{{{
back omlette open FILE           - open an HDF file to save all the backtest parts
back omlette check               - show the current omlette filename
back omlette display             - display the current omlette HDF sections
back omlette close               - close the HDF file saving the omlette
}}}
Real Soon Now you will be able to enjoy them more by reloading previously saved
omlettes, plotting the data or the results, and adding or editing comments.
        """
        sDo = 'omlette'
        #!WTF local variable '__doc__' referenced before assignment
        self.dhelp['omlette'] = __doc__

        # is this a backtest command or should it move up
        # leave it here for now, and move it up later

        global sCURRENT_OMLETTE_DIR
        # ingredients recipe dish
        # plot sSection
        #
        lArgs = self.lArgs
        _lCmds = ['load', 'open', 'check', 'save', 'close', 'display']
        assert len(lArgs) > 1, "ERROR: " +sDo +" " +str(_lCmds)
        sCmd = lArgs[1]
        assert sCmd in _lCmds, "ERROR: " +sDo +" " +str(_lCmds)

        oValues = self.oValues
        oOm = oEnsureOmlette(self.ocmd2, oValues, sNewOmlette="")
        if sCmd == 'check':
            assert hasattr(oOm, 'oHdfStore')
            assert oOm.oHdfStore is not None
            # FixMe: something better than filename
            self.poutput(sDo +" filename: " +oOm.oHdfStore.filename)
            return

        if sCmd == 'display':
            # display gives a complete listing of the contents of the HDF file
            assert hasattr(oOm, 'oHdfStore') and oOm.oHdfStore
            self.poutput(repr(oOm.oHdfStore))
            return

        ## if sCmd == 'save':
        ##     return

        if sCmd == 'close':
            assert oOm.oHdfStore is not None, \
                   "ERROR: " +sDo +" " +sCmd +"; not open: use '" +sDo +" open FILE'"
            oOm.vClose()
            return

        assert len(lArgs) >= 3, \
               "ERROR: " +sDo +" " +sCmd +" " +" FILENAME"
        sFile = lArgs[2]

        if sCmd == 'open':
            o = oOm.oAddHdfStore(sFile)
            assert o is not None and oOm.oHdfStore is not None
            sCURRENT_OMLETTE_DIR = os.path.dirname(sFile)
            return

        if sCmd == 'load':
            assert os.path.isfile(sFile), \
                   "ERROR: " +sDo +" " +sCmd +" file not found " +sFile
            sCURRENT_OMLETTE_DIR = os.path.dirname(sFile)
            raise RuntimeError(NotImplemented)
            return

        self.vError("Unrecognized omlette command: " + str(lArgs) +'\n' +__doc__)
        return

    # Create feeds (pandas DataFrames) from CSV OHLCV files
    LCOMMANDS += ['feed']
    def backtest_feed(self):
        """
==== OTCmd2 backtest feed

Create feeds (pandas DataFrames) from CSV OHLCV files.
{{{
back feed dir                                  - NotImplemented
back feed dir dirname                          - NotImplemented

back feed read_mt4_csv SYMBOL TIMEFRAME [YEAR] - read a CSV file from Mt4 into pandas
back feed read_yahoo_csv SYMBOL [STARTYEAR]    - read a Yahoo internet feed into pandas
back feed list                                 - list the feeds we have read
back feed get                                  - get the key name of the current feed
back feed info                                 - concise summary of the DataFrame
back feed plot                                 - plot the CSV data using OTPpnAmgc
               This plots the feed, with SMA, RSIs and MACDs, using matplotlib.
}}}
        """
        global dFEED_CACHE
        global sFEED_CACHE_KEY
        sDo = 'feed'
        #!WTF local variable '__doc__' referenced before assignment
        self.dhelp['feed'] = __doc__
        lArgs = self.lArgs
        oValues = self.oValues

        #? rename delete
        _lCmds = ['dir', 'list', 'get', 'set',
                  'read_mt4_csv', 'read_yahoo_csv', 'info', 'plot', 'to_hdf']
        assert len(lArgs) > 1, "ERROR: " +sDo +" command required: " +str(_lCmds)
        sCmd = lArgs[1]
        assert lArgs[1] in _lCmds, "ERROR: " +sDo +" " +str(_lCmds)

        if sCmd == 'dir':
            if len(lArgs) == 2:
                if not self.ocmd2.oConfig['feed']['sHistoryDir']:
                    self.poutput("No default history directory set: use \"feed dir dir\"")
                elif not os.path.isdir(self.ocmd2.oConfig['feed']['sHistoryDir']):
                    self.poutput("History directory not found: use \"feed dir dir\": " + \
                                 self.ocmd2.oConfig['feed']['sHistoryDir'])
                else:
                    self.poutput("Default history directory: " + \
                                 self.ocmd2.oConfig['feed']['sHistoryDir'])
                return

            sDir = lArgs[2]
            assert os.path.isdir(sDir)
            self.ocmd2.oConfig['feed']['sHistoryDir'] = sDir
            return

        if sCmd == 'read_mt4_csv':
            from OpenTrader.PandasMt4 import oReadMt4Csv
            assert len(lArgs) >= 3, \
                   "ERROR: " +sDo +" " +sCmd +" FILENAME [SYMBOL TIMEFRAME YEAR]"
            sFile = lArgs[2]
            if not os.path.isabs(sFile):
               sFile = os.path.join(self.ocmd2.sRoot, sFile)
            if False and not os.path.isfile(sFile):
                #? was self.ocmd2.oOptions.sMt4Dir
                sHistoryDir = os.path.join(self.ocmd2.oConfig['OTCmd2']['sMt4Dir'], 'history')
                if os.path.isdir(sHistoryDir):
                    import glob
                    l = glob.glob(sHistoryDir +"/*/" +sFile)
                    if l:
                        sFile = l[0]
                        self.vInfo("Found history file: " + sFile)
            assert os.path.isfile(sFile), \
                   "ERROR: " +sDo +" " +sCmd +" file not found " +sFile
            if len(lArgs) > 5:
                sSymbol = lArgs[3]
                sTimeFrame = lArgs[4]
                sYear = lArgs[5]
            else:
                lCooked = os.path.split(sFile)[-1].split('.')[0].split('-')
                if len(lCooked) > 1:
                    sYear = lCooked[-1]
                else:
                    sYear = ""
                sSymbol = lCooked[0][:6]
                sTimeFrame = lCooked[0][6:]

            self.vDebug(sDo +" " +sCmd +" " + \
                       "sSymbol=" +sSymbol \
                       +", sYear=" +sYear \
                       +", sTimeFrame=" +sTimeFrame)

            mFeedOhlc = oReadMt4Csv(sFile, sTimeFrame, sSymbol, sYear="")
            assert mFeedOhlc is not None, "oReadMt4Csv failed on " + sFile
            mFeedOhlc.info(True, sys.stdout)

            # NaturalNameWarning: object name is not a valid Python identifier: 'Mt4_csv|EURUSD|1440|2014'; it does not match the pattern ``^[a-zA-Z_][a-zA-Z0-9_]*$``;
            sKey = 'Mt4_csv' +'_' +sSymbol +'_' +sTimeFrame +'_' +sYear
            oOm = oEnsureOmlette(self.ocmd2, oValues)
            _dCurrentFeedFrame = oOm.dGetFeedFrame(sFile,
                                                   sTimeFrame,
                                                   sSymbol,
                                                   sYear)
            from OpenTrader.PandasMt4 import oReadMt4Csv, oPreprocessOhlc, vResampleFiles
            mFeedOhlc = oPreprocessOhlc(_dCurrentFeedFrame['mFeedOhlc'])
            sys.stdout.write('INFO:  Data Open length: %d\n' % len(mFeedOhlc))
            _dCurrentFeedFrame['mFeedOhlc'] = mFeedOhlc

            dFEED_CACHE[sKey] = _dCurrentFeedFrame
            sFEED_CACHE_KEY = sKey
            return

        _lFeedCacheKeys = dFEED_CACHE.keys()
        if sCmd == 'list':
            self.poutput("Feed keys: %r" % (self.G(_lFeedCacheKeys,)))
            return

        if sCmd == 'get':
            self.poutput("Current Feed key: %s" % (self.G(sFEED_CACHE_KEY,)))
            return

        if sCmd == 'set':
            assert len(lArgs) >= 3, \
                   "ERROR: " +sDo +" " +sCmd +" " + '|'.join(_lFeedCacheKeys)
            sKey = lArgs[2]
            assert sKey in _lFeedCacheKeys, \
                   "ERROR: " +sDo +" " +sCmd +" " + '|'.join(_lFeedCacheKeys)
            sFEED_CACHE_KEY = sKey
            return

        # The following all require that a feed has been loaded
        if not sFEED_CACHE_KEY or sFEED_CACHE_KEY not in dFEED_CACHE:
            self.vError("Run \"back read_*\" first to read a DataFrame")
            return
        _dCurrentFeedFrame = dFEED_CACHE[sFEED_CACHE_KEY]

        if _dCurrentFeedFrame is None:
            self.vError("Run \"back read_*\" first to read a DataFrame")
            return
        sSymbol = _dCurrentFeedFrame['sSymbol']
        sKey = _dCurrentFeedFrame['sKey']
        sTimeFrame = _dCurrentFeedFrame['sTimeFrame']
        mFeedOhlc = _dCurrentFeedFrame['mFeedOhlc']

        if sCmd in ['to_hdf']:
            """ DataFrame.to_hdf(path_or_buf, key, **kwargs)
            activate the HDFStore
            Parameters :
              path_or_buf : the path (string) or buffer to put the store
              key : string indentifier for the group in the store
              """

            assert len(lArgs) >= 3, \
                   "ERROR: " +sDo +" " +sCmd +" fixed|table filename"
            sType = lArgs[2]
            assert sType in ['fixed', 'table']
            sFile = lArgs[3]
            # FixME: if absolute assert os.path.exists(os.path.dirname(sFile))
            #? lArgs[4:] -> **kw ?
            vRetval = mFeedOhlc.to_hdf(sFile, sKey, format=sType)
            return

        _dPlotParams = self.ocmd2.oConfig['feed.plot.params']

        if sCmd == 'info':
            """Concise summary of a DataFrame.
            Parameters :
            verbose : boolean, default True
                    If False, don’t print column count summary
            buf : writable buffer, defaults to sys.stdout
            """
            import yaml

            mFeedOhlc.info(True, sys.stdout)

            s = '|  %s  |' % ("Plot Params",)
            self.poutput('-' * len(s))
            self.poutput(s)
            self.poutput('-' * len(s))
            yaml.dump(_dPlotParams,
                      allow_unicode=True,
                      default_flow_style=False)
            self.poutput('-' * len(s))
            return

        # 'download_hst_zip'
        if sCmd == 'plot':

            import matplotlib
            if 'matplotlib.rcParams' in self.ocmd2.oConfig:
                for sKey, gVal in self.ocmd2.oConfig['matplotlib.rcParams'].items():
                    matplotlib.rcParams[sKey] = gVal
            import numpy as np
            from OpenTrader.OTPpnAmgc import vGraphData

            from OpenTrader.OTBackTest import oPreprocessOhlc
            mFeedOhlc = oPreprocessOhlc(mFeedOhlc)
            # (Pdb) pandas.tseries.converter._dt_to_float_ordinal(mFeedOhlc.index)[0]
            # 735235.33333333337
            nDates = matplotlib.dates.date2num(mFeedOhlc.index.to_pydatetime())
            nVolume = 1000*np.random.normal(size=len(mFeedOhlc))

            self.vInfo("This may take minutes to display depending on your computer's speed")
            vGraphData(sSymbol, nDates,
                       mFeedOhlc.C.values, mFeedOhlc.H.values, mFeedOhlc.L.values, mFeedOhlc.O.values,
                       nVolume,
                       **_dPlotParams)
            return

        self.vError("Unrecognized feed command: " + str(lArgs) +'\n' +__doc__)
        return

    # Set the recipe that the chef will use, and make the ingredients from the feeds
    LCOMMANDS += ['recipe']
    def backtest_recipe(self):
        """
==== OTCmd2 backtest recipe

Set the recipe that the chef will use, and make the ingredients from the feeds.
{{{
back recipe list                        - list the known recipes
back recipe get                         - show the current recipe
back recipe set RECIPE                  - set the current recipe
back recipe ingredients                 - make the ingredients
back recipe config                      - show the current recipe config
back recipe config KEY                  - show the current config of KEY
back recipe config KEY VAL              - set the current config of KEY to VAL
back recipe config tabview              - view the config with tabview
}}}
        """
        global dFEED_CACHE
        global sFEED_CACHE_KEY
        lArgs = self.lArgs
        oValues = self.oValues
        sDo = 'recipe'
        #!WTF local variable '__doc__' referenced before assignment
        self.dhelp['recipe'] = __doc__
        lArgs = self.lArgs

        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore') # ignore problems during import
            from OpenTrader.Omlettes import lKnownRecipes
        # self.vDebug("lKnownRecipes: " + repr(lKnownRecipes))
        # are ingredients under chef?
        _lCmds = ['set', 'list', 'get', 'make', 'ingredients', 'config']

        sCmd = str(lArgs[1])
        if sCmd == 'list':
            self.poutput("Known Recipes: %r" % (self.G(lKnownRecipes,)))
            return

        if sCmd == 'get' or (sCmd == 'set' and len(lArgs) == 2):
            self.poutput("Current Recipe: %s" % (self.ocmd2.sRecipe,))
            return

        assert len(lArgs) > 1, "ERROR: not enough args: " +sDo +str(_lCmds)
        assert sCmd in _lCmds, "ERROR: %s %s not in: %r " % (
            sDo, sCmd, _lCmds)

        if sCmd == 'config':
            oRecipe = oEnsureRecipe(self.ocmd2, oValues)
            self.ocmd2.vConfigOp(lArgs, oRecipe.oConfig)
            return

        if sCmd == 'set':
            assert len(lArgs) > 2, \
                   "ERROR: %s %s requires one of: %s" % (
                sDo, sCmd, '|'.join(lKnownRecipes))
            sNewRecipe = str(lArgs[2])
            assert sNewRecipe in lKnownRecipes, \
                   "ERROR: %s %s %s not in: %s" % (
                sDo, sCmd, sNewRecipe, '|'.join(lKnownRecipes))
            if self.ocmd2.sRecipe != sNewRecipe:
                self.ocmd2.sRecipe = sNewRecipe
                oRecipe = oEnsureRecipe(self.ocmd2, oValues, sNewRecipe=sNewRecipe)
            #? do we update the config file? - I think not
            #? self.ocmd2.oConfig['backtest']['sRecipe'] = sNewRecipe
            return

        # The following all require that a feed has been loaded
        assert sFEED_CACHE_KEY
        assert sFEED_CACHE_KEY in dFEED_CACHE
        _dCurrentFeedFrame = dFEED_CACHE[sFEED_CACHE_KEY]
        assert _dCurrentFeedFrame
        if sCmd == 'make' or sCmd == 'ingredients':
            assert _dCurrentFeedFrame
            oRecipe = oEnsureRecipe(self.ocmd2, oValues)
            # ugly
            dFeedParams = _dCurrentFeedFrame
            mFeedOhlc = _dCurrentFeedFrame['mFeedOhlc']
            dFeeds = dict(mFeedOhlc=mFeedOhlc, dFeedParams=dFeedParams)

            oRecipe.dMakeIngredients(dFeeds)
            assert oRecipe.dIngredients
            return

        self.vError("Unrecognized recipe command: " + str(lArgs) +'\n' +__doc__)
        return

    LCOMMANDS += ['chef']
    def backtest_chef(self):
        """
==== OTCmd2 backtest chef

Set the chef that we will use, and cook from the ingredients and the feeds.
{{{
back chef list                          - list the known chefs
back chef set                           - show the current chef
back chef set CHEF                      - set the current chef
back chef cook                          - cook the recipe by the chef
}}}
        """
        global dFEED_CACHE
        global sFEED_CACHE_KEY
        lArgs = self.lArgs
        sDo = 'chef'
        #!WTF local variable '__doc__' referenced before assignment
        self.dhelp['chef'] = __doc__
        lArgs = self.lArgs

        from OpenTrader.Omlettes import lKnownChefs
        # self.vDebug("lKnownChefs: " + repr(lKnownChefs))

        _lCmds = ['get', 'set', 'list', 'cook']
        assert len(lArgs) > 1, "ERROR: not enough args: " +sDo +str(_lCmds)
        sCmd = lArgs[1]

        if sCmd == 'list':
            self.poutput("Known Chefs: %r" % (lKnownChefs,))
            return

        if sCmd == 'get' or (sCmd == 'set' and len(lArgs) == 2):
            self.poutput("Current Chef: %s" % (self.ocmd2.sChef,))
            return

        assert sCmd in _lCmds, "ERROR: not in: " +sDo +str(_lCmds)

        if sCmd == 'set':
            assert len(lArgs) > 2, \
                   "ERROR: %s %s needs one of: %s" % (
                sDo, sCmd, '|'.join(lKnownChefs))
            sNewChef = str(lArgs[2])
            assert sNewChef in lKnownChefs, \
                   "ERROR: %s %s %s not in: %s" % (
                sDo, sCmd, sNewChef, '|'.join(lKnownChefs))
            if self.ocmd2.sChef != sNewChef:
                self.ocmd2.sChef = sNewChef
                oChef = oEnsureChef(self.ocmd2, oValues, sNewChef=sNewChef)
            #? do we update the config file? - I think not
            #? self.ocmd2.oConfig['backtest']['sChef'] = sNewChef
            return

        # The following all require that a feed has been loaded
        assert sFEED_CACHE_KEY
        assert sFEED_CACHE_KEY in dFEED_CACHE
        _dCurrentFeedFrame = dFEED_CACHE[sFEED_CACHE_KEY]
        assert _dCurrentFeedFrame

        # There's always a default provided of these
        oOm = oEnsureOmlette(self.ocmd2, oValues)
        oRecipe = oEnsureRecipe(self.ocmd2, oValues)
        oChefModule = oEnsureChef(self.ocmd2, oValues)

        if sCmd == 'cook':
            from OpenTrader.OTBackTest import oPyBacktestCook
            assert oRecipe.dIngredients
            # ugly
            dFeeds = _dCurrentFeedFrame

            oBt = oPyBacktestCook(dFeeds, oRecipe, oChefModule, oOm)
            assert oBt is not None
            if type(oBt) == str:
                raise RuntimeError(oBt)
            oOm.oBt = oBt
            # self.vDebug("Cooked " + oBt.sSummary())
            return

        self.vError("Unrecognized chef command: " + str(lArgs) +'\n' +__doc__)
        return

    # List the servings the chef has cooked, and dish out the servings
    LCOMMANDS += ['servings']
    def backtest_servings(self):
        """
==== OTCmd2 backtest servings

List the servings the chef has cooked, and dish out the servings.
{{{
back servings list            - list the servings that result from the recipe and chef
back servings signals         - show the signals: when to buy or sell
back servings trades          - show the trades: what was bought or sold
back servings positions       - show how the trades effected the positions
back servings equity          - show the results of the trades as equity differences
back servings reviews         - show the metrics and reviews of the trades
back servings tabview SERVING - view with tabview: the SERVING, or reviews
}}}
        """
        #? back reviews get/set/servings/tabview

        lArgs = self.lArgs
        sDo = 'servings'
        #!WTF local variable '__doc__' referenced before assignment
        self.dhelp['servings'] = __doc__
        lArgs = self.lArgs

        # There's always a default provided of these
        oOm = oEnsureOmlette(self.ocmd2, oValues)
        oRecipe = oEnsureRecipe(self.ocmd2, oValues)
        oChefModule = oEnsureChef(self.ocmd2, oValues)

        if not hasattr(oOm, 'oBt') or not oOm.oBt:
            self.vError("You must use \"chef cook\" before you can have servings")
            return
        oBt = oOm.oBt

        # ['signals', 'trades', 'positions', 'equity', 'reviews', 'trade_price']
        _lCmds = oChefModule.lProducedServings[:]
        if tabview and tabview not in _lCmds: _lCmds += ['tabview']

        if len(lArgs) == 1 or lArgs[1] == 'list':
            self.poutput("Produced Servings: %r" % (oChefModule.lProducedServings,))
            return

        assert len(lArgs) > 1, "ERROR: argument required" +sDo +str(_lCmds)
        sCmd = lArgs[1]
        # self.vDebug("lProducedServings: " + repr(_lCmds))
        assert sCmd in _lCmds, "ERROR: %s %s not in %r" % (
            sDo, sCmd, _lCmds)

        oFd = sys.stdout
        # There's always a default provided of these
        oOm = oEnsureOmlette(self.ocmd2, oValues)
        oRecipe = oEnsureRecipe(self.ocmd2, oValues)
        oChefModule = oEnsureChef(self.ocmd2, oValues)

        ## oFun = getattr(self.ocmd2.oBt, sCmd)
        ## self.poutput(oFun())
        if sCmd == 'signals':
            # this was the same as: oBt._mSignals = bt.mSignals() or oBt.signals
            oOm.oBt._mSignals = oRecipe.mSignals(oOm.oBt)
            oFd.write('INFO:  bt.signals found: %d\n' % len(oOm.oBt.signals))
            oOm.vAppendHdf('recipe/servings/mSignals', oOm.oBt.signals)
            return

        if sCmd == 'trades':
            # this was the same as: oBt._mTrades =  oBt.mTrades() or oBt.trades
            oOm.oBt._mTrades = oRecipe.mTrades(oOm.oBt)
            oFd.write('INFO:  bt.trades found: %d\n' % len(oOm.oBt.trades))
            oOm.vAppendHdf('recipe/servings/mTrades', oOm.oBt.trades)
            return

        if sCmd == 'positions':
            # this was the same as: oBt._rPositions = oBt.rPositions() or oBt.positions
            oOm.oBt._rPositions = oRecipe.rPositions(oOm.oBt, init_pos=0)
            oFd.write('INFO:  bt.positions found: %d\n' % len(oOm.oBt.positions))
            oOm.vAppendHdf('recipe/servings/rPositions', oOm.oBt.positions)
            return

        if sCmd == 'equity':
            # this was the same as: oBt._rEquity = oBt.rEquity() or oBt.equity
            oOm.oBt._rEquity = oRecipe.rEquity(oOm.oBt)
            oFd.write('INFO:  bt.equity found: %d\n' % len(oOm.oBt.equity))
            oOm.vAppendHdf('recipe/servings/rEquity', oOm.oBt.equity)
            return

        if sCmd == 'trade_price':
            # oFd.write('INFO:  bt.rTradePrice() found: %d\n' % len(oBt.rTradePrice()))
            oFd.write('INFO:  bt.trade_price found: %d\n' % len(oOm.oBt.trade_price))
            oOm.vAppendHdf('recipe/servings/rTradePrice', oOm.oBt.trade_price)
            return

        if sCmd == 'metrics' or sCmd == 'reviews':
            oOm.vSetTitleHdf('recipe/servings', oOm.oChefModule.sChef)
            #? Leave this as derived or store it? reviews?
            oOm.vSetMetadataHdf('recipe/servings', oOm.oBt.dSummary())
            oFd.write(oOm.oBt.sSummary())
            return

        if tabview and sCmd == 'tabview':
            assert len(lArgs) > 2, "ERROR: " +sDo +" " +sCmd \
                   +": serving required, one of: reviews " +str(oChefModule.lProducedServings)

            sServing = lArgs[2]
            if sServing in ['metrics', 'reviews']:
                l = [['Metric', 'Value']]
                l += oOm.oBt.lSummary()
                l.sort()
                # , hdr_rows=lHdrRows
                tabview.view(l, column_width='max')
                return

            assert sServing in oChefModule.lProducedServings
            mDf = getattr(oOm.oBt, sServing)
            # FixMe: need index timestamp for mva
            tabview.view(mDf)
            return

        self.vError("Unrecognized servings command: " + str(lArgs) +'\n' +__doc__)
        return

    # Plot the servings the chef has cooked, using matplotlib
    LCOMMANDS += ['plot']
    def backtest_plot(self):
        """
==== OTCmd2 backtest plot

Plot the servings the chef has cooked, using matplotlib.
{{{
back plot show      - show the current plot
back plot trades    - plot the trades
back plot equity    - plot the cumulative equity
}}}
        """
        lArgs = self.lArgs
        sDo = 'plot'
        #!WTF local variable '__doc__' referenced before assignment
        self.dhelp['plot'] = __doc__
        lArgs = self.lArgs

        __doc__ = sBACplot__doc__
        _lCmds = ['show', 'trades', 'equity']
        if not hasattr(oOm, 'oBt') or not oOm.oBt:
            self.vError("You must use \"chef cook\" before you can plot")
            return
        # FixMe:
        oBt = oOm.oBt

        assert len(lArgs) > 1, "ERROR: " +sDo +str(_lCmds)
        sCmd = lArgs[1]
        assert sCmd in _lCmds, "ERROR: " +sDo +str(_lCmds)

        import matplotlib
        import matplotlib.pylab as pylab
        if sCmd == 'show':
            pylab.show()
            return

        # FixMe:
        matplotlib.rcParams['figure.figsize'] = (10, 5)

        if sCmd == 'equity':
            # FixMe: derive the period from the sTimeFrame
            sPeriod = 'W'
            close_label = 'C'
            mOhlc = oRecipe.dIngredients['mOhlc']
            oChefModule.vPlotEquity(oBt.equity, mOhlc, sTitle="%s\nEquity" % repr(oBt),
                                    sPeriod=sPeriod,
                                    close_label=close_label,
                                    )
            pylab.show()
            return

        if sCmd == 'trades':
            oBt.vPlotTrades()
            pylab.legend(loc='lower left')
            pylab.show()

            return
        self.vError("Unrecognized plot command: " + str(lArgs))
        return

    def bexecute(self, lArgs, oValues):
        """bexecute executes the backtest command.
        """
        self.lArgs = lArgs
        self.oValues = oValues

        # self.vassert_args(lArgs, LCOMMANDS, imin=1)
        if self.bis_help(lArgs):
            return

        sDo = lArgs[0]
        # An omlette is an HDF5 file that saves all the data from a backtest
        if sDo in ['omlette']:
            oMeth = getattr(self, 'backtest_' +sDo)
            oMeth()
            return

        if oValues.sRecipe:
            self.ocmd2.sRecipe = oValues.sRecipe
            self.poutput("DEBUG: backtest recipe from values: " + oValues.sRecipe)
        elif not hasattr(self.ocmd2, 'sRecipe') or not self.ocmd2.sRecipe:
            self.ocmd2.sRecipe = self.ocmd2.oConfig['backtest']['recipe']
            self.poutput("WARN: backtest recipe from config: " + self.ocmd2.sRecipe)
        if oValues.sChef:
            self.ocmd2.sChef = oValues.sChef
            self.poutput("DEBUG: backtest chef from values: " + oValues.sChef)
        elif not hasattr(self.ocmd2, 'sChef') or not self.ocmd2.sChef:
            self.ocmd2.sChef = self.ocmd2.oConfig['backtest']['chef']
            self.poutput("WARN: backtest chef from config: " + self.ocmd2.sChef)

        if sDo in ['feed', 'recipe', 'chef']:
            oMeth = getattr(self, 'backtest_' +sDo)
            oMeth()
            return

        # Set the chef that we will use, and cook from the ingredients and the feeds
        oOm = oEnsureOmlette(self.ocmd2, oValues)
        oRecipe = oEnsureRecipe(self.ocmd2, oValues)
        oChefModule = oEnsureChef(self.ocmd2, oValues)

        if sDo in ['servings', 'plot']:
            oMeth = getattr(self, 'backtest_' +sDo)
            try:
                oMeth()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                # This is still in the process of getting wired up and tested
                print(traceback.format_exc(10))
            return

        self.poutput("ERROR: Unrecognized backtest command: " + str(lArgs) +'\n' +__doc__)


def vDoBacktestCmd(self, lArgs, oValues):
    __doc__ = sBAC__doc__
