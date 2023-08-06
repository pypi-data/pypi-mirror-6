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
from LedgerTestCase import LedgerTestCase

class TestAssociations(LedgerTestCase):
    """
    lightweight Zope-only tax table tests
    """

    def testConstructed(self):
        self.failUnless(getattr(self.controller_tool, 'associations', None))

    def testPrerequisites(self):
        # make sure the default chart isn't borked ...
        self.controller_tool.associations.manage_verify()

    def testQueries(self):
        af = self.controller_tool.associations

        self.assertEqual(af.accountValues('bank_account', self.ledger),
                         [self.ledger.Ledger.A000001])

        self.assertEqual(map(lambda x: x.getObject(), 
                             af.searchResults(id=['bank_account'], ledger='Ledger')),
                         [af.bank_account])

        # TODO - wtf???
        self.assertEqual(af.accnosForLedger('bank_account', self.ledger.Ledger),
                         ('1060', '1060'))

    def testMissing(self):
        af = self.controller_tool.associations
        self.assertEqual(af.missingForLedger(self.ledger.Ledger),[])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestAssociations))
    return suite
