# coding: utf8

# part of pybacktest package: https://github.com/ematvey/pybacktest

"""
Functions for calculating performance statistics and reporting.
I think these are generic and only assume that rEquity is
an equity differences Series.
"""

import pandas
import numpy


def start(rEquity):
    return rEquity.index[0]
def end(rEquity):
    return rEquity.index[-1]
def days(rEquity):
    return (rEquity.index[-1] - rEquity.index[0]).days
def trades_per_month(rEquity):
    return rEquity.groupby(lambda x: (x.year, x.month) 
                       ).apply(lambda x: x[x != 0].count()).mean()
def profit(rEquity):
    return rEquity.sum()
def average(rEquity):
    return rEquity[rEquity != 0].mean()
def average_gain(rEquity):
    return rEquity[rEquity > 0].mean()
def average_loss(rEquity):
    return rEquity[rEquity < 0].mean()
def winrate(rEquity):
    return float(sum(rEquity > 0)) / len(rEquity)
def payoff(rEquity):
    return rEquity[rEquity > 0].mean() / -rEquity[rEquity < 0].mean()
def PF(rEquity):
    return abs(rEquity[rEquity > 0].sum() / rEquity[rEquity < 0].sum())
pf = PF
def maxdd(rEquity):
    return (rEquity.cumsum() - pandas.expanding_max(rEquity.cumsum())).abs().max()
def RF(rEquity):
    return rEquity.sum() / maxdd(rEquity)
rf = RF
def trades(rEquity):
    return len(rEquity[rEquity != 0])
def _days(rEquity):
    return rEquity.resample('D', how='sum').dropna()

def sharpe(rEquity):
    ''' daily sharpe ratio '''
    d = _days(rEquity)
    return (d.mean() / d.std()) ** (252**0.5)

def sortino(rEquity):
    ''' daily sortino ratio '''
    d = _days(rEquity)
    return (d.mean() / d[d < 0]).std()


def ulcer(rEquity):
    eq = rEquity.cumsum()
    return (((eq - pandas.expanding_max(eq)) ** 2).sum() / len(eq)) ** 0.5


def upi(rEquity, risk_free=0):
    eq = rEquity[rEquity != 0]
    return (eq.mean() - risk_free) / ulcer(eq)
UPI = upi


def mpi(rEquity):
    """ Modified UPI, with enumerator resampled to months (to be able to
    compare short- to medium-term strategies with different trade frequencies. """
    return rEquity.resample('M', how='sum').mean() / ulcer(rEquity)
MPI = mpi


def mcmdd(rEquity, runs=1000, quantile=0.99, array=False):
    maxdds = [maxdd(rEquity.take(numpy.random.permutation(len(rEquity)))) for i in xrange(runs)]
    if not array:
        return pandas.Series(maxdds).quantile(quantile)
    else:
        return maxdds


def holding_periods(rEquity):
    # rather crude, but will do
    return pandas.Series(rEquity.index.to_datetime(), index=rEquity.index, dtype=object).diff().dropna()


def dPerformanceSummary(equity_diffs, quantile=0.99, precision=4):
    def force_quantile(series, q):
        return sorted(series.values)[int(len(series) * q)]
    rEquity = equity_diffs[equity_diffs != 0]
    if getattr(rEquity.index, 'tz', None) is not None:
        rEquity = rEquity.tz_convert(None)
    if len(rEquity) == 0:
        return {}
    hold = holding_periods(equity_diffs)
    return {
        'backtest': {
            'from': str(rEquity.index[0]),
            'to': str(rEquity.index[-1]),
            'days': (rEquity.index[-1] - rEquity.index[0]).days,
            'trades': len(rEquity),
            },
        'exposure': {
            'trades/month': round(rEquity.groupby(
                    lambda x: (x.year, x.month)
                    ).apply(lambda x: x[x != 0].count()).mean(), precision),
            #'holding periods': {
            #    'max': str(hold.max()),
            #    'median': str(force_quantile(hold, 0.5)),
            #    'min': str(hold.min()),
            #    }
            },
        'performance': {
            'profit': round(rEquity.sum(), precision),
            'averages': {
                'trade': round(rEquity.mean(), precision),
                'gain': round(rEquity[rEquity > 0].mean(), precision),
                'loss': round(rEquity[rEquity < 0].mean(), precision),
                },
            'winrate': round(float(sum(rEquity > 0)) / len(rEquity), precision),
            'payoff': round(rEquity[rEquity > 0].mean() / -rEquity[rEquity < 0].mean(), precision),
            'PF': round(abs(rEquity[rEquity > 0].sum() / rEquity[rEquity < 0].sum()), precision),
            'RF': round(rEquity.sum() / maxdd(rEquity), precision),
            },
        'risk/return profile': {
            'sharpe': round(rEquity.mean() / rEquity.std(), precision),
            'sortino': round(rEquity.mean() / rEquity[rEquity < 0].std(), precision),
            'maxdd': round(maxdd(rEquity), precision),
            'WCDD (monte-carlo %s quantile)' % quantile: round(mcmdd(rEquity, quantile=quantile), precision),
            'UPI': round(UPI(rEquity), precision),
            'MPI': round(MPI(rEquity), precision),
            }
        }
