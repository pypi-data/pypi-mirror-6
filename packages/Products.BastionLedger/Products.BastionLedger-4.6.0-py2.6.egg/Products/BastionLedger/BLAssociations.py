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
import AccessControl, types, operator
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.AdvancedQuery import In, Eq
from AccessControl.Permissions import access_contents_information, \
     view_management_screens
from Acquisition import aq_base
from Permissions import ManageBastionLedgers, OperateBastionLedgers
from BLBase import PortalContent, LargePortalFolder, ProductsDictionary
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Exceptions import LedgerError
from catalog import makeBLAssociationsCatalog
from zope.interface import Interface, implements
from interfaces.account import IAssociation

#
# these are the minimally sufficient set of associations for the standard
# system/workflows to interoperate
#

DEPRECIATIONS = ('accum_dep', 'dep_exp')
# accum_dep - Accumulated Depreciation (Asset)
# dep_exp - Depeciation Expense (Expense)

ORDERS = ('freight', 'part_cogs', 'part_inc', 'part_inv', 'payables', 'order_pmt', 
          'receivables', 'sales_tax_due', 'sales_tax_paid')
# freight - Freight (Expense)
# part_cogs - Part, Cost of goods sold (Expense)
# part_inc - Part, Income (Income)
# part_inv - Part, Inventory (Asset)
# payables - Payables Ledger control a/c
# order_payments - Cash/credit payments account
# receivables - Receivables Ledger control a/c
# sales_tax_due - Consumption Tax account (Accrued/Owed on Sales)
# sales_tax_paid - Consumption Tax account (Paid on Purchases)

SHAREHOLDERS = ('dividend', 'dividend_payable', 'shareholders', 'dividend_pmt')
# dividend - Dividend Expense (Expense)
# dividend_payable - Accumulated Dividends (Liability)
# shareholders - Shareholders Ledger control a/c

PAYROLL = ('super_exp', 'wages', 'wages_exp', 'wages_pmt', 'wages_super', 'wages_tax',)
# super_exp - Staff superannuation expenses
# wages - Payroll control a/c
# wages_exp - Wages/Payroll Expenses (Expense)
# wages_pmt - Accumulated Wages (Liability)
# wages_super - Accrued superannuation for payroll (Liability)
# wages_tax - PAYG income tax for Payroll (Expense)

# TODO - cashflow statement needs some work so these aren't compulsory (yet)
CASHFLOW_STMT = ('int_inc', 'int_exp', 'div_inc', 'div_exp', 'loans') 

YEAR_END = ('profit_loss', 'retained_earnings', 'loss_fwd', 'tax_accr', 'tax_exp', 'tax_recv', 'tax_defr')
# profit_loss - current earnings (Proprietorship) - TODO clarify!  This either *should* be p&l or Extraordinary Earnings
# retained_earnings - earnings from prior periods (Proprietorship), TODO - we presently close out to this ...
# loss_fwd - losses carried forward
# tax_accr - Company Tax Accrued (Liability)
# tax_exp - Company Tax Expense (Expense) - PAYG company tax
# tax_recv - Company Tax Receivable (Asset) - tax refundable
# tax_defr - Company Tax Deferred (Asset) - losses offsetable

ASSOCIATIONS = ('bank_account', 'bank_exp') + DEPRECIATIONS + ORDERS + SHAREHOLDERS + PAYROLL + YEAR_END


manage_addBLAssociationForm = PageTemplateFile('zpt/add_association', globals())
def manage_addBLAssociation(self, id, ledger, accno, title='', description='', REQUEST=None):
    """
    add an association
    accno may also be a list of account numbers
    """
    self._setObject(id, BLAssociation(id, title, description, ledger, accno))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
    return id


def addBLAssociation(self, id, title=''):
    """
    Plone ctor
    """
    manage_addBLAssociation(self, id, 'Ledger', '1000', title)

class BLAssociation(PortalContent, PropertyManager):
    """
    A Catalogable record about a generic tag for an account
    """
    meta_type = portal_type = 'BLAssociation'

    implements(IAssociation)

    __ac_permissions__ = PortalContent.__ac_permissions__ + (
        (access_contents_information, ('accountValues', 'blAccount')),
        ) + PropertyManager.__ac_permissions__

    _properties = PropertyManager._properties + (
        {'id':'description', 'type':'text',   'mode':'w'},
        {'id':'ledger',      'type':'string', 'mode':'w'},
        {'id':'accno',       'type':'lines',  'mode':'w'},
        )

    manage_options = PropertyManager.manage_options + PortalContent.manage_options

    def __init__(self, id, title, description, ledger, accno):
        self.id = id
        self.title = title
        self.description = description
        self.ledger = ledger
        if type(accno) == types.StringType:
            self.accno = (accno)
        else:
            self.accno = tuple(accno)

    def title(self):
        return '%s - %s' % (self.ledger, self.accno)

    def indexObject(self,idxs=None):
        self.aq_parent.catalog_object(self, '/'.join(self.getPhysicalPath()), idxs=idxs)

    def unindexObject(self):
        self.aq_parent.uncatalog_object('/'.join(self.getPhysicalPath()))

    def accountValues(self, bastionledger):
        """
        return the list of accounts that satisfy the association in the bastionledger
        """
        try:
            return bastionledger._getOb(self.ledger).accountValues(accno=self.accno)
        except KeyError:
            raise LedgerError, "%s missing: %s" % (bastionledger, self.ledger)

    def blAccount(self, bastionledger):
        """
        return a single account that satisfies the association in the bastionledger
        """
        accounts = self.accountValues(bastionledger)
        return accounts and accounts[0] or None
            
    def _updateProperty(self, name, value):
        PropertyManager._updateProperty(self, name, value)
        if name in self.aq_parent.indexes():
            self.indexObject([name])

AccessControl.class_init.InitializeClass(BLAssociation)


def manage_addBLAssociationsFolder(self, id='associations', REQUEST=None):
    """
    """
    self._setObject(id, BLAssociationsFolder(id))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
    return id

class BLAssociationsFolder(LargePortalFolder, ZCatalog):
    """
    Implicit links between account(s) and things we want/need to associate
    """
    meta_type = portal_type = 'BLAssociationFolder'

    title = 'Associations'

    __ac_permissions__ = LargePortalFolder.__ac_permissions__ + (
        (access_contents_information, ('accountValues', 'accountsForLedger', 'missingForLedger')),
        (view_management_screens, ('manage_verify',)),
        ) + ZCatalog.__ac_permissions__

    manage_options = ZCatalog.manage_options[0:2] + (
        {'label':'View',   'action':''},
        {'label':'Verify', 'action':'manage_verify'},
        ) + ZCatalog.manage_options[2:]

    def __init__(self, id):
        """
        dimensions is a list of indexes tuples suitable for addIndex ...
        """
        ZCatalog.__init__(self, id)
        LargePortalFolder.__init__(self, id, self.title)
        makeBLAssociationsCatalog(self)

    def all_meta_types(self):
        return [ ProductsDictionary('BLAssociation') ]

    def accountValues(self, association, bastionledger):
        """
        returns the BLAccounts that satisfy the association in the bastionledger
        """
        assoc = self.get(association)
        if assoc:
            return assoc.accountValues(bastionledger)
        return []

    def accnosForLedger(self, association, ledger):
        """
        returns account numbers to introspect within a *specific* BLLedger with this tag
        """
        assocs = []
        for brain in self.searchResults(id=association, ledger=ledger.getId()):
            try:
                assocs.append(brain.getObject())
            except IndexError:
                continue

        if assocs:
            #results = []
            #for accno in map(lambda x: x.accno, assocs):
            #    if accno not in results:
            #        results.append(accno)
            #return results
            return reduce(operator.add, 
                          map(lambda x: x.accno, assocs))
        return []


    def missingForLedger(self, ledger):
        """
        returns a list of associations that are not present in the BLledger
        """
        accnos = self.uniqueValuesFor('accno')
        laccnos = map(lambda x: x['accno'], 
                      ledger.bastionLedger().evalAdvancedQuery(Eq('ledgerId', ledger.getId(), filter=True) & \
                                                                   In('accno', accnos)))
        missing = filter(lambda x: x not in laccnos, accnos)

        return map(lambda x: x.getObject(), self.searchResults(accno=missing))

    def manage_verify(self, associations=None, REQUEST=None):
        """
        verify that all of the prerequisite/necessary associations are listed
        in the folder
        """
        missing = []
        exists = self.objectIds('BLAssociation')
        for needed in associations or ASSOCIATIONS:
            if needed not in exists:
                missing.append(needed)
        if REQUEST:
            if missing:
                REQUEST.set('manage_tabs_message', 'missing: %s' % ', '.join(missing))
            else:
                REQUEST.set('manage_tabs_message', 'OK')
            return self.manage_main(self, REQUEST)
        if missing:
            raise AttributeError, ', '.join(missing)

    def get(self, tag):
        """
        return the association associated with the tag (or None)
        """
        return self._getOb(tag, None)

AccessControl.class_init.InitializeClass(BLAssociationsFolder)


