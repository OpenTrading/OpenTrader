# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

def sStripCreole(s):
    # quick and dirty for now
    s = s.replace('{{{', '')
    s = s.replace('}}}', '')
    return s
