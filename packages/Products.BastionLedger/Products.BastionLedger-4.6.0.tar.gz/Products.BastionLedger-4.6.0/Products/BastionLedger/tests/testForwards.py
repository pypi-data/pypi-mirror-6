#
#    Copyright (C) 2014  Corporation of Balclutha. All rights Reserved.
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

from LedgerTestCase import LedgerTestCase

from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import ceiling_date, floor_date
from Products.BastionLedger.BLGlobals import EPOCH
from Products.AdvancedQuery import Between, Eq

zero = ZCurrency('GBP 0.00')
ten = ZCurrency('GBP 10.00')

class TestForwards(LedgerTestCase):
    """
    verify forward-dated transactions (and end of day/rollover)
    """
    def testLedgerStatic(self):
        self.assertEqual(self.ledger.accrued_to, ceiling_date(self.now))

    def _postTxn(self, effective, acc1, acc2, amount, title='My Txn'):
        txn = self.ledger.Ledger.createTransaction(title=title, effective=effective)
        txn.createEntry(acc1, amount)
        txn.createEntry(acc2, -amount)
        txn.manage_post()
        return txn

    def testBalanceFunctionInternals(self):
        acc = self.ledger.Ledger.A000001
        self.assertEqual(list(acc.objectValues('BLControlEntry')), [])
        self.assertEqual(self.portal.portal_bastionledger.addCurrencies([(zero, EPOCH)], 'GBP'), zero)

    def testFutureBalances(self):
        acc = self.ledger.Ledger.A000001
        self.assertEqual(acc.totBalance(), zero)
        txn = self._postTxn(self.now+10, 'A000001', 'A000002', ten)

        # assure underlying cache
        self.assertEqual(acc.totBalance(), zero)
        self.assertEqual(acc.totDate(), EPOCH)

        self.assertEqual(acc.balance(effective=self.now), zero)
        self.assertEqual(acc.balance(), zero)
        self.assertEqual(acc.balance(effective=self.now+10), ten)

    def testRollOverNow(self):
        acc = self.ledger.Ledger.A000001
        txn = self._postTxn(self.now+10, 'A000001', 'A000002', ten)

        self.ledger.manage_dailyEnd(self.now+11)
        self.assertEqual(self.ledger.accrued_to, ceiling_date(self.now+11))

        # we *ignore* all forwards of *now* ...
        self.assertEqual(acc.totBalance(), zero)
        self.assertEqual(acc.totDate(), EPOCH)

        self.assertEqual(acc.balance(effective=self.now+10), ten)

    def testRollOverDated(self):
        ledger = self.ledger
        acc = ledger.Ledger.A000001
        txn = self._postTxn(self.now+10, 'A000001', 'A000002', ten)

        # assure manage_dailyEnd will pick up txns to _totalise()
        self.assertEqual(len(ledger.transactionValuesAdv(Between('effective', 
                                                                 ledger.accrued_to, 
                                                                 self.now+10) & \
                                                             Eq('status', 'posted'))), 1)
        self.assertEqual(int(ceiling_date(self.now+11) - ledger.accrued_to), 10) # *must* be greater than 0 ...

        ledger.manage_dailyEnd(self.now+11, self.now+12)

        # it's *now* self.now+12 ...
        self.assertEqual(acc.totBalance(), ten)
        self.assertEqual(acc.totDate(), floor_date(self.now+10))

if __name__ == '__main__':
    unittest.main()

