# -*-mode: python; py-indent-offset: 4; encoding: utf-8-dos; coding: utf-8 -*-

"""The make command lets us make things that are useful, such as making
the feature files that will be used to run the tests.

* make [--features_dir] features: will generate the test feature files to test the code.
"""

import sys
import os
import StringIO
from optparse import make_option

from doer import Doer

SDOC = __doc__

LOPTIONS = [make_option('--features_dir', action="store",
                        dest="sFeaturesDir",
                        # FixMe: relative file
                        default="tests/features",
                        help="directory the feature files will be written to. The directory must exist.")]

LCOMMANDS = []

from maker_templates import *

LDOCUMENTED_COMMANDS = ['csv', 'chart', 'subscribe', 'publish', 'backtest', 'make']
# can documented these by adding to dhelp[]
LUNDOCUMENTED_COMMANDS = ['help', 'test']

def sindent(s, sspaces):
    ls = s.replace('\n\n', '\n').split('\n')
    s = '\n' + sspaces
    s = s.join(ls)
    return sspaces +s

class DoMake(Doer):
    __doc__ = SDOC
    # putting this as a module variable make it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'make')

    LCOMMANDS += ['features']
    def make_features(self):
        """make [--features_dir] features will generate the test feature files
that are used to test the code from the code itself. This way, the
documentation in the feature files is drawn directly from the documentation
in the code, which makes it easier to keep it up-to-date with the code.

make features uses the --features_dir dir option to the make command to know what
directory the feature files will be written to. The directory must exist.
"""
        sFeaturesDir = self.oValues.sFeaturesDir
        assert os.path.isdir(sFeaturesDir), " Directory does not exist: " +sFeaturesDir

        i = 0
        lpages = []
        oold_stdout = self.ocmd2.stdout
        try:
            for selt in LDOCUMENTED_COMMANDS:
                i += 1
                try:
                    ostdout = StringIO.StringIO()
                    self.ocmd2.stdout = ostdout
                    if True:
                        #? decide
                        self.ocmd2.do_help(selt)
                    else:
                        sCmd = selt +' help'
                        self.ocmd2.onecmd(sCmd)
                    sOut = ostdout.getvalue()
                finally:
                    ostdout.close()
                    self.ocmd2.stdout = oold_stdout

                lOut = sOut.split('\n')
                sForHelp = '\n'.join(lOut[-2:])
                sOut = '\n'.join(lOut[:-2])
                d = dict(sname=selt, shelp=sOut)
                stext = SFEATURE_TEMPLATE % d

                if selt == 'test':
                    # FixMe:
                    continue
                # English
                if selt.endswith('e'):
                    smodule = selt + 'r'
                else:
                    smodule = selt + 'er'
                if smodule == 'maker':
                    lCommands = LCOMMANDS
                else:
                    _temp = __import__(smodule, globals(), locals(),
                                    ['LCOMMANDS'], -1)
                    lCommands = getattr(_temp, 'LCOMMANDS')
                for ssubcommand in lCommands:
                    try:
                        ostdout = StringIO.StringIO()
                        self.ocmd2.stdout = ostdout

                        d['sname'] = selt +' ' +ssubcommand
                        sCmd = selt +' help ' +ssubcommand
                        self.ocmd2.onecmd(sCmd)
                        sOut = ostdout.getvalue()
                    finally:
                        ostdout.close()
                        self.ocmd2.stdout = oold_stdout

                    d['shelp'] = sindent(sForHelp, '    ')
                    stext += SSCENARIO_TEMPLATE % d

                    d['scommand'] = "We get help when we type \"" +sCmd +"\""
                    # FixMe: remove 'For help on '
                    d['sstring'] = sindent('"""' +sOut +'"""', '        ')
                    stext += SGIVEN_STEP_TEMPLATE % d

                sfile = '%02d' % i +'_' +selt
                lpages.append(sfile)
                sfile = os.path.join(sFeaturesDir, sfile +'.feature')
                with open(sfile, 'w') as ofd:
                    ofd.write(stext)

                self.poutput("INFO: help for " +selt +':\n' +stext)
        finally:
            self.ocmd2.stdout = oold_stdout
        # FixMe: make and index from lpages

    # FixMe: I'm confused
    maker_features = make_features

    def bexecute(self, lArgs, oValues):
        """bexecute executes the make command.
        """
        self.oValues = oValues
        self.lArgs = lArgs

        self.vassert_args(lArgs, LCOMMANDS, imin=1)
        if self.bis_help(lArgs):
            return

        sdo = lArgs[0]
        omethod = getattr(self, 'make_' +sdo)
        omethod()

        return True
