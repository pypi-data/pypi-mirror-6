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
from Testing import ZopeTestCase
from DateTime import DateTime
from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

from setup import setupLedgerSite, ledger_products, ledger_name, ledger_owner, portal_name, default_user

setupLedgerSite()

#@onsetup
#def setup_product():
#    fiveconfigure.debug_mode = True
#    import Products.BastionLedger
#    zcml.load_config('configure.zcml',
#                     Products.BastionLedger)
#    fiveconfigure.debug_mode = False

class LedgerTestCase(PloneTestCase.PloneTestCase):
    """ Base test case for testing BastionLedger functionality """

    #
    # constants that may be affected by changes to chart of accounts ...
    #
    NUMBER_ACCOUNTS = 58
    NUMBER_ASSETS = 11

    LOSSFWD_ID = 'A000025'
    RETAINED_ID = 'A000026'
    PROFIT_ID = 'A000027'
    DEFERRED_ID = 'A000012'
    SALESTAX_ID = 'A000016'

    RECEIVABLES_CTL = 'A000005'

    now = DateTime()
    RUN_TIME = 60.0 / 86000 * 5 # generously five minutes to run tests 

    def getLedger(self):
        return getattr(self.getPortal(), ledger_name)

    def afterSetUp(self):
        ledger = self.ledger = self.getLedger()
        self.controller_tool = self.portal.portal_bastionledger

        self.portal_currencies = getattr(self.portal, 'portal_currencies', None)




