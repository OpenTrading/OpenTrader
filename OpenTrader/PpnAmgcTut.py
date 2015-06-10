# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

# from http://pythonprogramming.net/advanced-matplotlib-graphing-charting-tutorial

"""
give the Symbol Timeframe and Year to graph
The Timeframe is the period in minutes: e.g. 1 60 240 1440
YMMV: IT WILL NOT WORK for less than Daily: 1440
"""

import sys
import os
import urllib2
import time
import datetime
from collections import OrderedDict
import pandas
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick
import pylab

from PandasMt4 import oReadMt4Csv, oPreprocessOhlc

# matplotlib.rcParams.update({'font.size': 11})

dOHLC_CACHE_DF = {}

def rsiFunc(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi

def nSMA(values,window):
    weigths = np.repeat(1.0, window)/window
    smas = np.convolve(values, weigths, 'valid')
    return smas # as a numpy array

########EMA CALC ADDED############
def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a


def computeMACD(x, slow=26, fast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = ExpMovingAverage(x, slow)
    emafast = ExpMovingAverage(x, fast)
    return emaslow, emafast, emafast - emaslow

def lPullYahooToTxtfile(sSymbol):
    '''
        Use this to dynamically pull a sSymbol:
    '''
    try:
        print 'Currently Pulling',sSymbol
        print str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
        #Keep in mind this is close high low open, lol.
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+sSymbol+'/chartdata;type=quote;range=10y/csv'
        lStockLines = []
        try:
            sourceCode = urllib2.urlopen(urlToVisit).read()
            splitSource = sourceCode.split('\n')
            for eachLine in splitSource:
                splitLine = eachLine.split(',')
                if len(splitLine)==6:
                    if 'values' not in eachLine:
                        lStockLines.append(eachLine)
            return lStockLines
        except Exception, e:
            print str(e), 'failed to organize pulled data.'
    except Exception,e:
        print str(e), 'failed to pull pricing data'
    return None

def vGraphData(sSymbol, date, closep, highp, lowp, openp, volume,
               iShortSMA=10, iLongSMA=50,
               iRsiUpper=70, iRsiLower=30,
               iMacdSlow=26, iMacdFast=12, iMacdEma=9,
               bUseTalib=False,
               ):
    if bUseTalib:
        import talib

    x = 0
    y = len(date)
    newAr = []
    while x < y:
        appendLine = date[x],openp[x],closep[x],highp[x],lowp[x],volume[x]
        newAr.append(appendLine)
        x+=1

    if bUseTalib:
        Av1 = talib.SMA(closep, iShortSMA)
        Av2 = talib.SMA(closep, iLongSMA)
    else:
        Av1 = nSMA(closep, iShortSMA)
        Av2 = nSMA(closep, iLongSMA)

    SP = len(date[iLongSMA-1:])

    fig = plt.figure(facecolor='#07000d')

    ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')
    candlestick(ax1, newAr[-SP:], width=.6, colorup='#53c156', colordown='#ff1717')

    Label1 = str(iShortSMA)+' SMA'
    Label2 = str(iLongSMA)+' SMA'

    ax1.plot(date[-SP:],Av1[-SP:],'#e1edf9',label=Label1, linewidth=1.5)
    ax1.plot(date[-SP:],Av2[-SP:],'#4ee6fd',label=Label2, linewidth=1.5)

    uSpinesFg = "#5998ff"
    ax1.grid(True, color='white')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color(uSpinesFg)
    ax1.spines['top'].set_color(uSpinesFg)
    ax1.spines['left'].set_color(uSpinesFg)
    ax1.spines['right'].set_color(uSpinesFg)
    ax1.tick_params(axis='y', colors='white')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='white')
    plt.ylabel('Stock price and Volume')

    maLeg = plt.legend(loc=9, ncol=2, prop={'size': 7},
                       fancybox=True, borderaxespad=0.0)
    maLeg.get_frame().set_alpha(0.4)

    oLegend = pylab.gca().get_legend()
    if oLegend:
        # AttributeError: 'NoneType' object has no attribute 'get_texts'
        textEd = oLegend.get_texts()
        pylab.setp(textEd[0:5], color = 'white')

    volumeMin = 0

    ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
    rsi = rsiFunc(closep)
    rsiCol = '#c1f9f7'
    posCol = '#386d13'
    negCol = '#8f2020'

    ax0.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
    ax0.axhline(iRsiUpper, color=negCol)
    ax0.axhline(iRsiLower, color=posCol)
    ax0.fill_between(date[-SP:], rsi[-SP:], iRsiUpper, where=(rsi[-SP:]>=iRsiUpper), facecolor=negCol, edgecolor=negCol, alpha=0.5)
    ax0.fill_between(date[-SP:], rsi[-SP:], iRsiLower, where=(rsi[-SP:]<=iRsiLower), facecolor=posCol, edgecolor=posCol, alpha=0.5)
    ax0.set_yticks([iRsiLower, iRsiUpper])
    ax0.yaxis.label.set_color("w")
    ax0.spines['bottom'].set_color(uSpinesFg)
    ax0.spines['top'].set_color(uSpinesFg)
    ax0.spines['left'].set_color(uSpinesFg)
    ax0.spines['right'].set_color(uSpinesFg)
    ax0.tick_params(axis='y', colors='white')
    ax0.tick_params(axis='x', colors='white')
    plt.ylabel('RSI')

    uVolumeFg = '#00ffe8'
    ax1v = ax1.twinx()
    ax1v.fill_between(date[-SP:],volumeMin, volume[-SP:], facecolor=uVolumeFg, alpha=.4)
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    ###Edit this to 3, so it's a bit larger
    ax1v.set_ylim(0, 3*volume.max())
    ax1v.spines['bottom'].set_color(uSpinesFg)
    ax1v.spines['top'].set_color(uSpinesFg)
    ax1v.spines['left'].set_color(uSpinesFg)
    ax1v.spines['right'].set_color(uSpinesFg)
    ax1v.tick_params(axis='x', colors='white')
    ax1v.tick_params(axis='y', colors='white')

    ax2 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
    uMacdFill = '#00ffe8'
    emaslow, emafast, macd = computeMACD(closep, slow=iMacdSlow, fast=iMacdFast)
    ema9 = ExpMovingAverage(macd, iMacdEma)
    ax2.plot(date[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
    ax2.plot(date[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
    ax2.fill_between(date[-SP:], macd[-SP:]-ema9[-SP:], 0,
                     alpha=0.5, facecolor=uMacdFill, edgecolor=uMacdFill)

    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax2.spines['bottom'].set_color(uSpinesFg)
    ax2.spines['top'].set_color(uSpinesFg)
    ax2.spines['left'].set_color(uSpinesFg)
    ax2.spines['right'].set_color(uSpinesFg)
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    plt.ylabel('MACD', color='w')
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)

    plt.suptitle(sSymbol.upper(), color='white')

    plt.setp(ax0.get_xticklabels(), visible=False)
    ### add this ####
    plt.setp(ax1.get_xticklabels(), visible=False)

    ## ax1.annotate('Big news!',(date[510],Av1[510]),
    ##     xytext=(0.8, 0.9), textcoords='axes fraction',
    ##     arrowprops=dict(facecolor='white', shrink=0.05),
    ##     fontsize=14, color = 'w',
    ##     horizontalalignment='right', verticalalignment='bottom')

    plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
    plt.show()
    # fig.savefig('example.png',facecolor=fig.get_facecolor())

def iOldMain():
    sSymbol = sys.argv[1]
    lStockLines = lPullYahooToTxtfile(sSymbol)
    date, closep, highp, lowp, openp, volume = \
          np.loadtxt(lStockLines, delimiter=',', unpack=True,
                     converters={0: matplotlib.dates.strpdate2num('%Y%m%d')})
    # was  10, 50)
    dKw = OrderedDict(
        iShortSMA=10,
        iLongSMA=50,
        iRsiUpper=70,
        iRsiLower=30,
        iMacdSlow=26,
        iMacdFast=12,
        iMacdEma=9,
        bUseTalib=False,
        )
    vGraphData(sSymbol, date, closep, highp, lowp, openp, volume,
               **dKw
#               iShortSMA, iLongSMA,
#               iRsiUpper, iRsiLower,
#               iMacdSlow, iMacdFast, iMacdEma,
#               bUseTalib
               )

def oParseOptions(sUsage):
    """
    """
    oArgParser = ArgumentParser(description=sUsage)
    oArgParser.add_argument('-u', '--use_talib',
                            dest='bUseTalib', action='store_true', default=False,
                            help='Use Ta-lib for chart operations')
    return oArgParser

def iMain():
    sUsage = __doc__.strip()
    oArgParser = oParseOptions(sUsage)
    oArgParser.add_argument('lArgs', action="store",
                            nargs="*",
                            help="the Symbol Timeframe and Year to backtest (required)")
    oOptions = oArgParser.parse_args()
    lArgs = oOptions.lArgs

    assert len(lArgs) == 3, "Give the Symbol Timeframe and Year as arguments to this script"

    sSymbol = lArgs[0] # 'EURGBP'
    sTimeFrame = lArgs[1] # '1440'
    sYear = lArgs[2] # '2014'
    # FixMe:
    pDir = '/t/Program Files/HotForex MetaTrader/history/tools.fxdd.com'

    pCooked = os.path.join(pDir, sSymbol + sTimeFrame +'-' +sYear +'.csv')

    oOhlc = oReadMt4Csv(pCooked, sTimeFrame, sSymbol, sYear)
    oOhlc = oPreprocessOhlc(oOhlc)
    # (Pdb) pandas.tseries.converter._dt_to_float_ordinal(oOhlc.index)[0]
    # 735235.33333333337
    dates = matplotlib.dates.date2num(oOhlc.index.to_pydatetime())
    volume = 1000*np.random.normal(size=len(oOhlc))

    # FixMe:
    iShortSMA = 10
    iLongSMA = 50
    iRsiUpper = 70
    iRsiLower = 30
    iMacdSlow = 26
    iMacdFast = 12
    iMacdEma = 9

    vGraphData(sSymbol, dates,
               oOhlc.C.values, oOhlc.H.values, oOhlc.L.values, oOhlc.O.values,
               volume,
               iShortSMA, iLongSMA,
               iRsiUpper, iRsiLower,
               iMacdSlow, iMacdFast, iMacdEma,
               bUseTalib=oOptions.bUseTalib,
               )

if __name__ == '__main__':
    iMain()

