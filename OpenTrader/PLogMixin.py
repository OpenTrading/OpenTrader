# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

class PLogMixin(object):

    def vOutput(self, sMsg):
        self.poutput("OTPy: " +sMsg)

    def vError(self, sMsg):
        self.poutput("ERR!: " +sMsg)

    def vWarn(self, sMsg):
        self.poutput("WARN: " +sMsg)

    def vInfo(self, sMsg):
        self.pfeedback("INFO: " +sMsg)

    def vDebug(self, sMsg):
        self.pfeedback("DEBUG: " +sMsg)

