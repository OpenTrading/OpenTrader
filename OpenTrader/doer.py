# -*-mode: python; fill-column: 75; coding: utf-8; encoding: utf-8 -*-

import sys, os
import traceback

from pprint import pformat

from OpenTrader.PLogMixin import PLogMixin

class Doer(PLogMixin):
    """The Doer class has one main method: bexecute
which will execute the options and args given to it
in the do_instance method of the Cmd2 instance.

It encapsulkates everything tthat is needed to do a
command in the Cmd2 instance.
"""

    def __init__(self, ocmd2, sprefix):
        self.ocmd2 = ocmd2
        self.poutput = self.ocmd2.poutput
        self.pfeedback = self.ocmd2.pfeedback
        self.sprefix = sprefix

    def G(self, gVal=None):
        if gVal is not None:
            self.ocmd2._G = gVal
            self._G = self.ocmd2._G
        return self.ocmd2._G

    def vassert_args(self, lArgs, lcommands, imin=1):
        assert len(lArgs) >= imin, \
               "ERROR: argument required, one of: " +str(lcommands)
        sDo = lArgs[0]
        assert  sDo in lcommands + ['help'], \
          "ERROR: " +sDo +" choose one of: " +str(lcommands)

    def bis_help(self, lArgs):
        sDo = lArgs[0]
        # e.g. make help
        if sDo != 'help':
            return False
        if not hasattr(self, 'lCommands'):
            lCommands = []
            for sElt in dir(self):
                if not sElt.startswith(self.sprefix): continue
                sKey = sElt[len(self.sprefix)+1:]
                lCommands.append(sKey)
            self.lCommands = lCommands
        if len(lArgs) == 1:
            self.poutput(self.dhelp[''])
            # N.B.: subcommands by convention are documented in the module docstring
            self.poutput("For help on subcommands type: " +self.sprefix +" help <sub> ")
            self.poutput("For help on options type: help " +self.sprefix)
            return True
        # e.g. make help features
        smeth = lArgs[1]
        smethod = self.sprefix +'_' + smeth
        # FixMe: make a wrapper so this isnt needed?
        if smeth not in self.dhelp and hasattr(self, smethod):
            omethod = getattr(self, smethod)
            if hasattr(omethod, '__doc__'):
                self.dhelp[smeth] = omethod.__doc__
        if smeth in self.dhelp:
            self.poutput(self.dhelp[smeth])
            self.poutput("For help on options type: help " +self.sprefix)
            return True
        raise NotImplementedError("Unknown help command for " +sDo +": " \
                                      +smeth +' not in ' +repr(self.lCommands))

    def bexecute(self, loptions, dkw):
        raise NotImplementedError(self.__class__.__name__)

    def vInfo(self, sMsg):
        self.poutput("INFO: " +sMsg)

    def vWarn(self, sMsg):
        self.poutput("WARN: " +sMsg)

    def vError(self, sMsg):
        self.poutput("ERROR: " +sMsg)
