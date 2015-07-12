# coding: utf8

"""


s@dataobj@dDataDict@
s@extract_frame@mExtractFrame@
s@plot_equity@vPlotEquity@
s@plot_trades@vPlotTrades@
s@sig_mask_ext@lSignalFieldsExt@
s@sig_mask_int@lSignalFieldsInt@
s@pr_mask_ext@lPriceFieldsExt@
s@pr_mask_int@lPriceFieldsInt@
"""

# part of pybacktest package: https://github.com/ematvey/pybacktest

from __future__ import print_function
import sys
import time

from pandas.lib import cache_readonly

import pandas
from OpenTrader import PYBTDailyPerformance

class StatEngine(object):
    def __init__(self, equity_fn):
        self._stats = [i for i in dir(PYBTDailyPerformance) if not i.startswith('_')]
        self._equity_fn = equity_fn

    def __dir__(self):
        return dir(type(self)) + self._stats

    def __getattr__(self, attr):
        if attr in self._stats:
            equity = self._equity_fn()
            fn = getattr(PYBTDailyPerformance, attr)
            try:
                return fn(equity)
            except Exception, e:
                sys.stdout.write("Error calling %s function: %s\n" % (attr, str(e),))
                return
        else:
            raise IndexError(
                "Calculation of '%s' statistic is not supported" % attr)


def mExtractFrame(dDataDict, ext_mask, int_mask):
    """
    May return None
    """
    df = {}
    for f_int, f_ext in zip(int_mask, ext_mask):
        obj = dDataDict.get(f_ext)
        if isinstance(obj, pandas.Series):
            df[f_int] = obj
        else:
            df[f_int] = None
    if any(map(lambda x: isinstance(x, pandas.Series), df.values())):
        return pandas.DataFrame(df)
    return None

# are these specific to the chef or generic to the process?
lProducedServings = ['signals', 'trades', 'positions', 'equity', 'trade_price', 'reviews']

class ChefsOven(object):
    """
    Backtest (Pandas implementation of vectorized backtesting).

    Lazily attempts to extract multiple pandas.Series with signals and prices
    from a given namespace and combine them into equity curve.


    """
    # FixMe: ini file
    _lSignalFields = ('buy', 'sell', 'short', 'cover')
    _lSignalFieldsInt = ('Buy', 'Sell', 'Short', 'Cover')
    _lPriceFieldsInt = ('BuyPrice', 'SellPrice', 'ShortPrice', 'CoverPrice')
    # these are the results you can get back from this Chef

    def __init__(self, mOhlc, dDataDict, name='Unknown',
                 signal_fields=None,
                 price_fields=('buyprice', 'sellprice', 'shortprice',
                               'coverprice'),
                 open_label='O',
                 close_label='C'):
        """
        Arguments:

        *mOhlc* is a dataframe with the timeseries O H L C of the instrument.

        *dDataDict* should be dict-like structure containing signal series.
        The dict must contain pandas.Series with the names in
        signal_fields - default: ('buy', 'sell', 'short', 'cover')

        *name* is simply backtest/strategy name. Will be user for printing,
        potting, etc.

        *signal_fields* specifies names of signal Series that backtester will
        extract from dDataDict. By default follows AmiBroker's naming convention,
        which is ...?

        *price_fields* specifies names of price Series where trades will take
        place. If some price is not specified (NaN at signal's timestamp, or
        corresponding Series not present in dDataDict altogether), defaults to
        Open price of next bar. By default follows AmiBroker's naming
        convention: ('buyprice', 'sellprice', 'shortprice', 'coverprice'),


        """
        self.sName = 'pybacktest'
        self._mOhlc = mOhlc
        self.name = name
        self.open_label = open_label
        self.close_label = close_label
        
        self._dDataDict = dict([(k.lower(), v) for k, v in dDataDict.iteritems()])
        
        if signal_fields == None:
            signal_fields = _lSignalFields
        else:
            for sElt in signal_fields:
                assert sElt in dDataDict
                assert isinstance(dDataDict[sElt], pandas.Series)
        assert len(signal_fields) == len(price_fields)
        self._lSignalFieldsExt = signal_fields
        self._lPriceFieldsExt = price_fields

        self.run_time = time.strftime('%Y-%d-%m %H:%M %Z', time.localtime())
        self.stats = StatEngine(lambda: self.equity)
        # make things explicit with a functional programming style too
        self._mSignals = False
        self._rTradePrice = False
        self._rPositions = False
        self._mTrades = False
        self._rEquity = False

    def __repr__(self):
        return "Backtest(%s, %s)" % (self.name, self.run_time)

    @property
    def dDataDict(self):
        return self._dDataDict

    @cache_readonly
    def signals(self):
        if self._mSignals is False:
            self._mSignals = self.mSignals()
        return self._mSignals
    
    def mSignals(self):
        assert self.dDataDict
        for sKey in self._lSignalFieldsExt:
            # signals must be in the dDataDict or we cant run
            assert sKey in self.dDataDict
        m = mExtractFrame(self.dDataDict, self._lSignalFieldsExt,
                          self._lSignalFieldsInt)
        assert m is not None
        return m.fillna(value=False)

    @cache_readonly
    def prices(self):
        m = mExtractFrame(self.dDataDict, self._lPriceFieldsExt,
                          self._lPriceFieldsInt)
        # may be None
        return m
    
    @cache_readonly
    def trade_price(self):
        if self._rTradePrice is False:
            self._rTradePrice = self.rTradePrice()
        return self._rTradePrice
            
    def rTradePrice(self):
        if self.prices is None:
            return getattr(self.ohlc, self.open_label)  # .shift(-1)
        dp = pandas.Series(dtype=float, index=self.prices.index)
        for pf, sf in zip(self._lPriceFieldsInt, self._lSignalFieldsInt):
            s = self.signals[sf]
            p = self.prices[pf]
            dp[s] = p[s]
            
        self.default_price = getattr(self.ohlc, self.open_label)  # .shift(-1)
        return dp.combine_first(self.default_price)

    @cache_readonly
    def positions(self):
        if self._rPositions is False:
            self._rPositions = self.rPositions()
        return self._rPositions
    
    def rPositions(self):
        """
        Translate signal dataframe into positions series (trade prices aren't
        specified.
        WARNING: In production, override default zero value in init_pos with
        extreme caution.
        """
        from pybacktest import parts
        return parts.signals_to_positions(self.signals, init_pos=0,
                                          mask=self._lSignalFieldsInt)

    @cache_readonly
    def trades(self):
        if self._mTrades is False:
            self._mTrades = self.mTrades()
        return self._mTrades
    
    def mTrades(self):
        p = self.positions.reindex(
            self.signals.index).ffill().shift().fillna(value=0)
        p = p[p != p.shift()]
        tp = self.trade_price
        assert p.index.tz == tp.index.tz, "ERROR: Cant operate on signals and prices " \
                                          "indexed as of different timezones"
        t = pandas.DataFrame({'pos': p})
        t['price'] = tp
        t = t.dropna()
        t['vol'] = t.pos.diff()
        return t.dropna()

    @cache_readonly
    def equity(self):
        if self._rEquity is False:
            self._rEquity = self.rEquity()
        return self._rEquity
    
    def rEquity(self):
        # equity diff series
        from pybacktest import parts
        return parts.trades_to_equity(self.trades)

    @cache_readonly
    def ohlc(self):
        return self._mOhlc

    @cache_readonly
    def report(self):
        return PYBTDailyPerformance.dPerformanceSummary(self.equity)

    def summary(self):
        self.vPrintSummary()
        
    def vPrintSummary(self):
        print(self.sSummary())
        
    def sSummary(self):
        import yaml
        s = '|  %s  |' % self
        d = self.dSummary()
        sRetval = ""
        sRetval += '-' * len(s) +'\n'
        sRetval += s +'\n'
        sRetval += '-' * len(s) +'\n'
        sRetval += yaml.dump(d, allow_unicode=True, default_flow_style=False) +'\n'
        sRetval += '-' * len(s) +'\n'
        return sRetval
    
    def dSummary(self):
        return PYBTDailyPerformance.dPerformanceSummary(self.equity)
    
    def lSummary(self):
        dSummary = self.dSummary()
        l = []
        for sTop in dSummary.keys():
            for sMid in dSummary[sTop].keys():
                g = dSummary[sTop][sMid]
                if isinstance(g, dict):
                    for sBot in g.keys():
                        l.append([sTop +'_' +sBot +'_' +sBot, g[sBot]])
                else:
                    l.append([sTop +'_' +sMid, g])
        return l
    
    def vPlotTrades(self, subset=None):
        if subset is None:
            subset = slice(None, None)
        fr = self.trades.ix[subset]
        le = fr.price[(fr.pos > 0) & (fr.vol > 0)]
        se = fr.price[(fr.pos < 0) & (fr.vol < 0)]
        lx = fr.price[(fr.pos.shift() > 0) & (fr.vol < 0)]
        sx = fr.price[(fr.pos.shift() < 0) & (fr.vol > 0)]

        import matplotlib.pylab as pylab

        pylab.plot(le.index, le.values, '^', color='lime', markersize=12,
                   label='long enter')
        pylab.plot(se.index, se.values, 'v', color='red', markersize=12,
                   label='short enter')
        pylab.plot(lx.index, lx.values, 'o', color='lime', markersize=7,
                   label='long exit')
        pylab.plot(sx.index, sx.values, 'o', color='red', markersize=7,
                   label='short exit')
        eq = self.equity.ix[subset].cumsum()
        ix = eq.index
        oOS = getattr(self.ohlc, self.open_label)
        (eq + oOS[ix[0]]).plot(color='red', style='-', label='strategy')
        # self.ohlc.O.ix[ix[0]:ix[-1]].plot(color='black', label='price')
        oOS.ix[subset].plot(color='black', label='price')
        pylab.legend(loc='best')
        pylab.title('%s\nTrades for %s' % (self, subset))
    
def vPlotEquity(rEquityDiff, mOhlc, sPeriod='W',
                subset=None,
                sTitle="Equity",
                close_label='C',
                ):
    if subset is None:
        subset = slice(None, None)
    else:
        assert isinstance(subset, slice)
        
    rEquitySum = rEquityDiff[subset].cumsum()
    rEquitySum.plot(color='red', label='strategy')
    ix = mOhlc.ix[rEquitySum.index[0]:rEquitySum.index[-1]].index
    price = getattr(mOhlc, close_label)
    (price[ix] - price[ix][0]).resample(sPeriod, how='first').dropna() \
        .plot(color='black', alpha=0.5, label='underlying')

    import matplotlib.pylab as pylab

    pylab.legend(loc='best')
    pylab.title(sTitle)

