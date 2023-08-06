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
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase
import math
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.BLAssetRegister import BLAsset, EPOCH

dtrange = (DateTime('2006/01/01'), DateTime('2006/12/31'))

class TestDepreciationTool(LedgerTestCase):

    # TODO - fix up this timezone error!!!

    def afterSetUp(self):
        LedgerTestCase.afterSetUp(self)
        asset = self.portal.asset = BLAsset('asset', 'Asset','', DateTime('2006/01/01'), ZCurrency('GBP1000'), 'A000006', 'Prime Cost', 1, [])
        # fudge timezone ...
        asset.timezone = 'EST'

    def testAmountBeforePurchaseDate(self):
        self.assertEqual(self.portal.asset.depreciation((EPOCH, dtrange[0] - 1)), ZCurrency('GBP 0.00'))

    def testZeroHistCostDay(self):
        self.assertEqual(self.portal.asset.zeroValueDate(), DateTime('2007/01/01'))

    def testDepreciationDays(self):
        self.assertEqual(self.portal.asset.depreciationDays(dtrange), 365)

    def testPrimeCost(self):
        self.assertEqual(self.portal.asset.depreciation(dtrange), ZCurrency('GBP1000'))
        self.portal.asset._updateProperty('effective_life', 2)
        self.assertEqual(self.portal.asset.purchase_date, DateTime('2006/01/01'))
        self.assertEqual(min(DateTime('2008/01/01'), DateTime('2007/01/01')), DateTime('2007/01/01'))
        self.assertEqual(self.portal.asset.zeroValueDate(), DateTime('2008/01/01'))
        self.assertEqual(self.portal.asset.depreciationDays(dtrange), 365)
        self.assertEqual(self.portal.asset.depreciation(dtrange), ZCurrency('GBP500'))
        
    def testDiminishingRate(self):
        self.portal.asset._updateProperty('depreciation_method', 'Diminishing Value')
        self.assertEqual(self.portal.asset.depreciation(dtrange), ZCurrency('GBP1000'))
        self.portal.asset._updateProperty('effective_life', 2)
        self.assertEqual(self.portal.asset.zeroValueDate(), DateTime('2008/01/01'))
        self.assertEqual(self.portal.asset.depreciationDays(dtrange), 365)
        self.assertEqual(self.portal.asset.depreciation(dtrange), ZCurrency('GBP500'))

class TestAssetRegister(LedgerTestCase):

    def testTypeInfo(self):
        tinfo = self.portal.portal_types.getTypeInfo(self.ledger)
        self.failUnless(tinfo.allowType('BLAssetRegister'))

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLAssetRegister/assets')
        self.failUnless('assets' in ledger.restrictedTraverse('portal_factory/BLAssetRegister').objectIds())
        assets = temp_object.portal_factory.doCreate(temp_object, 'assets')
        self.failUnless('assets' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLAssetRegister/assets2')
        self.failUnless('assets2' in ledger.restrictedTraverse('portal_factory/BLAssetRegister').objectIds())
        temp_object.blassetregister_edit(['Current Assets'])
        self.failUnless('assets2' in ledger.objectIds())


        temp_object = assets.restrictedTraverse('portal_factory/BLAsset/car')
        self.failUnless('car' in ledger.restrictedTraverse('portal_factory/BLAsset').objectIds())
        #car = temp_object.portal_factory.doCreate(temp_object, 'car')
        #self.failUnless('car' in ledger.objectIds())

        # eek - lots of parameters ...
        #temp_object.blasset_edit()
        #self.failUnless('car' in ledger.objectIds())

    def test1yPrimeCost(self):
        dtrange = (DateTime('2006/01/01'), DateTime('2007/06/01'))

        self.ledger.manage_addProduct['BastionLedger'].manage_addBLAssetRegister('Assets')
        register = self.ledger.Assets
        register.manage_addProduct['BastionLedger'].manage_addBLAsset(dtrange[0],
                                                                      ZCurrency('GBP1000.00'),
                                                                      'A000006',
                                                                      'Prime Cost',
                                                                      1,
                                                                      id='Widget')
        asset = register.Widget

        self.assertEqual(asset.totalCost(), ZCurrency('GBP 1000.00'))
        self.assertEqual(asset.depreciation(dtrange), ZCurrency('GBP1000.00'))
        self.assertEqual(register.depreciationAmount(dtrange), ZCurrency('GBP1000.00'))

        tid = register.manage_applyDepreciation(dtrange)
        self.assertEqual(tid, 'T000000000001')

        txn = self.ledger.Ledger._getOb(tid)

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP1000.00'))

    def test5yPrimeCost(self):

        self.ledger.manage_addProduct['BastionLedger'].manage_addBLAssetRegister('Assets')
        register = self.ledger.Assets
        register.manage_addProduct['BastionLedger'].manage_addBLAsset(DateTime('2010/01/04'),
                                                                      ZCurrency('GBP400.00'),
                                                                      'A000006',
                                                                      'Prime Cost',
                                                                      5,
                                                                      id='Widget')
        asset = register.Widget

        # emulating depreciating company setup fees (as goodwill) ...

        self.assertEqual(asset.totalCost(), ZCurrency('GBP 400.00'))
        self.assertEqual(asset.zeroValueDate(), DateTime('2015/01/03'))

        self.assertEqual(asset.depreciation((DateTime('2009/07/01'), DateTime('2010/06/30'))), 
                                            ZCurrency('GBP 39.01'))

        prorata_range = (DateTime('2009/07/01'), DateTime('2010/06/30'))
        self.assertEqual(int(round(max(prorata_range) - min(prorata_range))), 364)

        sane_range = asset.saneDateRange(prorata_range)
        self.assertEqual(int(round(max(sane_range) - min(sane_range))), 365)

        #self.assertEqual(asset.depreciation(prorata_range), ZCurrency('GBP200.00') * (180.0 / 365.0))
        self.assertEqual(asset.depreciation(prorata_range), ZCurrency('GBP 39.01'))

        self.assertEqual(register.depreciationAmount((DateTime('2010/07/01'), DateTime('2011/06/30'))),
                                                     ZCurrency('GBP 80.00'))

        tid = register.manage_applyDepreciation((DateTime('2010/07/01'), DateTime('2011/06/30')))
        txn = self.ledger.Ledger._getOb(tid)
        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 80.00'))

        # hmmm - 366 days in period ...
        self.assertEqual(register.depreciationAmount((DateTime('2011/07/01'), DateTime('2012/06/30'))),
                                                     ZCurrency('GBP 80.22'))

        tid = register.manage_applyDepreciation((DateTime('2011/07/01'), DateTime('2012/06/30')))
        txn = self.ledger.Ledger._getOb(tid)
        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 80.22'))



def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestDepreciationTool))
    suite.addTest(makeSuite(TestAssetRegister))
    return suite
