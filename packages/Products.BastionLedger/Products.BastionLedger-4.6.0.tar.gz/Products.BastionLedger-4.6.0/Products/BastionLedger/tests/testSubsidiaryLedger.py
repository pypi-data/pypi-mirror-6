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
from LedgerTestCase import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.AdvancedQuery import Between
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import ceiling_date, floor_date
from Products.BastionLedger.BLGlobals import EPOCH

zero = ZCurrency('GBP 0.00')
ten = ZCurrency('GBP 10.00')

class TestSubsidiaryLedger(LedgerTestCase):
    """
    verify transaction workflow
    """
    def CONTROL_ID(self):
        return 'A0000%i' % (self.NUMBER_ACCOUNTS + 1)

    def afterSetUp(self):
        LedgerTestCase.afterSetUp(self)
        self.ledger.manage_addProduct['BastionLedger'].addBLSubsidiaryLedger('junk')
        self.sub = self.ledger.junk
        id = self.sub.manage_addProduct['BastionLedger'].addBLSubsidiaryAccount('bob')
        self.acc = self.sub._getOb(id)

    def testDefaultCurrency(self):
        self.assertEqual(self.sub.defaultCurrency(), 'GBP')
        
    def testCreated(self):
        # the big all-in test ...
        ledger = self.sub
        self.assertEqual(ledger.meta_type, 'BLSubsidiaryLedger')
        self.assertEqual(ledger.currencies, ['GBP'])
        self.failUnless(getattr(ledger, 'portal_workflow', False))

        self.assertEqual(ledger._control_accounts, (self.CONTROL_ID(),))
        self.assertEqual(ledger.controlAccount(self.CONTROL_ID()), self.ledger.Ledger._getOb(self.CONTROL_ID()))

        self.assertEqual(len(ledger.controlAccount(self.CONTROL_ID()).entryValues()), 1)

    def testWorkflow(self):
        ledger = self.sub
        self.loginAsPortalOwner()
        now = DateTime('2010/01/01')

        self.assertEqual(self.acc.balance(), 0)

        txn = ledger.createTransaction(title='My Txn', effective=now)

        self.assertEqual(txn.status(), 'incomplete')

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        self.assertEqual(txn.status(), 'incomplete')

        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(self.acc.getId(), -ten)
        self.assertEqual(txn.debitTotal(), ten)
        self.assertEqual(txn.creditTotal(), -ten)
        self.assertEqual(txn.status(), 'complete')

        txn.content_status_modify(workflow_action='post')
        self.assertEqual(txn.status(), 'posted')
        self.assertEqual(ledger.total(), -ten)

        # ensure it's not trashing the title (and effective date)
        self.assertEqual(txn.Title(), 'My Txn') 

        account = self.ledger.Ledger.A000001

        # test what we think is in the indexes
        glentry = txn.blEntry('A000001')
        self.assertEqual(glentry.transactionId(), txn.getId())
        self.assertEqual(glentry.ledgerId(), 'Ledger')
        self.assertEqual(glentry.accountId(), 'A000001')
        self.assertEqual(glentry.meta_type, 'BLEntry')

        subentry = txn.blEntry(self.acc.getId())
        self.assertEqual(subentry.transactionId(), txn.getId())
        self.assertEqual(subentry.ledgerId(), 'junk')
        self.assertEqual(subentry.accountId(), self.acc.getId())
        self.assertEqual(subentry.meta_type, 'BLSubsidiaryEntry')

        # we should sucessfully search this now ...
        entry = account.blEntry(txn.getId())
        self.failIf(entry is None)

        self.assertEqual(entry.status(), 'posted')
        self.assertEqual(entry.account, account.getId())
        self.assertEqual(entry.blAccount(), account)
        self.assertEqual(entry.blTransaction(), txn)
        #self.assertEqual(entry.getLedger(), self.ledger.Ledger)
        self.assertEqual(entry.effective(), txn.effective())
        self.assertEqual(entry.amount, ten)
        self.assertEqual(entry.isControlEntry(), False)

        self.assertEqual(list(account.entryIds()), [txn.getId()])

	self.assertEqual(account.openingDate(), EPOCH)
	self.assertEqual(account.openingDate(now), EPOCH)
        self.assertEqual(self.ledger.periods.balanceForAccount(now, self.sub.getId(), account.getId()), None)
	self.assertEqual(account.openingBalance(EPOCH), ZCurrency('GBP 0.00'))
	self.assertEqual(account.openingBalance(now), ZCurrency('GBP 0.00'))
	self.assertEqual(account.openingBalance(), ZCurrency('GBP 0.00'))
        self.assertEqual(account.entryValues(now), [entry])
        self.assertEqual(account.entryValues([now - 2, now + 1]), [entry])        
        self.assertEqual(account.entryValues(), [entry])        
        self.assertEqual(account.sum(self.acc.getId()), -ten)
        self.assertEqual(account.sum(self.acc.getId(), debits=False), -ten)
        self.assertEqual(account.sum(self.acc.getId(), credits=False), zero)
	self.assertEqual(account.balance(), ten)
	self.assertEqual(account.balance(effective=now), ten)

        self.assertEqual(entry, txn.blEntry(account.getId()))
                         
	self.assertEqual(self.acc.balance(), -ten)

        self.assertEqual(len(account.entryValues()), 1)
        self.assertEqual(len(self.acc.entryValues()), 1) #  entry

	# TODO
        #txn.content_status_modify(workflow_action='reverse')
	reversal_txn = txn.manage_reverse()

	self.assertEqual(txn.status(), 'reversed')
        self.assertEqual(txn.effective_date, now)

        self.assertEqual(reversal_txn, txn.referenceObject())

        #reversal_txn = txn.referenceObject()

        self.assertEqual(reversal_txn.status(), 'postedreversal')
        self.assertEqual(reversal_txn.meta_type, 'BLSubsidiaryTransaction')
        self.assertEqual(reversal_txn.effective_date, txn.effective_date)

        self.assertEqual(len(account.entryValues()), 0)
        self.assertEqual(len(account.entryValues(status=['postedreversal'])), 1)
        self.assertEqual(len(account.entryValues(status=['reversed'])), 1)
        self.assertEqual(len(self.acc.entryValues()), 0)

        self.assertEqual(len(self.acc.entryValues([now - 2, now + 1])), 0)
        self.assertEqual(self.acc.total([now - 2, now + 1]), 0)        

	self.assertEqual(self.acc.balance(), 0)
	#self.assertEqual(self.ledger.Ledger.A000001.balance(), 0)
	self.assertEqual(account.balance(), 0)
        self.assertEqual(ledger.total(), zero)


    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.sub

        temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryAccount/crap')
        self.failUnless('crap' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryAccount').objectIds())
        SL000002 = temp_object.portal_factory.doCreate(temp_object, 'SL000002')
        self.failUnless('SL000002' in ledger.objectIds())
 

        # doCreate should create the real object
        dt = DateTime('2000/01/01')
        temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction/T000000000099')
        self.failUnless('T000000000099' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction').objectIds())
        A222222 = temp_object.portal_factory.doCreate(temp_object, 'T000000000099')
        self.failUnless('T000000000099' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction/T000000000100')
        self.failUnless('T000000000100' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction').objectIds())
        temp_object.bltransaction_edit(title='Foo', effective=dt)
        self.assertEqual(ledger.transactionValues(effective=dt)[0].title, 'Foo')
        self.failUnless('T000000000100' in ledger.objectIds())
        
    def testControlBalance(self):
        ledger = self.sub

        self.loginAsPortalOwner()
        txn = ledger.createTransaction(title='My Txn', effective=DateTime('2007/07/02'))
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(self.acc.getId(), -ten)
        txn.content_status_modify(workflow_action='post')

        control = ledger.controlEntry(self.CONTROL_ID())
        a000001 = ledger.Ledger.A000001
        control_ac = ledger.Ledger._getOb(self.CONTROL_ID())

        self.assertEqual(control.effective(), None)
        self.assertEqual(control.isControlEntry(), True)
        self.assertEqual(control.lastTransactionDate(), DateTime('2007/07/02'))
        self.assertEqual(control.controlAccount(self.CONTROL_ID()), control_ac)
        self.assertEqual(control_ac.type, 'Asset') # assure doesn't close out to zero

        self.assertEqual(a000001.openingDate(DateTime('2007/06/30')), EPOCH)
        self.assertEqual(a000001.openingBalance(DateTime('2007/06/30')), zero)
        self.assertEqual(a000001.balance(effective=DateTime('2007/06/30')), zero)

        self.assertEqual(a000001.openingBalance(DateTime('2007/07/01')), zero)
        self.assertEqual(a000001.balance(effective=DateTime('2007/07/01')), zero)
        self.assertEqual(a000001.balance(effective=DateTime('2007/07/02')), ten)

        self.assertEqual(self.acc.balance(effective=DateTime('2007/06/30')), zero)
        self.assertEqual(self.acc.balance(effective=DateTime('2007/07/01')), zero)
        self.assertEqual(self.acc.balance(effective=DateTime('2007/07/02')), -ten)

        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2007/06/30'))), zero)
        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2007/07/01'))), zero)
        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2007/07/02'))), -ten)
        self.assertEqual(ledger.total(effective=(DateTime('2006/06/30'), DateTime('2007/07/02'))), 
                         -ten)
        
        self.assertEqual(control.balance(), -ten)
        self.assertEqual(control.balance(effective=DateTime('2007/06/30')), zero)
        self.assertEqual(control.balance(effective=DateTime('2007/07/01')), zero)
        self.assertEqual(control.balance(effective=DateTime('2007/07/02')), -ten)
        self.assertEqual(control.balance(effective=(DateTime('2006/06/30'), DateTime('2007/07/02'))), 
                         -ten)

        ###################################################################################
        #
        # make sure that it's all still kosher after a period end ...
        #
        ###################################################################################
        ledger.manage_periodEnd(DateTime('2007/06/30'))

        self.assertEqual(a000001.openingDate(DateTime('2007/06/30')), DateTime('2007/07/01'))
        self.assertEqual(a000001.openingBalance(DateTime('2007/06/30')), zero)
        self.assertEqual(a000001.balance(effective=DateTime('2007/06/30')), zero)

        self.assertEqual(a000001.balance(effective=DateTime('2007/07/01')), zero)
        self.assertEqual(a000001.balance(effective=DateTime('2007/07/02')), ten)

        self.assertEqual(self.acc.balance(effective=DateTime('2007/06/30')), zero)
        self.assertEqual(self.acc.balance(effective=DateTime('2007/07/01')), zero)
        self.assertEqual(self.acc.balance(effective=DateTime('2007/07/02')), -ten)

        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2007/06/30'))), zero)
        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2007/07/01'))), zero)
        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2007/07/02'))), -ten)
        
        ###############################################################################
        #
        # do another year-end and ensure opening balance/cache entries work
        #
        ###############################################################################
        ledger.manage_periodEnd(DateTime('2008/06/30'))

        self.assertEqual(a000001.openingDate(DateTime('2007/06/30')), DateTime('2007/07/01'))
        self.assertEqual(a000001.openingBalance(DateTime('2007/06/30')), zero)
        self.assertEqual(a000001.balance(effective=DateTime('2007/06/30')), zero)

        self.assertEqual(a000001.openingDate(DateTime('2008/06/30')), DateTime('2008/07/01'))
        self.assertEqual(self.ledger.periods.periodForLedger('Ledger', DateTime('2008/06/30')).aq_parent.getId(), '2008-06-30')
        self.assertEqual(a000001.openingBalance(DateTime('2008/06/30')), ten)
        self.assertEqual(a000001.balance(effective=DateTime('2008/06/30')), ten)
        self.assertEqual(a000001.balance(effective=DateTime('2008/07/02')), ten)

        self.assertEqual(self.acc.balance(effective=DateTime('2007/06/30')), zero)
        self.assertEqual(self.acc.balance(effective=DateTime('2008/06/30')), -ten)
        self.assertEqual(self.acc.balance(effective=DateTime('2008/07/02')), -ten)

        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2007/06/30'))), zero)
        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2008/06/30'))), -ten)
        self.assertEqual(ledger.total(effective=(EPOCH, DateTime('2008/07/02'))), -ten)


    def testMultiControls(self):
        ledger = self.sub
        self.loginAsPortalOwner()
        ledger.manage_changeControl(['A000054', 'A000055'])

        self.assertEqual(ledger.controlAccounts(), 
                         [self.ledger.Ledger.A000054, self.ledger.Ledger.A000055])

        c54 = ledger.controlAccount('A000054')
        c55 = ledger.controlAccount('A000055')

        self.assertEqual(c54.controlEntry(ledger.getId()).amount, zero)
        self.assertEqual(c55.controlEntry(ledger.getId()).amount, zero)

        t54 = ledger.createTransaction(title='T1/54', effective=DateTime('2007/07/02'), control='A000054')
        t54.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        t54.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(self.acc.getId(), -ten)
        t54.content_status_modify(workflow_action='post')

        self.assertEqual(c54.controlEntry(ledger.getId()).amount, -ten)
        self.assertEqual(c55.controlEntry(ledger.getId()).amount, zero)

        t55 = ledger.createTransaction(title='T2/55', effective=DateTime('2007/07/02'), control='A000055')
        t55.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        t55.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(self.acc.getId(), -ten)
        t55.content_status_modify(workflow_action='post')

        self.assertEqual(t54._control_account, 'A000054')
        self.assertEqual(t55._control_account, 'A000055')

        self.failUnless(c54.isControl())
        self.failUnless(c55.isControl())
        self.assertEqual(c54.controlLedgers()[0], ledger)
        self.assertEqual(c55.controlLedgers()[0], ledger)
        self.assertEqual(t54.controlAccount(), c54)
        self.assertEqual(t55.controlAccount(), c55)
        self.assertEqual(c54, self.ledger.Ledger.A000054)
        self.assertEqual(c55, self.ledger.Ledger.A000055)

        self.assertEqual(self.acc.balance(), -ten * 2)
        self.assertEqual(self.ledger.Ledger.A000001.balance(), ten * 2)

        # BLControlEntry totals filter
        self.assertEqual(filter(lambda x: x._control_account == 'A000054',
                                ledger.transactionValuesAdv(Between('effective', EPOCH, DateTime('2007/12/31')))), [t54])
        self.assertEqual(t54.objectValues('BLSubsidiaryEntry')[0].amount, -ten)
        self.assertEqual(self.portal.portal_bastionledger.addCurrencies([(-ten, DateTime('2007/07/02'))], 'GBP'), -ten)

        self.assertEqual(c54.controlEntry(ledger.getId()), self.ledger.Ledger.A000054.junk)
        self.assertEqual(c55.controlEntry(ledger.getId()), self.ledger.Ledger.A000055.junk)

        self.assertEqual(c54.controlEntry(ledger.getId()).amount, -ten)
        self.assertEqual(c54.controlEntry(ledger.getId()).total(), -ten)

        self.assertEqual(c54.controlEntry(ledger.getId()).balance(), -ten)
        self.assertEqual(c55.controlEntry(ledger.getId()).balance(), -ten)

        self.assertEqual(c54.balance(), -ten)
        self.assertEqual(c55.balance(), -ten)

        #self.assertEqual([str(t54), str(t55)], [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubsidiaryLedger))
    return suite
