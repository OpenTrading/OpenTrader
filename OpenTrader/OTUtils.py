# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

def sStripCreole(s):
    # quick and dirty for now
    s = s.replace('{{{', '')
    s = s.replace('}}}', '')
    return s

def lConfigToList(oC):
    l = [['Key', 'Value']]
    for sSect in oC.keys():
        for sKey in oC[sSect].keys():
            sMark = sSect +'/' +sKey
            l.append([sMark, oC[sSect][sKey]])
    return l
