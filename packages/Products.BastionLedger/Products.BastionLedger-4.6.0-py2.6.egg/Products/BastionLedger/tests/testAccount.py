#
#    Copyright (C) 2006-2013  Corporation of Balclutha. All rights Reserved.
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
import unittest
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionLedger.BLGlobals import EPOCH
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import floor_date, lastXDays

from zope import component
from ..interfaces.transaction import IEntry

class TestAccount(LedgerTestCase):
    """
    verify account processing
    """
    def testEmptyStuff(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.assertEqual(account.blLedger(), ledger)
        self.assertEqual(account.openingBalance(), ledger.zeroAmount())
        self.assertEqual(account.openingDate(), EPOCH)

        self.assertEqual(account.base_currency, 'GBP')
        self.assertEqual(account.isFCA(), False)
        self.failUnless(abs(account.created() - DateTime()) < self.RUN_TIME)
        self.assertEqual(account.CreationDate()[:10], self.now.strftime('%Y-%m-%d'))

        self.assertEqual(account.lastTransactionDate(), EPOCH)

    def testGlobalTagStuff(self):
        tax_exp = self.ledger.Ledger.accountValues(tags='tax_exp')[0]
        self.assertEqual(tax_exp.hasTag('tax_exp'), True)
        self.assertEqual(tax_exp.hasTag('tax_accr'), False)

    def testLocalTags(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.assertEqual(account.tags, ())
        self.failIf(account.hasTag('Whippee'))
        self.assertEqual(self.ledger.uniqueValuesFor('tags'), ())

        ledger.manage_addTag('Whippee', [account.accno])

        self.assertEqual(account.tags, ('Whippee',))
        self.assertEqual(self.ledger.uniqueValuesFor('tags'), (u'Whippee',))
        self.failUnless(account.hasTag('Whippee'))
        
    def testAddTag(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        # uniqueValuesFor() implementation ...
        self.assertEqual(self.ledger._catalog.indexes['tags'].uniqueValues(), ())

        self.failIf('tag1' in self.ledger.uniqueValuesFor('tags'))
        account.updateTags('tag1')

        self.failUnless('tag1' in self.ledger.uniqueValuesFor('tags'))
        self.assertEqual(account.hasTag('tag1'), True)

    def testGlobalTagStuff(self):
        # we silently ignore tags defined at global (portal_bastionledger) level
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.assertEqual(account.tags, ())

        ledger.manage_addTag('bank_account', [account.accno])

        self.assertEqual(account.tags, ())
        self.failIf('bank_account' in self.ledger.uniqueValuesFor('tags'))
        
    def testBalanceFunctions(self):
        # we're not doing forward-dated txns ...
        now = DateTime() - 20
        later = now + 5

        ledger = self.ledger.Ledger
        account = ledger.A000001

        # verify internal counters ...
        self.assertEqual(account._balance, ZCurrency('GBP 0.00'))
        self.assertEqual(account._balance_dt, EPOCH)

        ledger.manage_addTag('Whippee', [account.accno])

        txn = ledger.createTransaction(effective=now)
        entryid = txn.createEntry('A000001', 'GBP 10.00')
        txn.createEntry('A000002', '-GBP 10.00')

        #self.assertEqual(component.subscribers(txn.entryValues(), IEntry), None)

        txn.manage_post()

        # verify internal counters ...
        self.assertEqual(account._balance, ZCurrency('GBP 10.00'))
        self.assertEqual(account._balance_dt, floor_date(now))

        txn = ledger.createTransaction(effective=later)
        txn.createEntry('A000001', 'GBP 20.00')
        txn.createEntry('A000002', '-GBP 20.00')
        
        txn.manage_post()

        self.assertEqual(account.lastTransactionDate(), txn.effective_date)

        # verify internal counters ...
        self.assertEqual(account._balance, ZCurrency('GBP 30.00'))
        self.assertEqual(account._balance_dt, floor_date(later))

        # now go hammer balance stuff ...
	self.assertEqual(account.openingDate(), EPOCH)
	self.assertEqual(account.openingDate(now), EPOCH)
	self.assertEqual(account.openingDate(None), EPOCH)
        self.assertEqual(self.ledger.periods.balanceForAccount(now, 'Ledger', account.getId()), None)
	self.assertEqual(account.openingBalance(EPOCH), ZCurrency('GBP 0.00'))
	self.assertEqual(account.openingBalance(now), ZCurrency('GBP 0.00'))
	self.assertEqual(account.openingBalance(), ZCurrency('GBP 0.00'))
        self.assertEqual(len(account.entryValues(effective=(EPOCH, now))), 1)
        self.assertEqual(len(account.entryValues(effective=now)), 1)
        self.assertEqual(len(account.entryValues(effective=(EPOCH, later))), 2)
        self.assertEqual(len(account.entryValues(effective=later)), 2)
        self.assertEqual(len(account.entryValues()), 2)
        self.assertEqual(account.total(effective=(EPOCH, now)), ZCurrency('GBP 10.00'))
        self.assertEqual(account.total(effective=now), ZCurrency('GBP 10.00'))
	self.assertEqual(account.balance(effective=now), ZCurrency('GBP 10.00'))
	self.assertEqual(account.balance(), ZCurrency('GBP 30.00'))
	self.assertEqual(account.balance(effective=later), ZCurrency('GBP 30.00'))

        self.assertEqual(account.debitTotal(effective=now), ZCurrency('GBP 10.00'))
        self.assertEqual(account.debitTotal(effective=[now+2, later]), ZCurrency('GBP 20.00'))
        self.assertEqual(account.creditTotal(effective=now), ZCurrency('GBP 0.00'))
        self.assertEqual(account.creditTotal(effective=now+2), ZCurrency('GBP 0.00'))

        self.assertEqual(ledger.sum(tags='Whippee', effective=now), ZCurrency('GBP 10.00'))

        self.assertEqual(len(account.entryValues((EPOCH, later))), 2)
        self.assertEqual(ledger.sum(tags='Whippee', effective=later), ZCurrency('GBP 30.00'))

        self.assertEqual(len(account.entryValues((now+2, later))), 1)
        self.assertEqual(ledger.sum(tags='Whippee', effective=[now+2, later]), ZCurrency('GBP 20.00'))

        ledger.manage_delObjects([txn.getId()])

        # verify txn manage_unpost has removed entry
        self.assertEqual(len(account.entryValues()), 1)
        entry = account.entryValues()[0]
        self.assertEqual(entry.effective(), floor_date(now))
        self.assertEqual(entry.transactionId(), 'T000000000001')
        self.assertEqual(account.lastTransactionDate(), floor_date(now))

        # verify internal counters ...
        self.assertEqual((account._balance_dt, account._balance),
                         (floor_date(now), ZCurrency('GBP 10.00')))

        self.assertEqual(account.balance(), ZCurrency('GBP 10.00'))


    def testGraphingFunctions(self):
        now = floor_date(DateTime() - 20)
        days = lastXDays(now, 7)
        ledger = self.ledger.Ledger
        account = ledger.A000001
        self.assertEqual(days, [now-6, now-5, now-4, now-3, now-2, now-1, now])
        self.assertEqual(account.balances(days, account.entryValues((now-7, now))), 
                         ['0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00'])

        txn = ledger.createTransaction(effective=now-4)
        entryid = txn.createEntry('A000001', 'GBP 10.00')
        txn.createEntry('A000002', '-GBP 10.00')
        txn.manage_post()

        self.assertEqual(account.balances(days, account.entryValues((now-7, now))), 
                         ['0.00', '0.00', '10.00', '10.00', '10.00', '10.00', '10.00'])

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Ledger
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLAccount/A222222')
        self.failUnless('A222222' in ledger.restrictedTraverse('portal_factory/BLAccount').objectIds())
        A222222 = temp_object.portal_factory.doCreate(temp_object, 'A222222')
        self.failUnless('A222222' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLAccount/A222223')
        self.failUnless('A222223' in ledger.restrictedTraverse('portal_factory/BLAccount').objectIds())
        temp_object.blaccount_edit(title='Foo', 
                                   description='', 
                                   type='Asset', 
                                   subtype='Current Asset', 
                                   currency='GBP',
                                   accno='2222')
        self.failUnless('2222' in self.ledger.uniqueValuesFor('accno'))
        self.assertEqual(ledger.accountValues(accno='2222')[0].title, 'Foo')
        self.failUnless('A222223' in ledger.objectIds())

    def testTaxGroups(self):
        # checking persistence/non-taint of tax_codes dictionary
        self.loginAsPortalOwner()
        ledger = self.ledger.Ledger

        # our placebo
        self.assertEqual(ledger.A000001.tax_codes, {})

        acc = ledger.manage_addProduct['BastionLedger'].manage_addBLAccount('crap', 'AUD', type='Revenue', accno='1234',)

        self.assertEqual(acc.tax_codes, {})

        acc.manage_addTaxCodes('blabla_tax', [])

        self.assertEqual(acc.tax_codes, {'blabla_tax':[]})
        self.assertEqual(ledger.A000001.tax_codes, {})
        
        acc.manage_delTaxGroups(['blabla_tax'])

        self.assertEqual(acc.tax_codes, {})
        self.assertEqual(ledger.A000001.tax_codes, {})

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAccount))
    return suite

if __name__ == '__main__':
    unittest.main()

