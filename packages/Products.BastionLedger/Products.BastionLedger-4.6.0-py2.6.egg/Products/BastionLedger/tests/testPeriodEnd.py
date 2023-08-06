#
#    Copyright (C) 2008-2014  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase  # this fixes up PYTHONPATH :)
from Products.BastionLedger.tests import LedgerTestCase

from Products.BastionLedger.Exceptions import InvalidPeriodError
from Products.BastionLedger.utils import ceiling_date, floor_date
from Products.BastionLedger.BLGlobals import EPOCH

from Products.BastionLedger.interfaces.periodend import IPeriodEndInfo, IPeriodEndInfos

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency

p1_dt = DateTime('2007/06/30 UTC') #.toZone('UTC')
p2_dt = DateTime('2008/06/30 UTC') #.toZone('UTC')
p3_dt = DateTime('2009/06/30 UTC') #.toZone('UTC')

zero = ZCurrency('GBP 0.00')
ten = ZCurrency('GBP 10.00')
twenty = ZCurrency('GBP 20.00')
twentytwo = ZCurrency('GBP 22.00')

class TestPeriodEnd(LedgerTestCase.LedgerTestCase):

    def testCreated(self):
        self.failUnless(self.controller_tool.periodend_tool)

    def testEOD(self):
        self.assertEqual(self.ledger.accrued_to, ceiling_date(self.now))
        self.assertEqual(self.ledger.requiresEOD(), False)
        self.assertEqual(self.ledger.requiresEOD(self.now + 2), True)
        self.assertEqual(self.ledger.requiresEOD(DateTime('1900/01/01')), False)

    def testStartDates(self):
        effective = DateTime('2009/01/01')
        periods = self.ledger.periods
        
        self.assertEqual(periods.nextPeriodStart(effective), EPOCH)
        self.assertEqual(periods.nextPeriodEnd(effective), ceiling_date(DateTime('2009/06/30')))

        periods.addPeriodLedger(self.ledger.Ledger, EPOCH, ceiling_date(effective))

        self.assertEqual(periods.periodEnds(), [ceiling_date(DateTime('2009/01/01'))])
        self.assertEqual(periods.nextPeriodStart(effective), DateTime('2009/01/02'))
        self.assertEqual(periods.nextPeriodEnd(effective), ceiling_date(DateTime('2010/01/01')))

    def testStartDatesForLedger(self):
        effective = DateTime('2009/01/01')
        periods = self.ledger.periods

        self.assertEqual(periods.lastClosingForLedger('Ledger'), EPOCH)
        self.assertEqual(periods.lastClosingForLedger('Ledger', effective), EPOCH)

        periods.addPeriodLedger(self.ledger.Ledger, EPOCH, effective)

        self.assertEqual(periods.lastClosingForLedger('Ledger'), effective)
        self.assertEqual(periods.lastClosingForLedger('Ledger', effective), effective)
        self.assertEqual(periods.lastClosingForLedger('Ledger', effective+5), effective)

    def testRunReRun(self):
        self.loginAsPortalOwner()

        now = DateTime(self.ledger.timezone)
        pe_tool = self.controller_tool.periodend_tool

        pe_tool.manage_periodEnd(self.ledger, now+1)

        # TODO self.assertRaises(InvalidPeriodError, pe_tool.manage_periodEnd, self.ledger, now+1)

        pe_tool.manage_periodEnd(self.ledger, now+1, force=True)
        #self.assertEqual(len(self.ledger.transactionValues(title='EOP', case_sensitive=True)), 4)

        pe_tool.manage_reset(self.ledger)
        #self.assertEqual(len(self.ledger.transactionValues(title='EOP', case_sensitive=True)), 0)

    def testLossClosingEntries(self):
        self.loginAsPortalOwner()

        ledger = self.portal.ledger
        Ledger = ledger.Ledger

        # hmmm - a couple of expense txns ...
        txn = Ledger.createTransaction(title='My Txn', effective=p1_dt-20)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', '-GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000044', ten)
        txn.manage_post()

        self.assertEqual(Ledger.A000001.openingDate(effective=p1_dt-20), EPOCH)
        self.assertEqual(Ledger.A000001.openingBalance(effective=p1_dt-20), zero)

        self.assertEqual(Ledger.A000001.balance(effective=p1_dt), -ten)
        self.assertEqual(Ledger.A000001.type, 'Asset')  # balance carries over
        self.assertEqual(Ledger.A000044.balance(effective=p1_dt), ten)
        self.assertEqual(Ledger.A000044.type, 'Expense') # need something to close out (insurance exp)

        self.assertEqual(ledger.periods.lastClosingForLedger('Ledger', p1_dt), EPOCH)

        self.assertEqual(ledger.grossProfit(p1_dt), -ten)
        self.assertEqual(ledger.lossesAttributable(p1_dt), zero)
        self.assertEqual(ledger.corporationTax(p1_dt), zero)
        self.assertEqual(ledger.netProfit(p1_dt), -ten)

        self.assertEqual(ledger.lossesAttributable(p1_dt, -ten), zero)
        self.assertEqual(ledger.corporationTax(p1_dt, -ten, zero), zero)
        self.assertEqual(ledger.netProfit(p1_dt, -ten, zero, zero), -ten)

        self.assertEqual(ledger.grossProfit((EPOCH, p1_dt)), -ten)
        self.assertEqual(ledger.lossesAttributable((EPOCH, p1_dt)), zero)
        self.assertEqual(ledger.corporationTax((EPOCH, p1_dt)), zero)
        self.assertEqual(ledger.netProfit((EPOCH, p1_dt)), -ten)


        #######################################################################
        #
        # RUN YEAR END 1
        #
        #######################################################################
        self.controller_tool.periodend_tool.manage_periodEnd(self.ledger, p1_dt, force=False)

        periods = ledger.periods
        pinfo1 = periods.objectValues()[0]
        pinfo1L = pinfo1.Ledger

        self.assertEqual(pinfo1.period_began, EPOCH)
        self.assertEqual(pinfo1.period_ended, ceiling_date(p1_dt))
        self.assertEqual(pinfo1.gross_profit, -ten)
        self.assertEqual(pinfo1.net_profit, -ten)
        self.assertEqual(pinfo1.company_tax, zero)
        self.assertEqual(pinfo1.companyTax(), zero)
        self.assertEqual(pinfo1.losses_forward, ten)
        # alas not yet self.assertEqual(pinfo.lossesForward(), ten)

        self.assertEqual(pinfo1L.numberTransactions(), 2) # closing + tax loss
        # TODO - created date is screwed self.assertEqual(pinfo1L.numberAccounts(), 55)

        self.assertEqual(pinfo1L.balance('A000001'), -ten)
        self.assertEqual(pinfo1L.balance('A000044'), zero) # it's closed out
        self.assertEqual(pinfo1L.reportedBalance('A000044'), ten)


        # TODO self.assertRaises(InvalidPeriodError, periods.periodForLedger, 'Ledger', p1_dt - 367)
        self.assertEqual(periods.periodForLedger('Ledger', p1_dt - 30), None)
        self.assertEqual(periods.periodForLedger('Ledger', p1_dt - 20), None) # official period_began!
        self.assertEqual(periods.periodForLedger('Ledger', p1_dt - 19.5), None)
        self.assertEqual(periods.periodForLedger('Ledger', p1_dt), pinfo1L)
        self.assertEqual(periods.periodForLedger('Ledger', p1_dt + 1), pinfo1L)
        # TODO self.assertRaises(InvalidPeriodError, periods.periodForLedger, 'Ledger', p1_dt - 10)

        self.assertEqual(periods.lastClosingForLedger('Ledger', p1_dt - 1), EPOCH)
        self.assertEqual(periods.lastClosingForLedger('Ledger', p1_dt), ceiling_date(p1_dt))
        self.assertEqual(periods.lastClosingForLedger('Ledger', p1_dt + 1), ceiling_date(p1_dt))

        self.assertEqual(periods.balanceForAccount(p1_dt + 1, 'Ledger', 'A000001'), -ten)
        self.assertEqual(periods.balanceForAccount(p1_dt, 'Ledger', 'A000001'), -ten)
        self.assertEqual(periods.balanceForAccount(p1_dt - 1, 'Ledger', 'A000001'), None) # prev period
        self.assertEqual(periods.balanceForAccount(p1_dt + 1, 'Ledger', 'A000044'), zero)
        self.assertEqual(periods.balanceForAccount(p1_dt, 'Ledger', 'A000044'), zero)
        self.assertEqual(periods.balanceForAccount(p1_dt - 1, 'Ledger', 'A000044'), None)
        self.assertEqual(periods.balanceForAccount(p1_dt - 10, 'Ledger', 'A000044'), None)

        # checked newly cached amounts still compute correct balances for A, L, P's ...
        asset = Ledger.A000001
        # opening bal is always zero (but theres a txn summation from dt - 10)
        self.assertEqual(asset.openingDate(effective=p1_dt - 1), EPOCH)
        self.assertEqual(asset.openingDate(effective=p1_dt - 10), EPOCH)
        self.assertEqual(asset.openingDate(effective=p1_dt - 22), EPOCH)                         
        self.assertEqual(asset.openingDate(effective=p1_dt + 1), p1_dt + 1)
        self.assertEqual(asset.openingDate(effective=p1_dt), p1_dt + 1)

        self.assertEqual(asset.openingBalance(effective=p1_dt + 1), -ten)
        self.assertEqual(asset.openingBalance(effective=p1_dt), -ten)
        self.assertEqual(asset.openingBalance(effective=p1_dt - 1), zero)
        self.assertEqual(asset.openingBalance(effective=p1_dt - 22), zero)

        self.assertEqual(asset.total(effective=(p1_dt - 10,p1_dt)), zero)
        self.assertEqual(asset.total(effective=(p1_dt - 30,p1_dt)), -ten)
        self.assertEqual(asset.total(effective=(p1_dt - 1, p1_dt)), zero)

        self.assertEqual(asset.balance(effective=p1_dt + 1), -ten)
        self.assertEqual(asset.balance(effective=p1_dt), -ten)
        self.assertEqual(asset.balance(effective=p1_dt - 1), -ten)
        self.assertEqual(asset.balance(effective=p1_dt - 10), -ten)
        self.assertEqual(asset.balance(effective=p1_dt - 30), zero)

        loss = Ledger._getOb(self.LOSSFWD_ID)
        retained = Ledger._getOb(self.RETAINED_ID)
        profit = Ledger._getOb(self.PROFIT_ID)
        tax_defr = Ledger._getOb(self.DEFERRED_ID)
        self.failUnless(loss.hasTag('loss_fwd'))
        self.failUnless(retained.hasTag('retained_earnings'))
        self.failUnless(profit.hasTag('profit_loss'))
        self.failUnless(tax_defr.hasTag('tax_defr'))

        self.assertEqual(loss.balance(effective=p1_dt), zero)
        self.assertEqual(loss.balance(effective=p1_dt+1), ten)
        self.assertEqual(retained.balance(effective=p1_dt), zero)
        self.assertEqual(retained.balance(effective=p1_dt+1), zero)
        self.assertEqual(profit.balance(effective=p1_dt-1), zero)
        self.assertEqual(profit.balance(effective=p1_dt), ten)
        self.assertEqual(profit.balance(effective=p1_dt+1), zero)
        self.assertEqual(tax_defr.balance(effective=p1_dt-1), zero)
        self.assertEqual(tax_defr.periods.periodForLedger('Ledger', p1_dt), pinfo1L)

        # tax loss is rolled forward into *next* period
        self.assertEqual(pinfo1L.balance(self.LOSSFWD_ID), zero) # ???
        self.assertEqual(pinfo1L.balance(self.DEFERRED_ID), zero)
        self.assertEqual(pinfo1L.reportedBalance(self.PROFIT_ID), ten) # ???
        self.assertEqual(pinfo1L.reportedBalance(self.RETAINED_ID), zero)
        self.assertEqual(tax_defr.periods.balanceForAccount(p1_dt, 'Ledger', self.DEFERRED_ID), zero)
        self.assertEqual(tax_defr.openingDate(effective=p1_dt), p1_dt + 1)
        self.assertEqual(tax_defr.openingBalance(effective=p1_dt), zero)
        self.assertEqual(tax_defr.balance(effective=p1_dt), zero)
        self.assertEqual(tax_defr.balance(effective=p1_dt+1), zero)

        # TODO self.assertEqual(Ledger.sum(tags='retained_earnings', effective=p1_dt+1), ten)

        self.assertEqual(len(pinfo1L.blTransactions()), 2) # closing + deferred

        # blTransactions is sorted by date (and the deferred is forward-dated)
        closing = pinfo1L.blTransactions()[0]

        self.assertEqual(closing.effective(), floor_date(p1_dt))
        self.assertEqual(closing.debitTotal(), ten)

        self.assertEqual(ledger.lossesAttributable(p1_dt+1, ZCurrency('GBP 50.00')), ten)
        self.assertEqual(ledger.lossesAttributable(p1_dt+1, ZCurrency('GBP 5.00')), ZCurrency('GBP 5.00'))


    def testProfitClosingEntries(self):
        # tests profit + subsidiary ledger balances which have proved problematic
        self.loginAsPortalOwner()

        order_dt = p1_dt - 20

        self.ledger.Inventory.manage_addProduct['BastionLedger'].manage_addBLPart('widget')
        self.widget = self.ledger.Inventory.widget

        ledger = self.ledger.Ledger
        periodend_tool = self.controller_tool.periodend_tool

        income = ledger.accountValues(tags='part_inc')[0]
        self.widget.edit_prices('kilo', 1.5, 5,
                                ZCurrency('GBP20'),
                                ZCurrency('GBP10'),
                                ZCurrency('GBP10'),
                                ledger.accountValues(tags='part_inv')[0].getId(),
                                income.getId(),
                                ledger.accountValues(tags='part_cogs')[0].getId())

        receivables = self.ledger.Receivables
        control = receivables.controlAccounts()[0]

        receivables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        account = receivables.A1000000

        account.manage_addOrder(orderdate=order_dt)
        order = account.objectValues('BLOrder')[0]
        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')
        order.manage_invoice()

        # wtf is the txn??
        self.assertEqual(order.status(), 'invoiced')
        otxn = order.blTransaction()
        self.assertEqual(otxn.status(), 'posted')
        self.assertEqual(otxn.effective(), order_dt)

        self.assertEqual(account.balance(effective=order_dt + 1), twentytwo)
        self.assertEqual(account.balance(effective=order_dt), twentytwo)
        self.assertEqual(account.balance(effective=p1_dt), twentytwo)
        self.assertEqual(control.balance(effective=order_dt + 1), twentytwo)
        self.assertEqual(control.balance(effective=order_dt), twentytwo)
        self.assertEqual(income.balance(effective=order_dt), -twenty)
        self.assertEqual(income.balance(effective=p1_dt), -twenty)

        # hmmm - wierd profit calculations
        self.assertEqual(self.ledger.grossProfit(effective=p1_dt), ten)
        self.assertEqual(self.ledger.grossProfit(effective=(p1_dt-30, p1_dt)), ten)
        self.assertEqual(self.ledger.grossProfit(effective=(p1_dt, p2_dt)), zero)

        self.assertEqual(periodend_tool.reportingInfos(self.ledger, p1_dt), [])

        #######################################################################
        #
        # RUN YEAR END 1
        #
        #######################################################################
        periodend_tool.manage_periodEnd(self.ledger, p1_dt, force=True)

        periods = self.ledger.periods
        pinfo1 = periods.objectValues()[0]
        pinfo1R = pinfo1.Receivables
        pinfo1L = pinfo1.Ledger

        self.assertEqual(periodend_tool.reportingInfos(self.ledger, p1_dt), ['2007-06-30'])

        self.assertEqual(periods.periodForLedger('Receivables', p1_dt+2), pinfo1R)
        # TODO self.assertRaises(InvalidPeriodError, periods.periodForLedger, 'Ledger', p1_dt - 2)

        # TODO self.assertEqual(pinfo1R.numberAccounts(), 1)  # eek 0!!
        self.assertEqual(pinfo1R.numberTransactions(), 1)
        self.assertEqual(pinfo1R.period_began, EPOCH)
        self.assertEqual(pinfo1R.period_ended, ceiling_date(p1_dt))

        self.assertEqual(list(pinfo1R.objectIds()), [account.getId()]) 

        self.assertEqual(pinfo1.gross_profit, ten)
        self.assertEqual(pinfo1.net_profit, ZCurrency('GBP 7.00'))
        self.assertEqual(pinfo1.company_tax, ZCurrency('GBP 3.00'))
        # alas not yet self.assertEqual(pinfoL.companyTax(), ZCurrency('GBP 3.00'))
        self.assertEqual(pinfo1.losses_forward, zero)
        self.assertEqual(pinfo1.lossesForward(), zero)

        self.assertEqual(pinfo1R.balance(account.getId()), twentytwo)
        self.assertEqual(pinfo1L.balance(income.getId()), zero) # it's had closing applied
        self.assertEqual(pinfo1L.balance(control.getId()), twentytwo) # it's had closing applied
        self.assertEqual(periods.balanceForAccount(p2_dt, 'Ledger', income.getId()), zero)
        self.assertEqual(periods.balanceForAccount(p2_dt, 'Ledger', control.getId()), twentytwo)
        self.assertEqual(periods.balanceForAccount(p2_dt, 'Receivables', account.getId()), twentytwo)

        self.assertEqual(len(pinfo1L.blTransactions()), 3) # closing + tax + p&l forward
        self.assertEqual(len(pinfo1R.blTransactions()), 0) # no I or E a/c's

        self.assertEqual(pinfo1L.balance(self.LOSSFWD_ID), zero)
        self.assertEqual(pinfo1L.balance(self.DEFERRED_ID), zero)
        self.assertEqual(pinfo1L.reportedBalance(self.PROFIT_ID), -ZCurrency('GBP 7.00'))
        self.assertEqual(pinfo1L.reportedBalance(self.RETAINED_ID), zero)

        closing = pinfo1L.blTransactions()[0]

        self.assertEqual(closing.effective(), p1_dt)
        #self.assertEqual(closing.debitTotal(), twenty)

        self.assertEqual(ledger.lossesAttributable(p2_dt, ZCurrency('GBP 50.00')), zero)
        self.assertEqual(ledger.lossesAttributable(p2_dt, ZCurrency('GBP 5.00')), zero)

        tax = pinfo1L.blTransactions()[1]

        self.assertEqual(tax.effective(), p1_dt)
        #self.assertEqual(tax.debitTotal(), ZCurrency('GBP 3.00'))

        #######################################################################
        #
        # RUN YEAR END 2
        #
        #######################################################################
        periodend_tool.manage_periodEnd(self.ledger, p2_dt)

        pinfo2 = periods.objectValues()[1]
        pinfo2R = pinfo2.Receivables
        pinfo2L = pinfo2.Ledger

        self.failUnless(pinfo2.period_began > pinfo1.period_ended)
        self.failUnless(pinfo2.period_began - pinfo1.period_ended < 0.00005)

        self.assertEqual(periodend_tool.reportingInfos(self.ledger, p2_dt), ['2007-06-30', '2008-06-30'])

        self.assertEqual(pinfo2R.numberTransactions(), 0) # no txns this period

        self.assertEqual(pinfo2.gross_profit, zero)
        self.assertEqual(pinfo2.net_profit, zero)
        self.assertEqual(pinfo2.company_tax, zero)
        self.assertEqual(pinfo2.companyTax(), zero)
        self.assertEqual(pinfo2.losses_forward, zero)
        self.assertEqual(pinfo2.lossesForward(), zero)

        self.assertEqual(pinfo2R.balance(account.getId()), twentytwo)
        self.assertEqual(pinfo2L.balance(income.getId()), zero)
        self.assertEqual(pinfo2L.balance(control.getId()), twentytwo)
        self.assertEqual(periods.balanceForAccount(p2_dt, 'Ledger', control.getId()), twentytwo)
        self.assertEqual(periods.balanceForAccount(p2_dt, 'Receivables', account.getId()), twentytwo)
        self.assertEqual(periods.balanceForAccount(p2_dt, 'Ledger', income.getId()), zero)

        # now pay the bill ...
        txn = self.ledger.Receivables.createTransaction(effective=p3_dt-10)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', twentytwo)
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(account.getId(),-twentytwo)
        txn.manage_post()

        self.assertEqual(income.balance(effective=p3_dt), zero)
        self.assertEqual(account.balance(effective=p3_dt), zero)

        # first check that *any* delegation actually works ...
        self.assertEqual(self.ledger.Receivables.total(effective=(p2_dt,p3_dt)), -twentytwo)
        entry = control.Receivables
        self.assertEqual(entry.balance(effective=p3_dt), zero)
        self.assertEqual(entry.total(effective=(p2_dt,p3_dt)), -twentytwo)
        self.assertEqual(entry.lastTransactionDate(), p3_dt-10)

        # then verify the call itself ...
        self.assertEqual(control.openingDate(p3_dt), floor_date(p2_dt + 1))
        self.assertEqual(control.openingBalance(p3_dt), twentytwo)
        self.assertEqual(control.balance(effective=p3_dt), zero)
        
        #######################################################################
        #
        # RUN YEAR END 3
        #
        #######################################################################
        periodend_tool.manage_periodEnd(self.ledger, p3_dt)

        pinfo3 = periods.objectValues()[2]
        pinfo3R = pinfo3.Receivables
        pinfo3L = pinfo3.Ledger

        self.failUnless(pinfo3L.period_began > pinfo2L.period_ended)
        self.failUnless(pinfo3L.period_began - pinfo2L.period_ended < 0.00005)

        self.assertEqual(periodend_tool.reportingInfos(self.ledger, p3_dt), 
                         ['2007-06-30', '2008-06-30', '2009-06-30'])

        self.assertEqual(pinfo3R.numberTransactions(), 1) # pmt

        self.assertEqual(pinfo3.gross_profit, zero)
        self.assertEqual(pinfo3.net_profit, zero)
        self.assertEqual(pinfo3.company_tax, zero)
        self.assertEqual(pinfo3.companyTax(), zero)
        self.assertEqual(pinfo3.losses_forward, zero)
        self.assertEqual(pinfo3.lossesForward(), zero)

        self.assertEqual(pinfo3R.balance(account.getId()), zero)
        self.assertEqual(pinfo3L.balance(control.getId()), zero)
        self.assertEqual(periods.balanceForAccount(p3_dt, 'Receivables', account.getId()), zero)

        self.assertEqual(periods.lastClosingForLedger('Ledger', p1_dt - 1), EPOCH)
        self.assertEqual(periods.lastClosingForLedger('Ledger', p2_dt - 1), ceiling_date(p1_dt))
        self.assertEqual(periods.lastClosingForLedger('Ledger', p3_dt - 1), ceiling_date(p2_dt))
        
        # ensure delete removes txns
        tids = map(lambda x: x.getId(), pinfo1.blTransactions())
        self.assertEqual(len(tids), 3)

        self.controller_tool.periodend_tool.manage_reset(self.ledger)
        self.assertEqual(ledger.transactionValues(id=tids), [])

    def testClosingTxnOnEOP(self):
        self.loginAsPortalOwner()

        txn = self.ledger.Ledger.createTransaction(title='My Txn', effective=p1_dt+1)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', '-GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000044', ten)
        txn.manage_post()

        #######################################################################
        #
        # RUN YEAR END 1
        #
        #######################################################################
        self.controller_tool.periodend_tool.manage_periodEnd(self.ledger, p1_dt, force=False)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestPeriodEnd))
    return suite
