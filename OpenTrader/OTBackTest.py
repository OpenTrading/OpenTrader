# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
Give the Symbol Timeframe and Year to backtest
The Timeframe is the period in minutes: e.g. 1 60 240 1440
"""

from __future__ import print_function
import sys, os
import traceback
import datetime
from collections import OrderedDict
from argparse import ArgumentParser

import pandas
import talib
from talib import abstract
import matplotlib
import matplotlib.pylab as pylab

from PandasMt4 import oReadMt4Csv, oPreprocessOhlc, vCookFiles

from Omlettes import Omlette

""" Set of data-loading helpers """



# http://nbviewer.ipython.org/github/ematvey/pybacktest/blob/master/examples/tutorial.ipynb
#? is this generic or specific to this chefModule?
#? IOOW does oPyBacktestCook belong here or PybacktestChef.py?
#? I think it belongs as a method to a class instance in PybacktestChef
# replace ChefModule with the instance and make cook a method in it.
# Thing is, I think dApplyRecipe is Chef dependent.
def oPyBacktestCook(dFeeds, oRecipe, oChefModule, oOm, oFd=sys.stdout):
    """
    Returns an error message string on failure; a Cooker instance on success.
    """
    dDishes = oRecipe.dApplyRecipe(oRecipe.dIngredients)
    rBuy = rCover = dDishes['rBuy']
    rSell = rShort = dDishes['rSell']

    if not len(rBuy[rBuy == True]):
        sMsg = "WARN: NO Buy/Cover signals; qutting!"
        sys.stderr.write(sMsg +'\n')
        return sMsg
    if not len(rSell[rSell == True]):
        sMsg = "WARN: NO Short/Sell signals; qutting!"
        sys.stderr.write(sMsg +'\n')
        return sMsg

    oFd.write('INFO:  Buy/Cover signals: \n%s\n' % rBuy[rBuy == True])
    oFd.write('INFO:  Short/Sell signals: \n%s\n' % rSell[rSell == True])

    mOhlc = oRecipe.dIngredients['mOhlc']
    assert len(mOhlc) == len(rBuy) == len(rSell)

    #? is this generic or specific to this chefModule?
    #? IOOW does dMakeChefsParams belong in Omlette or PybacktestChef.py?
    #? I think it belongs in Omlette and happens to work in PybacktestChef
    dDataObj = oOm.dMakeChefsParams(buy=rBuy, sell=rSell, short=rShort, cover=rCover,
                                    ohlc=mOhlc)
    #? should we test the dDataObj in oChefModule for validity?
    # *dataobj* should be dict-like structure containing signal series.
    # *signal_fields* specifies names of signal Series that backtester will
    # attempt to extract from dataobj.
    # the keys of sSataObj must be in the list and order of signal_fields
    dChefParams = OrderedDict(
        # derive these from the series
        signal_fields=('buy', 'sell', 'short', 'cover'),
        open_label='O',
        close_label='C',
        )
    oBt = oChefModule.ChefsOven(mOhlc, dDataObj, name=oOm.oRecipe.sName,
                               **dChefParams)
    #? mOhlc
    oOm.vAppendHdf('recipe/dishes/rBuy', rBuy)
    oOm.vAppendHdf('recipe/dishes/rSell', rSell)
    oOm.vAppendHdf('recipe/dishes/rShort', rShort)
    oOm.vAppendHdf('recipe/dishes/rCover', rCover)
    # FixMe:
    dChefParams['sName'] = oOm.oChefModule.sChef
    dChefParams['sUrl'] = 'file://' +oChefModule.__file__
    oOm.vSetMetadataHdf('recipe/dishes', dChefParams)

    return oBt

def vPlotEquityCurves(oBt, mOhlc, oChefModule,
                      sPeriod='W',
                      close_label='C',):
    matplotlib.rcParams['figure.figsize'] = (10, 5)

    # FixMe: derive the period from the sTimeFrame
    oChefModule.vPlotEquity(oBt.equity, mOhlc, sTitle="%s\nEquity" % repr(oBt),
                           sPeriod=sPeriod,
                           close_label=close_label,
                           )
    pylab.show()

    oBt.vPlotTrades()
    pylab.legend(loc='lower left')
    pylab.show()

    oBt.vPlotTrades(subset=slice(sYear+'-05-01', sYear+'-09-01'))
    pylab.legend(loc='lower left')
    pylab.show()

def oParseOptions(sUsage):
    """
    usage: OTBackTest.py [-h] [-P] [-R SRECIPE] [-C SCHEF] [-O SOMELETTE]
                         [lArgs [lArgs ...]]

    give the Symbol Timeframe and Year to backtest The Timeframe is the period in
    minutes: e.g. 1 60 240 1440

    positional arguments:
      lArgs                 the Symbol Timeframe and Year to backtest (required)

    optional arguments:
      -h, --help            show this help message and exit
      -P, --plot_equity     plot the equity curves of the servings
      -R SRECIPE, --recipe SRECIPE
                            recipe to backtest
      -C SCHEF, --chef SCHEF
                            recipe to backtest
      -O SOMELETTE, --omelette SOMELETTE
                            store the recipe and servings in an hdf5 store
    """
    oArgParser = ArgumentParser(description=sUsage)
    oArgParser.add_argument('-P', '--plot_equity',
                            dest='bPlotEquity', action='store_true', default=False,
                            help='plot the equity curves of the servings')
    oArgParser.add_argument("-R", "--recipe", action="store",
                            dest="sRecipe", default="SMARecipe",
                            help="recipe to backtest")
    oArgParser.add_argument("-C", "--chef", action="store",
                            dest="sChef",
                            default="PybacktestChef",
                            help="recipe to backtest")
    oArgParser.add_argument("-O", "--omelette", action="store",
                            dest="sOmelette", default="",
                            help="store the recipe and servings in an hdf5 store")
    return oArgParser


def iMain():
    oHdfStore = None

    sUsage = __doc__.strip()
    oArgParser = oParseOptions(sUsage)
    oArgParser.add_argument('lArgs', action="store",
                            nargs="*",
                            help="the Symbol Timeframe and Year to backtest (required)")
    oOptions = oArgParser.parse_args()
    lArgs = oOptions.lArgs
    oFd = sys.stdout

    assert len(lArgs) == 3, "Give the Symbol Timeframe and Year as arguments to this script"

    sSymbol = lArgs[0] # 'EURGBP'
    sTimeFrame = lArgs[1] # '1440'
    sYear = lArgs[2] # '2014'
    sDir = '/t/Program Files/HotForex MetaTrader/history/tools.fxdd.com'
    sCsvFile = os.path.join(sDir, sSymbol + sTimeFrame +'-' +sYear +'.csv')
    if not os.path.isfile(sCsvFile):
        vCookFiles(sSymbol, sDir)

    oOm = None
    try:
        oOm = Omlette.Omlette(sHdfStore=oOptions.sOmelette, oFd=sys.stdout)

        oRecipe = oOm.oAddRecipe(oOptions.sRecipe)
        oChefModule = oOm.oAddChef(oOptions.sChef)

        dFeedParams = dict(sTimeFrame=sTimeFrame, sSymbol=sSymbol, sYear=sYear)
        dFeed = oOm.dGetFeedFrame(sCsvFile, **dFeedParams)
        mFeedOhlc = dFeed['mFeedOhlc']

        mFeedOhlc = oPreprocessOhlc(mFeedOhlc)
        oFd.write('INFO:  Data Open length: %d\n' % len(mFeedOhlc))
        # ugly - should be a list of different feed timeframes etc.
        dFeeds = dict(mFeedOhlc=mFeedOhlc, dFeedParams=dFeedParams)
        dRecipeParams = oRecipe.dRecipeParams()
        # this now comes from the recipe ini file: bUseTalib=oOptions.bUseTalib
        dIngredientsParams = dict(dRecipeParams=dRecipeParams)
        oRecipe.dMakeIngredients(dFeeds, dIngredientsParams)
        assert oRecipe.dIngredients

        oBt = oPyBacktestCook(dFeeds, oRecipe, oChefModule, oOm)
        assert oBt is not None
        if type(oBt) == str:
            raise RuntimeError(oBt)

        # this was the same as: oBt._mSignals = bt.mSignals() or oBt.signals
        oBt._mSignals = oRecipe.mSignals(oBt)
        oFd.write('INFO:  bt.signals found: %d\n' % len(oBt.signals))
        oOm.vAppendHdf('recipe/servings/mSignals', oBt.signals)

        # this was the same as: oBt._mTrades =  oBt.mTrades() or oBt.trades
        oBt._mTrades = oRecipe.mTrades(oBt)
        oFd.write('INFO:  bt.trades found: %d\n' % len(oBt.trades))
        oOm.vAppendHdf('recipe/servings/mTrades', oBt.trades)

        # this was the same as: oBt._rPositions = oBt.rPositions() or oBt.positions
        oBt._rPositions = oRecipe.rPositions(oBt, init_pos=0)
        oFd.write('INFO:  bt.positions found: %d\n' % len(oBt.positions))
        oOm.vAppendHdf('recipe/servings/rPositions', oBt.positions)

        # this was the same as: oBt._rEquity = oBt.rEquity() or oBt.equity
        oBt._rEquity = oRecipe.rEquity(oBt)
        oFd.write('INFO:  bt.equity found: %d\n' % len(oBt.equity))
        oOm.vAppendHdf('recipe/servings/rEquity', oBt.equity)

        # oFd.write('INFO:  bt.rTradePrice() found: %d\n' % len(oBt.rTradePrice()))
        oFd.write('INFO:  bt.trade_price found: %d\n' % len(oBt.trade_price))
        oOm.vAppendHdf('recipe/servings/rTradePrice', oBt.trade_price)

        oOm.vSetTitleHdf('recipe/servings', oOm.oChefModule.sChef)
        #? Leave this as derived or store it? reviews?
        oOm.vSetMetadataHdf('recipe/servings', oBt.dSummary())
        oFd.write(oBt.sSummary())

        oOm.vSetMetadataHdf('recipe', dRecipeParams)

        if oOptions.bPlotEquity:
            vPlotEquityCurves(oBt, mOhlc)
    except KeyboardInterrupt:
        pass
    except Exception, e:
        sys.stderr.write("ERROR: " +str(e) +"\n" + \
                         traceback.format_exc(10) +"\n")
        sys.stderr.flush()
        sys.exc_clear()
    finally:
        if oOm: oOm.vClose()

if __name__ == '__main__':
    iMain()
