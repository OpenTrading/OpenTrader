# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
"""

import sys, os
import datetime
from collections import OrderedDict
import pandas

from Recipe import Recipe

class SMARecipe(Recipe):
    
    sName = 'SMACross'
    # There will always be at least one Feed Dataframe that is required
    # but you could have more: multi-equity, multi-timeframe...
    lRequiredFeeds = [dict(mFeedOhlc=dict(lNames=['T', 'O', 'H', 'L', 'C'],
                                          sPandasType='DataFrame',)),]
    lRequiredIngredients = [dict(rShortMa=dict(iShortMa=50, bUseTalib=True,
                                               sPandasType='Series',)),
                            dict(rLongMa=dict(iLongMa=200, bUseTalib=True,
                                              sPandasType='Series',))]
    sIniFile = 'SMARecipe.ini'
    
    __fVersion__ = 1.0
    #? should oOm be required?
    def __init__(self, oOm=None, oFd=sys.stdout):
        Recipe.__init__(self, oOm)
        self.sFile = __file__
        self.oFd = oFd
        self.zReadIniFile()

    def dMakeIngredients(self, dFeeds, dIngredientsParams):
        """dMakeIngredients takes a dictionary of feeds dFeeds
        with at least one key from lRequiredFeeds to work on.
        It returns a dictionary of ingredients with the keys in lRequiredIngredients
        and a key to the dIngredientsParams that it used.
        """
        oC = self.oConfigObj
        iLongMa = dIngredientsParams.get('iLongMa',
                                         int(oC['rLongMa']['iLongMa']))
        iShortMa = dIngredientsParams.get('iShortMa',
                                          int(oC['rShortMa']['iShortMa']))
        bUseTalib = dIngredientsParams.get('bUseTalib',
                                           bool(oC['rShortMa']['bUseTalib']))

        self.vCheckRequiredFeeds(dFeeds)
        mFeedOhlc = dFeeds['mFeedOhlc']
        
        iBeginValid = max(iLongMa, iShortMa)-1
        iEndOhlc = len(mFeedOhlc)

        if bUseTalib:
            import talib
            if False:
                # This is how I read the documentation:
                rShortMa = talib.SMA(mFeedOhlc.O, timeperiod=iShortMa)
                rLongMa = talib.SMA(mFeedOhlc.O, timeperiod=iLongMa)
                # TypeError: Argument 'real' has incorrect type (expected numpy.ndarray, got Series)
            else:
                aOhlcCleanShortMA = talib.SMA(mFeedOhlc.O.values, timeperiod=iShortMa)
                aOhlcCleanLongMA = talib.SMA(mFeedOhlc.O.values, timeperiod=iLongMa)
                rShortMa = pandas.Series(aOhlcCleanShortMA, name='O',
                                         index=mFeedOhlc.O.index)
                rLongMa = pandas.Series(aOhlcCleanLongMA, name='O',
                                        index=mFeedOhlc.O.index)
        else:
            rShortMa = pandas.rolling_mean(mFeedOhlc.O, iShortMa)
            rLongMa = pandas.rolling_mean(mFeedOhlc.O, iLongMa)

        rShortMa = rShortMa[iBeginValid:]
        rLongMa = rLongMa[iBeginValid:]
        mOhlc = mFeedOhlc[iBeginValid:]
        self.oOm.vAppendHdf('recipe/ingredients/rShortMa', rShortMa)
        self.oOm.vSetMetadataHdf('recipe/ingredients/rShortMa', dIngredientsParams)
        self.oOm.vAppendHdf('recipe/ingredients/rLongMa', rLongMa)
        self.oOm.vSetMetadataHdf('recipe/ingredients/rLongMa', dIngredientsParams)
        self.dIngredients = dict(rShortMa=rShortMa, rLongMa=rLongMa,
                                 mOhlc=mOhlc,
                                 dIngredientsParams=dIngredientsParams)
        return self.dIngredients
    
    def dApplyRecipe(self, dDishesParams):
        """dApplyRecipe
        and returns a dictionary with keys rBuy, rCover, rSell, rShort,
        which are pandas timeseries ismorphic to the 
        and a copy of the dDishesParams.
        """
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

