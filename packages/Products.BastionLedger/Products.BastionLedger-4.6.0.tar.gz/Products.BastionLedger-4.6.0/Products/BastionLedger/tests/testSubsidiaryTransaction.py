#
#    Copyright (C) 2002-2013  Corporation of Balclutha. All rights Reserved.
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
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import floor_date


class TestSubsidiaryTransaction(LedgerTestCase):
    """
    verify transaction workflow
    """
    def testEntry(self):
        ledger = self.portal.ledger.Receivables

        INDEX_COUNT = len(self.ledger.searchResults())

        ledger.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        dt = DateTime(self.ledger.timezone)

        self.assertEqual(len(self.ledger.searchResults()), INDEX_COUNT + 1)

        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryTransaction(effective=dt)
	txn = ledger._getOb(tid)

        self.assertEqual(len(self.ledger.searchResults()), INDEX_COUNT + 2)

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        self.assertEqual(len(self.ledger.searchResults()), INDEX_COUNT + 3)
        self.assertEqual(txn.total(), ZCurrency('GBP10.00'))

        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry('A1000000', 'GBP -10.00')
        self.assertEqual(len(self.ledger.searchResults()), INDEX_COUNT + 4)
        self.assertEqual(txn.total(), 0)

        glent = txn.blEntry('A000001')
        subent = txn.blEntry('A1000000')

        self.assertEqual(glent.amount, ZCurrency('GBP 10.00'))
        self.assertEqual(glent.ledgerId(), 'Ledger')
        self.assertEqual(glent.accountId(), 'A000001')

        self.assertEqual(subent.amount,-ZCurrency('GBP 10.00'))
        self.assertEqual(subent.ledgerId(), 'Receivables')
        self.assertEqual(subent.accountId(), 'A1000000')

        self.assertEqual(txn.blEntry('A000001', 'Ledger').amount, ZCurrency('GBP 10.00'))
        self.assertEqual(txn.blEntry('A1000000', 'Receivables').amount,-ZCurrency('GBP 10.00'))


    def testMultiCurrencyEntry(self):
        ledger = self.portal.ledger.Receivables
        ledger.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        dt = DateTime(self.ledger.timezone)

        ctl = ledger.controlAccounts()[0]

        self.assertEqual(ctl.balance(effective=dt), ZCurrency('GBP 0.00'))

        # simulate a charge
        txn = ledger.createTransaction(effective=dt)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry('A1000000', 'AUD -25.00')

        self.assertEqual(txn.controlAccount(), ctl)

        self.assertEqual(txn.status(), 'complete')
        self.assertEqual(ctl.balance(effective=dt), ZCurrency('GBP 0.00'))

        txn.manage_post()

        self.assertEqual(ctl.balance(effective=dt), -ZCurrency('GBP 10.00'))
        self.assertEqual(ledger.A1000000.balance(effective=dt), -ZCurrency('GBP 10.00'))
        self.assertEqual(ledger.A1000000.balance(effective=dt, currency='AUD'), -ZCurrency('AUD 25.00'))

        # simulate a payment
        txn = ledger.createTransaction(effective=dt)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', '-GBP 9.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000042', '-GBP 1.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry('A1000000', 'AUD 25.00')

        txn.manage_post()

        fcent = txn.blEntry('A1000000')
        self.assertEqual(fcent.foreignAmount(), ZCurrency('GBP 10.00'))

        self.assertEqual(ledger.A1000000.balance(effective=dt), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.A1000000.balance(effective=dt, currency='AUD'), ZCurrency('AUD 0.00'))
        self.assertEqual(ctl.balance(effective=dt), ZCurrency('GBP 0.00'))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubsidiaryTransaction))
    return suite
