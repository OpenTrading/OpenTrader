# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

# should these all be of chart ANY
"""
Manage orders in an OTMql4AQMp enabled Metatrader:
{{{
  ord list          - list the ticket numbers of current orders.
  ord info iTicket  - list the current order information about iTicket.
  ord trades        - list the details of current orders.
  ord history       - list the details of closed orders.
  ord close iTicket [fPrice iSlippage]            - close an order;
                    Without the fPrice and iSlippage it will be a market order.
  ord buy|sell sSymbol fVolume [fPrice iSlippage] - send an order to open;
                    Without the fPrice and iSlippage it will be a market order.
  ord stoploss
  ord trail
  ord exposure      - total exposure of all orders, worst case scenario
}}}
"""

SDOC = __doc__

import sys
import os

from optparse import make_option

from OpenTrader.doer import Doer

LOPTIONS = []

LCOMMANDS = []

class DoOrder(Doer):
    __doc__ = SDOC
    # putting this as a module variable order it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'order')

    LCOMMANDS += ['list']
    def order_list(self, sMark, sChartId):
        """ord list          - list the ticket numbers of current orders.
        """
        self.dhelp['list'] = __doc__

        sMsgType = 'exec' # Mt4 command
        # FixMe: trailing |
        sInfo = 'jOTOrdersTickets'
        j = self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
        # jOTOrdersTickets
        # pprint the json?
        self.ocmd2.vOutput(sInfo +": " +str(j))

    LCOMMANDS += ['tickets']
    order_tickets = order_list

    LCOMMANDS += ['trades']
    def order_trades(self, sMark, sChartId):
        """ord trades        - list the details of current orders.
        """
        self.dhelp['trades'] = __doc__

        sMsgType = 'exec' # Mt4 command
        # FixMe: trailing |
        sInfo = 'jOTOrdersTrades'
        j = self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
        self.ocmd2.vOutput(sInfo +": " +str(j))

    LCOMMANDS += ['history']
    def order_history(self, sMark, sChartId):
        """ord history       - list the details of closed orders.
        """
        self.dhelp['history'] = __doc__

        sMsgType = 'exec' # Mt4 command
        # FixMe: trailing |
        sInfo = 'jOTOrdersHistory'
        j = self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sInfo)
        self.ocmd2.vOutput(sInfo +": " +str(j))

    LCOMMANDS += ['info']
    def order_info(self, sMark, sChartId):
        """ord info iTicket  - list the current order information about iTicket.
        """
        self.dhelp['info'] = __doc__

        sMsgType = 'exec' # Mt4 command
        sCmd = 'jOTOrderInformationByTicket'
        assert len(self.lArgs) > 1, "ERROR: orders info iTicket"
        sInfo = str(self.lArgs[1])
        j = self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sInfo)
        self.ocmd2.vOutput(sInfo +": " +str(j))

    LCOMMANDS += ['exposure']
    def order_exposure(self, sMark, sChartId):
        """ord exposure      - total exposure of all orders, worst case scenario
        """
        self.dhelp['exposure'] = __doc__

        sMsgType = 'exec' # Mt4 command
        sCmd = 'fOTExposedEcuInMarket'
        sInfo = str(0)
        f = self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sInfo)
        self.ocmd2.vOutput(sInfo +": " +str(f))

    LCOMMANDS += ['close']
    def order_close(self, sMark, sChartId):
        """ord close iTicket [fPrice iSlippage]            - close an order;
                    Without the fPrice and iSlippage it will be a market order.
        """
        self.dhelp['close'] = __doc__

        sMsgType = 'exec' # Mt4 command
        assert len(self.lArgs) >= 2, "ERROR: order close iTicket [fPrice iSlippage}"
        sTicket = self.lArgs[1]
        if len(self.lArgs) >= 3:
            sPrice = self.lArgs[2]
            sSlippage = self.lArgs[3]
            sCmd = 'iOTOrderCloseFull'
            self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sTicket, sPrice, sSlippage)
        else:
            sCmd = 'iOTOrderCloseMarket'
            self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sTicket)

    LCOMMANDS += ['sell']
    def order_sell(self, sMark, sChartId):
        """ord buy|sell sSymbol fVolume [fPrice iSlippage] - send an order to open;
                    Without the fPrice and iSlippage it will be a market order.
        """
        self.dhelp['sell'] = __doc__
        self.order_buy_or_sell(sMark, sChartId, 'sell')

    LCOMMANDS += ['buy']
    def order_buy(self, sMark, sChartId):
        """ord buy|sell sSymbol fVolume [fPrice iSlippage] - send an order to open;
                    Without the fPrice and iSlippage it will be a market order.
        """
        self.dhelp['buy'] = __doc__
        self.order_buy_or_sell(sMark, sChartId, 'buy')

    def order_buy_or_sell(self, sMark, sChartId, sDo):
        sMsgType = 'exec' # Mt4 command
        if sDo == 'buy':
            iCmd = 0
        else:
            iCmd = 1 # Sell 1
        assert len(self.lArgs) >= 3, "ERROR: order buy|sell sSymbol fVolume [fPrice iSlippage]"
        # double stoploss, double takeprofit,
        # string comment="", int magic=0
        sArg1 = str(iCmd)
        sSymbol = self.lArgs[1]
        sVolume = self.lArgs[2]
        if len(self.lArgs) >= 5:
            sPrice = self.lArgs[3]
            sSlippage = self.lArgs[4]
            sCmd = 'iOTOrderSend'
            self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sSymbol, sArg1, sVolume, sPrice, sSlippage)
        else:
            sCmd = 'iOTOrderSendMarket'
            self.ocmd2.gWaitForMessage(sMsgType, sChartId, sMark, sCmd, sSymbol, sArg1, sVolume)

    def bexecute(self, lArgs, oValues):
        """bexecute executes the order command.
        """
        from OTMql427.SimpleFormat import sMakeMark

        _lCmds = LCOMMANDS
        self.lArgs = lArgs
        self.oValues = oValues

        self.vassert_args(lArgs, LCOMMANDS, imin=1)
        if self.bis_help(lArgs):
            return

        if self.ocmd2.oListenerThread is None:
            self.ocmd2.vError("ListenerThread not started; use 'sub run retval.#'")
            return

        sChartId = self.ocmd2.sDefaultChart
        # sMark is a simple timestamp: unix time with msec.
        sDo = lArgs[0]
        if sDo in LCOMMANDS:
            sMark = sMakeMark()
            oMeth = getattr(self, 'order_' +sDo)
            oMeth(sMark, sChartId)
            return

        self.ocmd2.poutput("ERROR: Unrecognized order command: " + str(lArgs) +'\n' +__doc__)
