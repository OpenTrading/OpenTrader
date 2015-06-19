# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
"""

import sys
import os
from pprint import pprint, pformat

import tabview

from OTUtils import sStripCreole, lConfigToList
    
#? feed rename delete
sBAC__doc__ = """
Backtest recipes with chefs, and serve the results as metrics and plots.

The subcommands are:
* omlette   - An omlette is an HDF5 file that saves all the data from a backtest
* feed      - Create feeds (pandas DataFrames) from CSV OHLCV files
* recipe    - Set the recipe that the chef will use, and make the ingredients from the feeds
* chef      - Set the chef that we will use, and cook from the ingredients and the feeds
* servings  - List the servings the chef has cooked, and dish out the servings
* plot      - Plot the servings the chef has cooked, using matplotlib
"""

sBAComlette__doc__ = """
==== OTCmd2 backtest omlette

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
sBAC__doc__ += sBAComlette__doc__

sBACfeed__doc__ = """
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
sBAC__doc__ += sBACfeed__doc__

sBACrecipe__doc__ = """
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
sBAC__doc__ += sBACrecipe__doc__

sBACchef__doc__ = """
==== OTCmd2 backtest chef

Set the chef that we will use, and cook from the ingredients and the feeds.
{{{
back chef list                          - list the known chefs
back chef set                           - show the current chef
back chef set CHEF                      - set the current chef
back chef cook                          - cook the recipe by the chef
}}}
"""
sBAC__doc__ += sBACchef__doc__

sBACservings__doc__ = """
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
sBAC__doc__ += sBACservings__doc__

sBACplot__doc__ = """
==== OTCmd2 backtest plot

Plot the servings the chef has cooked, using matplotlib.
{{{
back plot show      - show the current plot
back plot trades    - plot the trades
back plot equity    - plot the cumulative equity
}}}
"""
sBAC__doc__ += sBACplot__doc__

dRunCache = {}

dFEED_CACHE = {}
sFEED_CACHE_KEY = ""

_sCurrentOmletteDir = ""
_oCurrentOmlette = None
_oCurrentRecipe = None
_oCurrentChef = None

def oEnsureOmlette(self, oOpts, sNewOmlette=""):
    from Omlettes import Omlette
    if not sNewOmlette and hasattr(self, 'oOm') and self.oOm:
        return self.oOm
    oOm = Omlette.Omlette(oFd=sys.stdout)
    if sNewOmlette:
        # The default is no HDF file - it's not in self.oOptions.sOmlette
        oOm.oAddHdfStore(sNewOmlette)
        
    self.oOm = oOm
    return oOm

def oEnsureRecipe(self, oOpts, sNewRecipe=""):
    oOm = oEnsureOmlette(self, oOpts)
    if not sNewRecipe and hasattr(oOm, 'oRecipe') and oOm.oRecipe:
        return oOm.oRecipe
    if not sNewRecipe:
        # The are set earlier in the call to do_back
        sNewRecipe = self.sRecipe
    if hasattr(oOm, 'oRecipe') and oOm.oRecipe:
        sOldName = oOm.oRecipe.sName
    else:
        sOldName = ""
    oRecipe = oOm.oAddRecipe(sNewRecipe)
    if sOldName and sOldName != sNewRecipe:        
        #? do we invalidate the current servings if the recipe changed?
        vClearOven(self, oOpts)
    return oRecipe

def oEnsureChef(self, oOpts, sNewChef=""):
    oOm = oEnsureOmlette(self, oOpts)
    if not sNewChef and hasattr(oOm, 'oChefModule') and oOm.oChefModule:
        return oOm.oChefModule
    if not sNewChef:
        # The are set earlier in the call to do_back
        sNewChef = self.sChef
    if hasattr(oOm, 'oChefModule') and oOm.oChefModule and oOm.oChefModule.sChef:
        sOldName = oOm.oChefModule.sChef
    else:
        sOldName = ""
    oChefModule = oOm.oAddChef(sNewChef)
    if sOldName and sOldName != sNewChef:
	#? do we invalidate the current servings if the chef changed?
        vClearOven(self, oOpts)
    return oOm.oChefModule

def vClearOven(self, oOpts):
    oOm = oEnsureOmlette(self, oOpts)
    oOm.oBt = None
    
def vDoBacktestCmd(self, oArgs, oOpts=None):
    __doc__ = sBAC__doc__
    global dFEED_CACHE
    global sFEED_CACHE_KEY

    lArgs = oArgs.split()
    sDo = lArgs[0]
    
    # An omlette is an HDF5 file that saves all the data from a backtest
    if sDo == 'omlette':
        # is this a backtest command or should it move up
        # leave it here for now, and move it up later
        __doc__ = sBAComlette__doc__
        
        global _sCurrentOmletteDir
        # ingredients recipe dish
        # plot sSection
        # 
        _lCmds = ['load', 'open', 'check', 'save', 'close', 'display']
        assert len(lArgs) > 1, "ERROR: " +sDo +" " +str(_lCmds)
        sCmd = lArgs[1]
        assert sCmd in _lCmds, "ERROR: " +sDo +" " +str(_lCmds)
        
        oOm = oEnsureOmlette(self, oOpts, sNewOmlette="")
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
            self.oOm.vClose()
            return
        
        assert len(lArgs) >= 3, \
               "ERROR: " +sDo +" " +sCmd +" " +" FILENAME"
        sFile = lArgs[2]
        
        if sCmd == 'open':
            o = oOm.oAddHdfStore(sFile)
            assert o is not None and oOm.oHdfStore is not None
            _sCurrentOmletteDir = os.path.dirname(sFile)
            return

        if sCmd == 'load':
            assert os.path.isfile(sFile), \
                   "ERROR: " +sDo +" " +sCmd +" file not found " +sFile
            _sCurrentOmletteDir = os.path.dirname(sFile)
            raise RuntimeError(NotImplemented)
            return

        self.vError("Unrecognized omlette command: " + str(oArgs) +'\n' +__doc__)
        return

    # Create feeds (pandas DataFrames) from CSV OHLCV files
    if sDo == 'feed':
        __doc__ = sBACfeed__doc__
        #? rename delete
        _lCmds = ['dir', 'list', 'get', 'set',
                  'read_mt4_csv', 'read_yahoo_csv', 'info', 'plot', 'to_hdf']
        assert len(lArgs) > 1, "ERROR: " +sDo +" " +str(_lCmds)
        sCmd = lArgs[1]
        assert lArgs[1] in _lCmds, "ERROR: " +sDo +" " +str(_lCmds)
        
        if sCmd == 'dir':
            if len(lArgs) == 2:
                if not self.oConfig['feed']['sHistoryDir']:
                    self.poutput("No default history directory set: use \"feed dir dir\"")
                elif not os.path.isdir(self.oConfig['feed']['sHistoryDir']):
                    self.poutput("History directory not found: use \"feed dir dir\": " + \
                                 self.oConfig['feed']['sHistoryDir'])
                else:
                    self.poutput("Default history directory: " + \
                                 self.oConfig['feed']['sHistoryDir'])
                return
            
            sDir = lArgs[2]
            assert os.path.isdir(sDir)
            self.oConfig['feed']['sHistoryDir'] = sDir
            return
        
        if sCmd == 'read_mt4_csv':
            from PandasMt4 import oReadMt4Csv
            assert len(lArgs) >= 3, \
                   "ERROR: " +sDo +" " +sCmd +" FILENAME [SYMBOL TIMEFRAME YEAR]"
            sFile = lArgs[2]
            if not os.path.isfile(sFile):
                sHistoryDir = os.path.join(self.oOptions.sMt4Dir, 'history')
                assert os.path.isdir(sHistoryDir)
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
            oOm = oEnsureOmlette(self, oOpts)
            _dCurrentFeedFrame = oOm.dGetFeedFrame(sFile,
                                                   sTimeFrame,
                                                   sSymbol,
                                                   sYear)
            from PandasMt4 import oReadMt4Csv, oPreprocessOhlc, vResampleFiles
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

        _dPlotParams = self.oConfig['feed.plot.params']

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
            import numpy as np
            from OTPpnAmgc import vGraphData
            if 'matplotlib.rcParams' in self.oConfig:
                for sKey, gVal in self.oConfig['matplotlib.rcParams'].items():
                    matplotlib.rcParams[sKey] = gVal

            from OTBackTest import oPreprocessOhlc
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

        self.vError("Unrecognized feed command: " + str(oArgs) +'\n' +__doc__)
        return

    # Set the recipe that the chef will use, and make the ingredients from the feeds
    if sDo == 'recipe':
        __doc__ = sBACrecipe__doc__
        from .Omlettes import lKnownRecipes
        # self.vDebug("lKnownRecipes: " + repr(lKnownRecipes))
        # are ingredients under chef?
        _lCmds = ['set', 'list', 'get', 'make', 'ingredients', 'config']
        
        sCmd = str(lArgs[1])
        if sCmd == 'list':
            self.poutput("Known Recipes: %r" % (self.G(lKnownRecipes,)))
            return

        if sCmd == 'get' or (sCmd == 'set' and len(lArgs) == 2):
            self.poutput("Current Recipe: %s" % (self.sRecipe,))
            return

        assert len(lArgs) > 1, "ERROR: not enough args: " +sDo +str(_lCmds)
        assert sCmd in _lCmds, "ERROR: %s %s not in: %r " % (
            sDo, sCmd, _lCmds)

        
        if sCmd == 'config':
            oRecipe = oEnsureRecipe(self, oOpts)
            self.vConfigOp(lArgs, oRecipe.oConfig)
            return
        
        if sCmd == 'set':
            assert len(lArgs) > 2, \
                   "ERROR: %s %s requires one of: %s" % (
                sDo, sCmd, '|'.join(lKnownRecipes))
            sNewRecipe = str(lArgs[2])
            assert sNewRecipe in lKnownRecipes, \
                   "ERROR: %s %s %s not in: %s" % (
                sDo, sCmd, sNewRecipe, '|'.join(lKnownRecipes))
            if self.sRecipe != sNewRecipe:
                self.sRecipe = sNewRecipe
                oRecipe = oEnsureRecipe(self, oOpts, sNewRecipe=sNewRecipe)
            #? do we update the config file? - I think not
            #? self.oConfig['backtest']['sRecipe'] = sNewRecipe
            return

        # The following all require that a feed has been loaded
        assert sFEED_CACHE_KEY
        assert sFEED_CACHE_KEY in dFEED_CACHE
        _dCurrentFeedFrame = dFEED_CACHE[sFEED_CACHE_KEY]
        assert _dCurrentFeedFrame
        if sCmd == 'make' or sCmd == 'ingredients':
            assert _dCurrentFeedFrame
            oRecipe = oEnsureRecipe(self, oOpts)
            # ugly
            dFeedParams = _dCurrentFeedFrame
            mFeedOhlc = _dCurrentFeedFrame['mFeedOhlc']
            dFeeds = dict(mFeedOhlc=mFeedOhlc, dFeedParams=dFeedParams)

            oRecipe.dMakeIngredients(dFeeds)
            assert oRecipe.dIngredients
            return
        
        self.vError("Unrecognized recipe command: " + str(oArgs) +'\n' +__doc__)
        return

    # Set the chef that we will use, and cook from the ingredients and the feeds
    if sDo == 'chef':
        __doc__ = sBACchef__doc__
        from .Omlettes import lKnownChefs
        # self.vDebug("lKnownChefs: " + repr(lKnownChefs))

        _lCmds = ['get', 'set', 'list', 'cook']
        assert len(lArgs) > 1, "ERROR: not enough args: " +sDo +str(_lCmds)
        sCmd = lArgs[1]
        
        if sCmd == 'list':
            self.poutput("Known Chefs: %r" % (lKnownChefs,))
            return

        if sCmd == 'get' or (sCmd == 'set' and len(lArgs) == 2):
            self.poutput("Current Chef: %s" % (self.sChef,))
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
            if self.sChef != sNewChef:
                self.sChef = sNewChef
                oChef = oEnsureChef(self, oOpts, sNewChef=sNewChef)
            #? do we update the config file? - I think not
            #? self.oConfig['backtest']['sChef'] = sNewChef
            return

        # The following all require that a feed has been loaded
        assert sFEED_CACHE_KEY
        assert sFEED_CACHE_KEY in dFEED_CACHE
        _dCurrentFeedFrame = dFEED_CACHE[sFEED_CACHE_KEY]
        assert _dCurrentFeedFrame
        
        # There's always a default provided of these
        oOm = oEnsureOmlette(self, oOpts)
        oRecipe = oEnsureRecipe(self, oOpts)
        oChefModule = oEnsureChef(self, oOpts)

        if sCmd == 'cook':
            from .OTBackTest import oPyBacktestCook
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
        
        self.vError("Unrecognized chef command: " + str(oArgs) +'\n' +__doc__)
        return

    oOm = oEnsureOmlette(self, oOpts)
    oRecipe = oEnsureRecipe(self, oOpts)
    oChefModule = oEnsureChef(self, oOpts)

    # List the servings the chef has cooked, and dish out the servings
    if sDo == 'servings':
        __doc__ = sBACservings__doc__
        if not hasattr(oOm, 'oBt') or not oOm.oBt:
            self.vError("You must use \"chef cook\" before you can have servings")
            return
        oBt = oOm.oBt

        # ['signals', 'trades', 'positions', 'equity', 'reviews', 'trade_price']
        _lCmds = oChefModule.lProducedServings[:]
        if tabview not in _lCmds: _lCmds += ['tabview']
        
        if len(lArgs) == 1 or lArgs[1] == 'list':
            self.poutput("Produced Servings: %r" % (oChefModule.lProducedServings,))
            return

        assert len(lArgs) > 1, "ERROR: argument required" +sDo +str(_lCmds)
        sCmd = lArgs[1]
        # self.vDebug("lProducedServings: " + repr(_lCmds))
        assert sCmd in _lCmds, "ERROR: %s %s not in %r" % (
            sDo, sCmd, _lCmds)

        oFd = sys.stdout
        ## oFun = getattr(self.oBt, sCmd)
        ## self.poutput(oFun())
        if sCmd == 'signals':
            # this was the same as: oBt._mSignals = bt.mSignals() or oBt.signals
            oBt._mSignals = oRecipe.mSignals(oBt)
            oFd.write('INFO:  bt.signals found: %d\n' % len(oBt.signals))
            oOm.vAppendHdf('recipe/servings/mSignals', oBt.signals)
            return
            
        if sCmd == 'trades':
            # this was the same as: oBt._mTrades =  oBt.mTrades() or oBt.trades
            oBt._mTrades = oRecipe.mTrades(oBt)
            oFd.write('INFO:  bt.trades found: %d\n' % len(oBt.trades))
            oOm.vAppendHdf('recipe/servings/mTrades', oBt.trades)
            return
            
        if sCmd == 'positions':
            # this was the same as: oBt._rPositions = oBt.rPositions() or oBt.positions
            oBt._rPositions = oRecipe.rPositions(oBt, init_pos=0)
            oFd.write('INFO:  bt.positions found: %d\n' % len(oBt.positions))
            oOm.vAppendHdf('recipe/servings/rPositions', oBt.positions)
            return
            
        if sCmd == 'equity':
            # this was the same as: oBt._rEquity = oBt.rEquity() or oBt.equity
            oBt._rEquity = oRecipe.rEquity(oBt)
            oFd.write('INFO:  bt.equity found: %d\n' % len(oBt.equity))
            oOm.vAppendHdf('recipe/servings/rEquity', oBt.equity)
            return
            
        if sCmd == 'trade_price':
            # oFd.write('INFO:  bt.rTradePrice() found: %d\n' % len(oBt.rTradePrice()))
            oFd.write('INFO:  bt.trade_price found: %d\n' % len(oBt.trade_price))
            oOm.vAppendHdf('recipe/servings/rTradePrice', oBt.trade_price)
            return
            
        if sCmd == 'metrics' or sCmd == 'reviews':
            oOm.vSetTitleHdf('recipe/servings', oOm.oChefModule.sChef)
            #? Leave this as derived or store it? reviews?
            oOm.vSetMetadataHdf('recipe/servings', oBt.dSummary())
            oFd.write(oBt.sSummary())
            return

        if tabview and sCmd == 'tabview':
            assert len(lArgs) > 2, "ERROR: " +sDo +" " +sCmd \
                   +": serving required, one of: reviews " +str(oChefModule.lProducedServings)
            
            sServing = lArgs[2]
            if sServing in ['metrics','reviews']:
                l = [['Metric', 'Value']]
                l += oBt.lSummary()
                l.sort()
                # , hdr_rows=lHdrRows
                tabview.view(l, column_width='max')
                return

            assert sServing in oChefModule.lProducedServings
            mDf = getattr(oBt, sServing)
            # FixMe: need index timestamp for mva 
            tabview.view(mDf)
            return
                         
        self.vError("Unrecognized servings command: " + str(oArgs) +'\n' +__doc__)
        return

    # Plot the servings the chef has cooked, using matplotlib
    if sDo == 'plot':
        __doc__ = sBACplot__doc__
        _lCmds = ['show', 'trades', 'equity']
        if not hasattr(oOm, 'oBt') or not oOm.oBt:
            self.vError("You must use \"chef cook\" before you can plot")
            return
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
            sPeriod='W'
            close_label='C'
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
        self.vError("Unrecognized plot command: " + str(oArgs) +"\n" + sBAC__doc__)
        return

    self.vError("Unrecognized backtest command: " + str(oArgs) +"\n" + sBAC__doc__)

