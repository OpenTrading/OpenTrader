# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
"""

import sys
import os
import collections
from pybacktest.data import load_from_yahoo

#? feed rename delete
sBAC__doc__ = ""
sBACfeed__doc__ = """
back feed dir
back feed dir dirname

back feed read_mt4_csv SYMBOL TIMEFRAME [YEAR]
back feed read_yahoo_csv SYMBOL [STARTYEAR]
back feed info
back feed plot
"""
sBAC__doc__ += sBACfeed__doc__

sBACrecipe__doc__ = """
back recipe list                                 - list the known recipes
back recipe set                                  - show the current recipe
back recipe set RECIPE                           - set the current recipe
"""
sBAC__doc__ += sBACrecipe__doc__

sBACchef__doc__ = """
back chef list                                   - list the known chefs
back chef set                                    - show the current chef
back chef set CHEF                               - set the current chef
back chef cook
"""
sBAC__doc__ += sBACchef__doc__

sBACservings__doc__ = """
back servings list                               - list the servings
back servings signals
back servings trades
back servings positions
back servings equity
back servings summary
"""
sBAC__doc__ += sBACservings__doc__

sBACplot__doc__ = """
back plot show
back plot set
back plot trades
back plot equity
"""
sBAC__doc__ += sBACplot__doc__

dDF_CACHE = {}
dRunCache = {}

_sCurrentOmletteDir = ""
_dCurrentFeed = None
_oCurrentOmlette = None
_oCurrentRecipe = None
_oCurrentChef = None

def oEnsureOmlette(self, oOpts, sNewOmlette=""):
    from Omlettes import Omlette
    if not sNewOmlette and hasattr(self, 'oOm') and \
       self.oOm:
        return self.oOm
    if not sNewOmlette:
        # The default is no HDF file - it's not in self.oOptions.sOmlette
        pass
    oOm = Omlette.Omlette(sHdfStore=sNewOmlette, oFd=sys.stdout)
    self.oOm = oOm
    return oOm

def oEnsureRecipe(self, oOpts, sNewRecipe=""):
    oOm = oEnsureOmlette(self, oOpts)
    if not sNewRecipe and hasattr(oOm, 'oRecipe') and oOm.oRecipe:
        return oOm.oRecipe
    if not sNewRecipe:
        # The are set earlier in the call to do_back
        sNewRecipe = self.sRecipe
    if oOm.oRecipe.sName and oOm.oRecipe.sName != sNewRecipe:
        #? do we invalidate the current servings if the recipe changed?
        oClearOven(self)
    oRecipe = oOm.oAddRecipe(sNewRecipe)
    return oOm.oRecipe

def oEnsureChef(self, oOpts, sNewChef=""):
    oOm = oEnsureOmlette(self, oOpts)
    if not sNewChef and hasattr(oOm, 'oChefModule') and oOm.oChefModule:
        return oOm.oChefModule
    if not sNewChef:
        # The are set earlier in the call to do_back
        sNewChef = self.sChef
    if oOm.oChefModule.sChef and oOm.oChefModule.sChef != sNewChef:
	#? do we invalidate the current servings if the chef changed?
        oClearOven(self)
    oChefModule = oOm.oAddChef(sNewChef)
    return oOm.oChefModule

def oClearOven(self):
    pass

def vDoBacktestCmd(self, oArgs, oOpts=None):
    __doc__ = sBAC__doc__
    
    global _dCurrentFeed
    
    # begin end
    _sCurrentFeedDir = '/t/Program Files/HotForex MetaTrader/history/tools.fxdd.com'
    _dPlotParams = collections.OrderedDict(
        iShortSMA=10,
        iLongSMA=50,
        iRsiUpper=70,
        iRsiLower=30,
        iMacdSlow=26,
        iMacdFast=12,
        iMacdEma=9,
        bUseTalib=False,
        )

    
    
    lArgs = oArgs.split()
    if lArgs[0] == 'omlette':
        global _sCurrentOmletteDir
        # ingredients recipe dish
        _lCmds = ['load', 'check', 'save', 'display']
        assert len(lArgs) > 1, "ERROR: " +lArgs[0] +" " +str(_lCmds)
        assert lArgs[1] in _lCmds, "ERROR: " +lArgs[0] +" " +str(_lCmds)
        if lArgs[1] == 'check':
            return
        if lArgs[1] == 'display':
            return
        assert len(lArgs) >= 3, \
               "ERROR: " +lArgs[0] +" " +lArgs[1] +" " +" filename"
        sFile = lArgs[2]
        if not os.path.exists(os.path.dirname(sFile)) and \
               os.path.exists(_sCurrentOmletteDir):
            # FixxME: check relative
            s = os.path.join(_sCurrentOmletteDir, sFile)
            if os.path.exists(s): sFile = s
        if lArgs[1] == 'load':
            assert os.path.isfile(sFile), \
                   "ERROR: " +lArgs[0] +" " +lArgs[1] +" file not found " +sFile
            _sCurrentOmletteDir = os.path.dirname(sFile)
            return
        if lArgs[1] == 'save':
            _sCurrentOmletteDir = os.path.dirname(sFile)
            return
        
        self.vError("Unrecognized omlette command: " + str(oArgs) +'\n' +__doc__)
        return
    
    if lArgs[0] == 'feed':
        __doc__ = sBACfeed__doc__
        #? rename delete
        _lCmds = ['dir', 'read_mt4_csv', 'read_yahoo_csv', 'info', 'plot', 'to_hdf']
        assert len(lArgs) > 1, "ERROR: " +lArgs[0] +" " +str(_lCmds)
        assert lArgs[1] in _lCmds, "ERROR: " +lArgs[0] +" " +str(_lCmds)
        if lArgs[1] == 'dir':
            from OTBackTest import oReadMt4Csv
            if len(lArgs) == 2:
                if not _sCurrentFeedDir:
                    self.poutput("No default history directory set: use \"feed dir dir\"")
                else:
                    self.poutput("Default history directory: " + _sCurrentFeedDir)
                return
            sDir = lArgs[2]
            assert os.path.isdir(sDir)
            _sCurrentFeedDir = sDir
            return
        if lArgs[1] == 'read_mt4_csv':
            from OTBackTest import oReadMt4Csv
            if False:
                assert len(lArgs) >= 4, \
                       "ERROR: " +lArgs[0] +" " +lArgs[1] +" SYMBOL TIMEFRAME [YEAR]"
                sSymbol = lArgs[2] # 'EURGBP'
                sTimeframe = lArgs[3] # '1440'
                if len(lArgs) > 4:
                    sYear = lArgs[4] # '2014'
                else:
                    sYear = ""
                sFile = os.path.join(_sCurrentFeedDir, sSymbol + sTimeframe +'-' +sYear +'.csv')
                assert os.path.isfile(sFile)
            else:
                assert len(lArgs) >= 3, \
                       "ERROR: " +lArgs[0] +" " +lArgs[1] +" filename [SYMBOL TIMEFRAME YEAR]"
                sFile = lArgs[2]
                if not os.path.exists(os.path.dirname(sFile)) and \
                       os.path.exists(_sCurrentFeedDir):
                    # FixxME: check relative
                    s = os.path.join(_sCurrentFeedDir, sFile)
                    if os.path.exists(s): sFile = s
                assert os.path.isfile(sFile), \
                       "ERROR: " +lArgs[0] +" " +lArgs[1] +" file not found " +sFile
                if len(lArgs) > 5:
                    sSymbol= lArgs[3]
                    sTimeframe = lArgs[4]
                    sYear = lArgs[5]
                else:
                    lCooked = os.path.split(sFile)[-1].split('.')[0].split('-')
                    if len(lCooked) > 1:
                        sYear = lCooked[-1]
                    else:
                        sYear = ""
                    sSymbol = lCooked[0][:6]
                    sTimeframe = lCooked[0][6:]
                
                self.vDebug(lArgs[0] +" " +lArgs[1] +" " + \
                           "sSymbol=" +sSymbol \
                           +", sYear=" +sYear \
                           +", sTimeframe=" +sTimeframe)
            
            tOhlc = oReadMt4Csv(sFile, sTimeframe, sSymbol, sYear="")
            assert tOhlc is not None, "oReadMt4Csv failed on " + sFile
            tOhlc.info(True, sys.stdout)

            # NaturalNameWarning: object name is not a valid Python identifier: 'Mt4_csv|EURUSD|1440|2014'; it does not match the pattern ``^[a-zA-Z_][a-zA-Z0-9_]*$``;
            sKey = 'Mt4_csv' +'_' +sSymbol +'_' +sTimeframe +'_' +sYear
            global _dCurrentFeed
            _dCurrentFeed = collections.OrderedDict(
                sSymbol=sSymbol,
                sTimeframe=sTimeframe,
                sKey=sKey,
                sFile=sFile,
                tOhlc=tOhlc,
                _dPlotParams=_dPlotParams,
                )
            return
        
        # The following all require that a feed has been loaded
        if _dCurrentFeed is None:
            self.vError("Run \"back read_*\" first to read a DataFrame")
            return
        sSymbol = _dCurrentFeed['sSymbol']
        sKey = _dCurrentFeed['sKey']
        sTimeframe = _dCurrentFeed['sTimeframe']
        tOhlc = _dCurrentFeed['tOhlc']
        _dPlotParams = _dCurrentFeed['_dPlotParams']
        
        if lArgs[1] in ['to_hdf']:
            """ DataFrame.to_hdf(path_or_buf, key, **kwargs)
            activate the HDFStore
            Parameters :
              path_or_buf : the path (string) or buffer to put the store
              key : string indentifier for the group in the store
              """
            
            assert len(lArgs) >= 3, \
                   "ERROR: " +lArgs[0] +" " +lArgs[1] +" fixed|table filename"
            sType = lArgs[2]
            assert sType in ['fixed', 'table']
            sFile = lArgs[3]
            # FixME: if absolute assert os.path.exists(os.path.dirname(sFile))
            #? lArgs[4:] -> **kw ?
            vRetval = tOhlc.to_hdf(sFile, sKey, format=sType)
            return
        
        if lArgs[1] == 'info':
            """ Concise summary of a DataFrame.
            Parameters :
            verbose : boolean, default True
                    If False, don’t print column count summary
            buf : writable buffer, defaults to sys.stdout
            """
            import yaml
            
            tOhlc.info(True, sys.stdout)
            
            s = '|  %s  |' % ("Plot Params",)
            self.poutput('-' * len(s))
            self.poutput(s)
            self.poutput('-' * len(s), '\n')
            self.poutput(repr(_dPlotParams))
            # yaml.dump(, allow_unicode=True, default_flow_style=False))
            self.poutput('-' * len(s))
            return

        # 'download_hst_zip'
        if lArgs[1] == 'plot':
            import matplotlib
            import numpy as np
            from PpnAmgcTut import vGraphData
            if 'matplotlib.rcParams' in self.oConfig:
                for sKey, gVal in self.oConfig['matplotlib.rcParams'].items():
                    matplotlib.rcParams[sKey] = gVal
                        
            from OTBackTest import oPreprocessOhlc
            tOhlc = oPreprocessOhlc(tOhlc)
            # (Pdb) pandas.tseries.converter._dt_to_float_ordinal(tOhlc.index)[0]
            # 735235.33333333337
            nDates = matplotlib.dates.date2num(tOhlc.index.to_pydatetime())
            nVolume = 1000*np.random.normal(size=len(tOhlc))

            self.vWarn("This may take minutes to display depending on your computer's speed")
            vGraphData(sSymbol, nDates,
                       tOhlc.C.values, tOhlc.H.values, tOhlc.L.values, tOhlc.O.values,
                       nVolume,
                       **_dPlotParams)
            
        return
            
    if lArgs[0] == 'recipe':
        __doc__ = sBACrecipe__doc__
        from .Omlettes import lKnownRecipes
        # self.vDebug("lKnownRecipes: " + repr(lKnownRecipes))
        
        _lCmds = ['set', 'list']
        
        sCmd = str(lArgs[1])
        if sCmd == 'list':
            self.poutput("Known Recipes: %r" % (lKnownRecipes,))
            return
        
        if sCmd == 'get' or (sCmd == 'set' and len(lArgs) == 2):
            self.poutput("Current Recipe: %s" % (self.sRecipe,))
            return
        
        assert len(lArgs) > 1, "ERROR: not enough args: " +lArgs[0] +str(_lCmds)
        assert sCmd in _lCmds, "ERROR: not in: " +lArgs[0] +str(_lCmds)
        
        if sCmd == 'set':
            assert len(lArgs) > 2, \
                   "ERROR: %s %s requires one of: %s" % (
                lArgs[0], sCmd, '|'.join(lKnownRecipes))
            sNewRecipe = str(lArgs[2])
            assert sNewRecipe in lKnownRecipes, \
                   "ERROR: %s %s %s not in: %s" % (
                lArgs[0], sCmd, sNewRecipe, '|'.join(lKnownRecipes))
            if self.sRecipe != sNewRecipe:
                self.sRecipe = sNewRecipe
                oRecipe = oEnsureRecipe(self, oOpts, sNewRecipe=sNewRecipe)
            #? do we update the config file? - I think not
            #? self.oConfig['backtest']['sRecipe'] = sNewRecipe
            return
        
        return
    
    if lArgs[0] == 'chef':
        __doc__ = sBACchef__doc__
        from .Omlettes import lKnownChefs
        # self.vDebug("lKnownChefs: " + repr(lKnownChefs))
        
        _lCmds = ['set', 'list', 'cook']        
        sCmd = lArgs[1]
        if sCmd == 'list':
            self.poutput("Known Chefs: %r" % (lKnownChefs,))
            return
        
        if sCmd == 'get' or (sCmd == 'set' and len(lArgs) == 2):
            self.poutput("Current Chef: %s" % (self.sChef,))
            return
        
        assert len(lArgs) > 1, "ERROR: not enough args: " +lArgs[0] +str(_lCmds)
        assert sCmd in _lCmds, "ERROR: not in: " +lArgs[0] +str(_lCmds)
        
        if sCmd == 'set':
            assert len(lArgs) > 2, \
                   "ERROR: %s %s %s one of: %s" % (
                lArgs[0], sCmd, '|'.join(lKnownChefs))
            sNewChef = str(lArgs[2])
            assert sNewChef in lKnownChefs, \
                   "ERROR: %s %s %s not in: %s" % (
                lArgs[0], sCmd, sNewChef, '|'.join(lKnownChefs))
            if self.sChef != sNewChef:
                self.sChef = sNewChef
                oChef = oEnsureChef(self, oOpts, sNewChef=sNewChef)
            #? do we update the config file? - I think not
            #? self.oConfig['backtest']['sChef'] = sNewChef
            return
        
        # need feed
        # There's always a default provided of these
        oOm = oEnsureOmlette(self, oOpts)
        oRecipe = oEnsureRecipe(self, oOpts)
        oChefModule = oEnsureChef(self, oOpts)

        if sCmd == 'cook':
            from .OTBackTest import oPyBacktestCook
            # assert oRecipe.dIngredients
            ## oBt = oPyBacktestCook(dFeeds, oRecipe, oChefModule, oOm)
            ## assert oBt is not None
            ## if type(oBt) == str:
            ##     raise RuntimeError(oBt)
            pass
        return
    
    if lArgs[0] == 'servings':
        __doc__ = sBACservings__doc__
        oChefModule = oEnsureChef(self, oOpts)
        # ['signals', 'trades', 'positions', 'equity', 'summary', 'display']
        _lCmds = oChefModule.lProducedServings
        if sCmd == 'list':
            self.poutput("Produced Servings: %r" % (_lCmds,))
            return
        
        self.vDebug("lProducedServings: " + repr(_lCmds))        
        assert len(lArgs) > 1, "ERROR: " +lArgs[0] +str(_lCmds)
        sCmd = lArgs[1]
        assert sCmd in _lCmds, "ERROR: " +lArgs[0] +str(_lCmds)
        
        oFun = getattr(self.oBt, sCmd)
        self.poutput(oFun())
        return
    
    if lArgs[0] == 'plot':
        __doc__ = sBACplot__doc__
        _lCmds = ['show', 'set', 'trades', 'equity']
        assert len(lArgs) > 1, "ERROR: " +lArgs[0] +str(_lCmds)
        sCmd = lArgs[1]
        assert sCmd in _lCmds, "ERROR: " +lArgs[0] +str(_lCmds)
        
        import matplotlib.pylab as pylab
        if sCmd == 'show':
            pylab.show()
            return
        if sCmd == 'set':
            #?
            pylab.show()
            return

        assert len(lArgs) > 1, "ERROR: " +lArgs[0] +str(_lCmds)
        sCmd = lArgs[1]
        assert sCmd in _lCmds, "ERROR: " +lArgs[0] +str(_lCmds)
        oFun = getattr(self.oBt, 'plot_' + sCmd)
        oFun()
        pylab.show()
        return
    
    self.vError("Unrecognized backtest command: " + str(oArgs) +"\n" + sBAC__doc__)
    
