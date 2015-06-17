# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
"""

import sys, os
import datetime
import pandas

from Recipe import Recipe

class SMARecipe(Recipe):
        
    #? should oOm be required?
    def __init__(self, oOm=None, oFd=sys.stdout):
        Recipe.__init__(self, oOm, oFd)
        self.__fVersion__ = 1.0
        self.sIniFile = 'SMARecipe.ini'
        self.sFile = __file__

    # make this a property>
    def oEnsureConfigObj(self):
        """
        oEnsureConfigObj ensures that the .ini file has been read.
        For each recipe, an .ini file is now required and is relied on.
        It's only read once, and is stored as self.oConfigObj
        """
        if self.oConfigObj is not None:
            return self.oConfigObj
        self.vReadIniFile()
        assert self.oConfigObj is not None
        return self.oConfigObj
    
    def dMakeIngredients(self, dFeeds):
        """
        dMakeIngredients takes a dictionary of feeds dFeeds
        with at least one key from lRequiredFeeds to work on.
        It returns a dictionary of ingredients with the keys in lRequiredIngredients
        and a copy of the config  that it used as the key dIngredientsConfig.
        """
        oC = self.oEnsureConfigObj()
        assert oC is not None
        iLongMa = oC['rLongMa']['iLongMa']
        iShortMa = oC['rShortMa']['iShortMa']
        bUseTalib = oC['rShortMa']['bUseTalib']

        self.vCheckRequiredFeeds(dFeeds)
        mFeedOhlc = dFeeds['mFeedOhlc']
        
        iBeginValid = max(iLongMa, iShortMa)-1
        iEndOhlc = len(mFeedOhlc)

        if bUseTalib:
            import talib
            aShortMA = talib.SMA(mFeedOhlc.O.values, timeperiod=iShortMa)
            aLongMA = talib.SMA(mFeedOhlc.O.values, timeperiod=iLongMa)
            rShortMa = pandas.Series(aShortMA, name='O',
                                     index=mFeedOhlc.O.index)
            rLongMa = pandas.Series(aLongMA, name='O',
                                    index=mFeedOhlc.O.index)
        else:
            rShortMa = pandas.rolling_mean(mFeedOhlc.O, iShortMa)
            rLongMa = pandas.rolling_mean(mFeedOhlc.O, iLongMa)

        rShortMa = rShortMa[iBeginValid:]
        rLongMa = rLongMa[iBeginValid:]
        mOhlc = mFeedOhlc[iBeginValid:]
        self.oOm.vAppendHdf('recipe/ingredients/rShortMa', rShortMa)
        self.oOm.vAppendHdf('recipe/ingredients/rLongMa', rLongMa)
        self.dIngredients = dict(rShortMa=rShortMa, rLongMa=rLongMa,
                                 mOhlc=mOhlc,
                                 dIngredientsConfig=dict(oC))
        return self.dIngredients
    
    def dApplyRecipe(self):
        """dApplyRecipe
        returns a dictionary with keys rBuy, rCover, rSell, rShort,
        which are pandas timeseries 
        and a copy of the dDishesParams.
        """
        #? copy this
        dDishesParams = self.dIngredients
        self.vCheckRequiredDishes(dDishesParams)
        rShortMa = dDishesParams['rShortMa']
        rLongMa = dDishesParams['rLongMa']
        
        assert isinstance(rShortMa, pandas.Series) and len(rShortMa)
        assert isinstance(rLongMa, pandas.Series) and len(rLongMa)

        sys.stdout.write('>  Data MA length %d\n' % len(rShortMa))
        sys.stdout.write('>  Date from: %s to: %s\n' % ( str(rShortMa.index[0]), str(rShortMa.index[-1]),))

        rBuy = rCover = (rShortMa > rLongMa) & (rShortMa.shift() < rLongMa.shift())  # ma cross up
        rSell = rShort = (rShortMa < rLongMa) & (rShortMa.shift() > rLongMa.shift())  # ma cross down
        # maybe one day
        dDishesParams = dict()
        return dict(rBuy=rBuy, rCover=rCover, rSell=rSell, rShort=rShort,
                    dDishesParams=dDishesParams)

