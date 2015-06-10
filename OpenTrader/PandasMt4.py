# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import sys, os
import datetime
import pandas

dDF_OHLC = {}
dDF_Raw1Df = {}

def vCookFiles(sSymbol, sDir):
    for sYear in ['2010', '2011', '2012', '2013', '2014', '2015']:
        sRaw1 = os.path.join(sDir, sSymbol + '1-' +sYear +'.csv')
        assert os.path.exists(sRaw1), "File not found: " +sRaw1

        for sTimeFrame in ['60', '240', '1440']:
            sCooked = os.path.join(sDir, sSymbol + sTimeFrame +'-' +sYear +'.csv')
            if not os.path.exists(sCooked):
                print "INFO: cooking %s %s %s" % (sTimeFrame, sSymbol, sYear, )
                vCookFile(sRaw1, sCooked, sTimeFrame, sSymbol, sYear)
            assert os.path.exists(sCooked)

def vCookFile(sRaw1, sCooked, sTimeFrame, sSymbol, sYear):
    global dDF_Raw1Df

    sKey = sSymbol + sTimeFrame + sYear
    if sKey not in dDF_Raw1Df:
        print "INFO: reading " + sRaw1
        dDF_Raw1Df[sKey] = pandas.read_csv(sRaw1, header=None,
                                             names=['D', 'T', 'O', 'H', 'L', 'C', 'V'],
                                             parse_dates={'timestamp': ['D', 'T']},
                                             index_col='timestamp',
                                             dtype='float64')
        print "INFO: raw data length: %d" % len(dDF_Raw1Df[sKey])
        # 2015 INFO: raw data length: 633920

    oDfOpen1 = dDF_Raw1Df[sKey].iloc[:, [0]]
    print "INFO: %s %s %s raw open length: %d" % (sTimeFrame, sSymbol, sYear, len(oDfOpen1),)
    dDF_OHLC[sTimeFrame] = oDfOpen1.resample(sTimeFrame+'T', how='ohlc',
                                             closed='left',
                                             # kind='timestamp'
                                             )
    print "INFO: sampled length from %d to %d raw/%s = %.2f" % (len(oDfOpen1),
                                                                len(dDF_OHLC[sTimeFrame]),
                                                                sTimeFrame,
                                                                len(oDfOpen1)/float(sTimeFrame))
    dDF_OHLC[sTimeFrame].to_csv(sCooked, header=False)
    print "INFO: wrote "+sCooked

def oReadMt4Csv(pCooked, sTimeFrame, sSymbol, sYear=""):
    global dDF_OHLC
    sKey = sSymbol + sTimeFrame + sYear
    if sKey not in dDF_OHLC:
        print "INFO: reading " + pCooked
        dDF_OHLC[sKey] = pandas.read_csv(pCooked,
                                         names=['T', 'O', 'H', 'L', 'C'],
                                         parse_dates={'timestamp': ['T']},
                                         index_col='timestamp',
                                         dtype={'O': 'float64',
                                                'H': 'float64',
                                                'L': 'float64',
                                                'C': 'float64'})
    return dDF_OHLC[sKey]

def oPreprocessOhlc(oOhlc):
    # is this in-place?
    return oOhlc.dropna(how='any')

