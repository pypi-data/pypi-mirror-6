#
#    Copyright (C) 2008-2013  Corporation of Balclutha. All rights Reserved.
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

from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase
from Products.BastionLedger.BLAssociations import ASSOCIATIONS
from Products.AdvancedQuery import Eq

# copying/pasting etc (indexing takes a long time)
ALL_TESTS = False

class TestLedger(LedgerTestCase):
    """
    verify Ledger processing
    """
    def testDefaultCurrency(self):
        self.assertEqual(self.ledger.Ledger.defaultCurrency(), 'GBP')

    def testBatchMacros(self):
        # context/batch_macros/macros/navigation ...
        macros = self.ledger.restrictedTraverse('batch_macros')
        macros = self.ledger.Ledger.restrictedTraverse('batch_macros')
        # whippee ...

    def testNoSearchResultsDups(self):
        # tests that indexes have been restored after copy ...
        ledger = self.ledger.Ledger
        self.assertEqual(ledger.accountValues(accno=('2155',)), [ledger._getOb(self.SALESTAX_ID)])
    

    def testGlobalTags(self):
        ledger = self.ledger.Ledger

        self.assertEqual(map(lambda x: x.getId(),
                             ledger.accountValues(tags='sales_tax_due')), [self.SALESTAX_ID])

    def testLocalTags(self):
        ledger = self.ledger.Ledger

        self.failIf('crap1' in self.ledger.uniqueValuesFor('tags'))

        # office furniture and equipment
        ledger.manage_addTag('crap1', ['1820'])

        self.failUnless('crap1' in self.ledger.uniqueValuesFor('tags'))

        new_tags = ledger.itsAssociations()

        #self.assertEqual(len(filter(lambda x: not x['global'], new_tags)), 1)

        self.assertEqual(len(ledger.accountValues(tags='crap1')), 1)
        self.assertEqual(map(lambda x: x.getId(), ledger.accountValues(tags='crap1')),
                         map(lambda x: x.getId(), ledger.accountValues(accno='1820')))

    def testLocalAddInGlobal(self):
        ledger = self.ledger.Ledger
        
        self.failIf('sales_tax_due' in self.ledger.uniqueValuesFor('tags'))
        ledger.manage_addTag('sales_tax_due', ['1820'])
        self.failIf('sales_tax_due' in self.ledger.uniqueValuesFor('tags'))

    def testAccountSearchTagAware(self):
        ledger = self.ledger.Ledger
        self.assertEqual(map(lambda x: x.getId(),
                             ledger.accountValues(tags='sales_tax_due')), [self.SALESTAX_ID])

    def testAccountValues(self):
        ledger = self.ledger.Ledger
        account = ledger.accountValues()[0]
        self.assertEqual(len(ledger.accountValues()), self.NUMBER_ACCOUNTS)
        self.assertEqual(map(lambda x: x.getId(),
                             ledger.accountValues(tags='sales_tax_due')), [self.SALESTAX_ID])

        self.assertEqual(map(lambda x: x.getId(),
                             ledger.accountValues(accno=account.accno)), [account.getId()])
        

    def testAccountValuesAdv(self):
        ledger = self.ledger.Ledger
        account = ledger.accountValues()[0]

        self.assertEqual(ledger.accountValuesAdv(Eq('accno', account.accno)), [account])

        # a more advanced query ...
        self.failIf(account in ledger.accountValuesAdv(Eq('type', account.type) & ~Eq('accno', account.accno)))
        
        # new summation/totalling stuff
        self.assertEqual(len(ledger.accountValues(type='Asset')), self.NUMBER_ASSETS)
        self.assertEqual(len(ledger.accountValuesAdv(Eq('type', 'Asset'))), self.NUMBER_ASSETS)

    def testRenameTag(self):
        ledger = self.ledger.Ledger

        account = ledger.accountValues(accno='1820')[0]

        ledger.manage_addTag('crap2', ['1820'])
        ledger.manage_renameTags(['crap2'], 'crap3')

        self.assertEqual(account.accno, '1820')
        self.failIf('crap2' in account.tags)
        self.failUnless('crap3' in account.tags)

    def testVerifyVerifies(self):
        self.loginAsPortalOwner()
        self.assertEqual(self.ledger.verifyExceptions(), None)

    if ALL_TESTS:
        def testCopyPaste(self):
            self.loginAsPortalOwner()
            self.portal.manage_addProduct['OFSP'].manage_addFolder('copies')
            self.portal.copies.manage_pasteObjects(self.portal.manage_copyObjects('ledger'))
            self.failUnless(self.portal.copies.ledger)

        def testPortalFactoryCreation(self):
            self.loginAsPortalOwner()
            temp_object = self.portal.restrictedTraverse('portal_factory/Ledger/new_ledger1')
            self.failUnless('new_ledger1' in self.portal.restrictedTraverse('portal_factory/Ledger').objectIds())
            new_ledger1 = temp_object.portal_factory.doCreate(temp_object, 'new_ledger1')
            self.failUnless('new_ledger1' in self.portal.objectIds())
 
            # document_edit should create the real object
            temp_object = self.portal.restrictedTraverse('portal_factory/Ledger/new_ledger2')
            temp_object.blledger_edit('Ledger 2', 'USD', 'EST')
            self.failUnless('new_ledger2' in self.portal.objectIds())
        
    def _X_testXML(self):
        xml = str(self.ledger.asXML())
        
        #self.assertEqual(xml, '')
        self.assertEqual(self.ledger.parseXML(xml), '')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestLedger))
    return suite
