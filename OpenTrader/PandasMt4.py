# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import sys, os
import pandas

dDF_OHLC = {}
dDF_RAW1MIN = {}

def vResampleFiles(sSymbol, sDir):
    for sYear in ['2010', '2011', '2012', '2013', '2014', '2015']:
        sRaw1 = os.path.join(sDir, sSymbol + '1-' +sYear +'.csv')
        assert os.path.exists(sRaw1), "File not found: " +sRaw1

        for sTimeFrame in ['60', '240', '1440']:
            sResampledCsv = os.path.join(sDir, sSymbol + sTimeFrame +'-' +sYear +'.csv')
            if not os.path.exists(sResampledCsv):
                print "INFO: cooking %s %s %s" % (sTimeFrame, sSymbol, sYear, )
                vResample1Min(sRaw1, sResampledCsv, sTimeFrame)
            assert os.path.exists(sResampledCsv)

def vResample1Min(sRaw1, sResampledCsv, sTimeFrame, oFd=sys.stdout):
    global dDF_RAW1MIN

    sKey = sSymbol
    if sKey not in dDF_RAW1MIN:
        print "INFO: reading " + sRaw1
        dDF_RAW1MIN[sKey] = pandas.read_csv(sRaw1, header=None,
                                           names=['D', 'T', 'O', 'H', 'L', 'C', 'V'],
                                           parse_dates={'timestamp': ['D', 'T']},
                                           index_col='timestamp',
                                           dtype='float64')
        print "INFO: raw data length: %d" % len(dDF_RAW1MIN[sKey])

    oDfOpen1 = dDF_RAW1MIN[sKey].iloc[:, [0]]
    print "INFO: %s raw open length: %d" % (sTimeFrame, len(oDfOpen1),)
    dDF_OHLC[sTimeFrame] = oDfOpen1.resample(sTimeFrame+'T', how='ohlc',
                                             closed='left',
                                             # kind='timestamp'
                                             )
    oFd.write("INFO: sampled length from %d to %d raw/%s = %.2f\n" % (len(oDfOpen1),
                                                                      len(dDF_OHLC[sTimeFrame]),
                                                                      sTimeFrame,
                                                                      len(oDfOpen1)/float(sTimeFrame)))
    dDF_OHLC[sTimeFrame].to_csv(sResampledCsv, header=False)
    print "INFO: wrote "+sResampledCsv

def oReadMt4Csv(sResampledCsv, sTimeFrame, sSymbol, sYear=""):
    global dDF_OHLC
    sKey = sSymbol + sTimeFrame + sYear
    if sKey not in dDF_OHLC:
        print "INFO: reading " + sResampledCsv
        dDF_OHLC[sKey] = pandas.read_csv(sResampledCsv,
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

