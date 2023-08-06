#
#    Copyright (C) 2002-2014  Corporation of Balclutha. All rights Reserved.
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

from LedgerTestCase import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.BLGlobals import EPOCH
from Products.BastionLedger.utils import add_seconds, floor_date

class TestOrderBook(LedgerTestCase):

    def afterSetUp(self):
        LedgerTestCase.afterSetUp(self)
        self.loginAsPortalOwner()
        self.ledger.Inventory.manage_addProduct['BastionLedger'].manage_addBLPart('widget')
        self.widget = self.ledger.Inventory.widget
        ledger = self.ledger.Ledger
        self.widget.edit_prices('kilo', 1.5, 5,
                                ZCurrency('GBP20'),
                                ZCurrency('GBP10'),
                                ZCurrency('GBP10'),
                                ledger.accountValues(tags='part_inv')[0].getId(),
                                ledger.accountValues(tags='part_inc')[0].getId(),
                                ledger.accountValues(tags='part_cogs')[0].getId())
        
    def testCreated(self):
        # the big all-in test ...
        for ledger in ('Receivables', 'Payables'):
            ob = getattr(self.ledger, ledger)
            self.assertEqual(ob.meta_type, 'BLOrderBook')

    def testReceivableProcess(self):

	price = ZCurrency('GBP20')

        receivables = self.ledger.Receivables

        self.assertEqual(receivables.isReceivable(), True)
        self.assertEqual(receivables.isPayable(), False)

        receivables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading', 
                                                                                contact='John Doe',
                                                                                email='j.doe@acme.com')
        account = receivables.A1000000

        self.assertEqual(account.blLedger(), receivables)
        self.assertEqual(account.email, 'j.doe@acme.com')
        self.assertEqual(account.contact, 'John Doe')

        controlAccount = receivables.controlAccounts()[0]
        self.assertEqual(controlAccount, self.ledger.Ledger._getOb(self.RECEIVABLES_CTL))
        
        controlEntry = receivables.controlEntry(controlAccount.getId())
        self.assertEqual(controlEntry.aq_parent, controlAccount)
        self.assertEqual(receivables, controlEntry.blLedger())
        
        orderdate = DateTime('2008/03/04')
        account.manage_addOrder(orderdate=orderdate)
        order = account.objectValues('BLOrder')[0]

        self.assertEqual(order.isBuy(), False)
        self.assertEqual(order.isSell(), True)

        self.assertEqual(order.status(), 'incomplete')
        self.assertEqual(order.orderdate, orderdate)
        self.assertEqual(order.taxincluded, False)
        self.assertEqual(order.contact, 'John Doe')
        self.assertEqual(order.email, 'j.doe@acme.com')

        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')
        self.assertEqual(order.status(), 'open')

	self.loginAsPortalOwner()
        order.content_status_modify(workflow_action='invoice')
        self.assertEqual(order.getGross(), price)
        self.assertEqual(order.status(), 'invoiced')        

        txn = order.blTransaction()
        self.failUnless(txn)
        self.assertEqual(txn.debitTotal(), ZCurrency('GBP32'))  # hmmm - how *did* we get 32 ...
        self.assertEqual(txn.creditTotal(), ZCurrency('-GBP32'))  # hmmm - how *did* we get 32 ...
        self.assertEqual(txn.status(), 'posted')
        self.assertEqual(txn.effective(), orderdate)

        # test all order postings ...
        self.assertEqual(len(txn.entryValues()),5)

        entry = account.blEntry(txn.getId())
        self.assertEqual(entry.status(), 'posted')
        self.assertEqual(entry.account, account.getId())
        self.assertEqual(entry.blAccount(), account)
        self.assertEqual(entry.blTransaction(), txn)
        self.assertEqual(entry.blLedger(), self.ledger.Receivables)
        self.assertEqual(entry.effective(), txn.effective())
        self.assertEqual(entry.amount, price * 1.1)
        self.assertEqual(entry.isControlEntry(), False)

        self.assertEqual(account.entryValues(), [entry])

        self.assertEqual(account.entryValues([orderdate - 1, orderdate + 1]), [entry])        
	self.assertEqual(account.balance(), price * 1.1)

	order.content_status_modify(workflow_action='cancel')
        self.assertEqual(order.status(), 'cancelled')        
	self.assertEqual(txn.status(), 'reversed')
	self.assertEqual(account.balance(), 0)


    def testPayableProcess(self):

        payables = self.ledger.Payables

        self.assertEqual(payables.isReceivable(), False)
        self.assertEqual(payables.isPayable(), True)

        id = payables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        account = payables._getOb(id)
        self.assertEqual(account.meta_type, 'BLOrderAccount')

        order = account.manage_addOrder()

        self.assertEqual(order.meta_type, 'BLOrder')
        self.assertEqual(order.isBuy(), True)
        self.assertEqual(order.isSell(), False)

        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')

        order.manage_invoice()
        self.assertEqual(order.getGross(), ZCurrency('GBP10'))
        self.assertEqual(account.openingDate(None), EPOCH)
        self.assertEqual(account.openingBalance(), ZCurrency('GBP 0.00'))
        self.assertEqual(account.openingBalance(EPOCH-1), ZCurrency('GBP 0.00'))
        self.assertEqual(len(account.entryValues(effective=self.now)), 1)
        self.assertEqual(len(account.entryValues(effective=(EPOCH, self.now))), 1)
        self.assertEqual(account.total(effective=self.now-2), ZCurrency('GBP 0.00'))
        self.assertEqual(account.total(effective=(EPOCH, self.now)), -ZCurrency('GBP 11.00'))
        self.assertEqual(account.total(effective=(EPOCH, self.now+1)), -ZCurrency('GBP 11.00'))
        self.assertEqual(account.total(currency='GBP'), -ZCurrency('GBP 11.00'))
        #self.assertEqual(account.entryValues(), 0)
	self.assertEqual(account.balance(), -ZCurrency('GBP 11.00'))

        txn = order.blTransaction()

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP11'))
        self.assertEqual(txn.creditTotal(), ZCurrency('-GBP11'))

	order.content_status_modify(workflow_action='cancel')
        self.assertEqual(order.status(), 'cancelled')        
	self.assertEqual(txn.status(), 'reversed')
	self.assertEqual(account.balance(), 0)
	self.assertEqual(txn.status(), 'reversed')

        # this seems to hang ...
        account.createObject(type_name='BLOrder')

    def testReceivablesDiscount(self):
        receivables = self.ledger.Receivables
        receivables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        account = receivables.A1000000
        account.manage_addOrder(discount=10.0)
        order = account.objectValues('BLOrder')[0]
        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')
        orderitem = order.objectValues('BLOrderItem')[-1]

        self.assertEqual(order.discount, 0.1)
        self.assertEqual(orderitem.discount, 0.0)
        self.assertEqual(orderitem.unit, ZCurrency('GBP 20.00'))
        self.assertEqual(orderitem.quantity, 1)
        self.assertEqual(orderitem.amount, None)
        
        self.assertEqual(orderitem.calculateGrossPrice(), ZCurrency('GBP 20.00'))
        self.assertEqual(orderitem.calculateNetPrice(), ZCurrency('GBP 18.00'))

        self.assertEqual(order.getGross(), ZCurrency('GBP 20.0'))
	self.assertEqual(order.getDiscount() ,ZCurrency('GBP 2.00'))
	self.assertEqual(order.getTax(), ZCurrency('GBP 1.80') )
	self.assertEqual(order.getNet(), ZCurrency('GBP 19.80'))

        # check that the txn is complete (less Sales)
        order.manage_invoice()

        self.assertEqual(orderitem.amount, ZCurrency('GBP 18.00'))

    def testPayablesDiscount(self):
        payables = self.ledger.Payables
        payables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        account = payables.A1000000
        account.manage_addOrder(discount=10.0)
        order = account.objectValues('BLOrder')[0]
        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')

        self.assertEqual(order.discount, 0.1)

        # should be
        # CR Supplier                GBP 9.90
        # DR Inventory     GBP 9.00
        # DR Tax           GBP 0.90
        self.assertEqual(order.getGross(), ZCurrency('GBP 10.0'))
	self.assertEqual(order.getDiscount(), ZCurrency('GBP 1.00'))
        self.assertEqual(order.getTax(), ZCurrency('GBP 0.90'))
	self.assertEqual(order.getNet(), ZCurrency('GBP 9.90'))

        # check that the txn is complete (less Inventory)
        order.manage_invoice()


    def testCashBookBuy(self):

        self.ledger.manage_addProduct['BastionLedger'].manage_addBLCashBook('test', 'A000001', 'Inventory')
        cashbook = self.ledger.test
        account = cashbook.CASH

        self.assertEqual(account.blLedger(), cashbook)

        self.assertEqual(account.meta_type, 'BLCashAccount')
        self.assertEqual(account.tax_codes.keys(), ['sales_tax'])

        order = account.manage_addOrder('test', buysell='buy')

        self.assertEqual(order.isBuy(), True)
        self.assertEqual(order.isSell(), False)

        self.assertEqual(order.meta_type, 'BLCashOrder')
        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')
        self.assertEqual(order.getGross(), ZCurrency('GBP10'))

    def testCashBookSell(self):

        self.ledger.manage_addProduct['BastionLedger'].manage_addBLCashBook('test', 'A000001', 'Inventory')
        cashbook = self.ledger.test
        account = cashbook.CASH
        self.assertEqual(account.meta_type, 'BLCashAccount')
        order = account.manage_addOrder('test',buysell='sell')

        self.assertEqual(order.isBuy(), False)
        self.assertEqual(order.isSell(), True)

        self.assertEqual(order.meta_type, 'BLCashOrder')
        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')
        self.assertEqual(order.getGross(), ZCurrency('GBP20'))

    def testCrossCurrencyOrder(self):

        if self.portal_currencies:
            portal_currencies = self.portal_currencies

            receivables = self.ledger.Receivables

            self.assertEqual(receivables.controlAccounts()[0].base_currency, 'GBP')
            self.assertEqual(receivables.defaultCurrency(), 'GBP')

            id = receivables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading', currency='AUD')
            account = receivables._getOb(id)
            order = account.manage_addOrder()
            order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')
            self.assertEqual(order.getGross(), ZCurrency('AUD 50.00'))

            self.assertEqual(account.balance(), ZCurrency('AUD 0.00'))
            order.manage_invoice()

            txn = order.blTransaction()

            self.assertEqual(txn.isMultiCurrency(), True)

            # _stamp() requirements ...
            self.assertEqual(txn.effective_date, floor_date(DateTime()))
            self.failIf(txn.effective_date < account.openingDate())

            self.assertEqual((account._balance, account._balance_dt),
                             (ZCurrency('GBP 22.00'), floor_date(DateTime())))

            self.assertEqual(account.balance(), ZCurrency('AUD 55.00'))

            entry = account.entryValues()[-1]
            self.assertEqual(entry.amount, ZCurrency('AUD 55.00'))

            self.assertEqual(entry.amountAs('AUD'), ZCurrency('AUD 55.00'))
            self.assertEqual(entry.amountAs('GBP'), ZCurrency('GBP 22.00'))

            # assure underlying representation
            self.assertEqual(entry.posted_amount, ZCurrency('GBP 22.00'))
            self.assertEqual(entry.fx_rate, 2.5)

            # and all postings are correct for fx ...
            self.assertEqual(self.ledger.verifyExceptions(), None)

            # ensure re-posting doesn't f**k anything up ...
            txn = entry.blTransaction()
            txn.manage_repost(force=True)

            entry = account.blEntry(txn.getId())

            self.assertEqual(entry.posted_amount, ZCurrency('GBP 22.00'))
            self.assertEqual(entry.fx_rate, 2.5) 


    def testPortalFactoryAccountCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Receivables
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLOrderAccount/S222222')
        self.failUnless('S222222' in ledger.restrictedTraverse('portal_factory/BLOrderAccount').objectIds())
        S222222 = temp_object.portal_factory.doCreate(temp_object, 'S222222')
        self.failUnless('S222222' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLOrderAccount/S222223')
        self.failUnless('S222223' in ledger.restrictedTraverse('portal_factory/BLOrderAccount').objectIds())
        temp_object.blaccount_edit(title='Foo', 
                                   description='', 
                                   type='Asset', 
                                   subtype='Current Asset',
                                   currency='GBP',
                                   accno='2222')
        self.failUnless('2222' in self.ledger.uniqueValuesFor('accno'))
        self.assertEqual(ledger.accountValues(accno='2222')[0].title, 'Foo')
        self.failUnless('S222223' in ledger.objectIds())

        # doCreate should create the real object
        dt = DateTime('2000/01/01')
        ##temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction/T000000000099')
        ##self.failUnless('T000000000099' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction').objectIds())
        ##S222222 = temp_object.portal_factory.doCreate(temp_object, 'T000000000099')
        ##self.failUnless('T000000000099' in ledger.objectIds())
 
        # document_edit should create the real object
        ##temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction/T000000000100')
        ##self.failUnless('T000000000100' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction').objectIds())
        ##temp_object.bltransaction_edit(title='Foo', effective=dt)
        ##self.failUnless('T000000000100' in ledger.objectIds())
        
        
    def testPortalFactoryOrderCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Receivables

        ledger.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading', currency='AUD')
        account = ledger.A1000000

        temp_object = account.restrictedTraverse('portal_factory/BLOrder/AR0000000099')
        self.failUnless('AR0000000099' in account.restrictedTraverse('portal_factory/BLOrder').objectIds())

        self.failUnless(abs(temp_object.created()-self.now) < self.RUN_TIME)

        dt = DateTime('2000/01/01')

        temp_object.blorder_edit(dt, dt)
        self.failUnless('AR0000000099' in account.objectIds())

    def testPortalFactoryCashBookCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLCashBook/cash1')
        self.failUnless('cash1' in ledger.restrictedTraverse('portal_factory/BLCashBook').objectIds())
        cash1 = temp_object.portal_factory.doCreate(temp_object, 'cash1')
        self.failUnless('cash1' in ledger.objectIds())
 
    def testPortalFactoryOrderBookCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLOrderBook/cash1')
        self.failUnless('cash1' in ledger.restrictedTraverse('portal_factory/BLOrderBook').objectIds())
        cash1 = temp_object.portal_factory.doCreate(temp_object, 'cash1')
        self.failUnless('cash1' in ledger.objectIds())
 
    def testOrderToAccount(self):
        payables = self.ledger.Payables
        payables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        account = payables.A1000000
        account.manage_addOrder(discount=10.0)
        order = account.objectValues('BLOrder')[0]
        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')

        acc2 = order.upgradeToAccount('Payables')
        self.assertEqual(acc2.getId(), 'A1000001')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOrderBook))
    return suite
