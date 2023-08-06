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

import AccessControl, types, operator, logging
from DateTime import DateTime
from Acquisition import aq_base
from AccessControl.Permissions import access_contents_information
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.AdvancedQuery import Between, Eq
from Products.BastionBanking.ZCurrency import ZCurrency

from BLGlobals import EPOCH
from BLBase import *
from BLLedger import LedgerBase
from BLAccount import addBLAccount
from BLSubsidiaryTransaction import manage_addBLSubsidiaryTransaction
from BLControlEntry import BLControlEntry
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from Exceptions import LedgerError
from Products.CMFCore import permissions
from utils import ceiling_date

from zope.interface import Interface, implements

from interfaces.ledger import ISubsidiaryLedger
from interfaces.tools import IBLLedgerToolMultiple


manage_addBLSubsidiaryLedgerForm = PageTemplateFile('zpt/add_subsidiaryledger', globals()) 
def manage_addBLSubsidiaryLedger(self, id, controlAccounts, currencies, title='', REQUEST=None):
    """ a journal """
    
    # do some checking ...
    controls = []
    for acc in controlAccounts:
        if type(acc) == types.StringType:
            control = self.Ledger._getOb(acc)
        assert control.meta_type =='BLAccount', "Incorrect Control Account Type - Must be strictly GL"
        assert not getattr(aq_base(control), id, None),"A Subsidiary Ledger Already Exists for this account."
        controls.append(control)

    self._setObject(id, BLSubsidiaryLedger(id, title, controls, currencies))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

    return self._getOb(id)

def addBLSubsidiaryLedger(self, id, title='', REQUEST=None):
    """
    Plone-based entry - we set up a new account in the ledger for the control
    account if one's not passed in (which is unlikely)
    """
    gl = self.Ledger
    control = addBLAccount(gl, title='Control Account: %s' % title) # get next accno
    
    ledger = manage_addBLSubsidiaryLedger(self, id, (control,), gl.currencies, title)
    return id

class BLSubsidiaryLedger(LedgerBase):
    """
    A journal whose accounts all aggregate into an account in the Ledger
    """
    meta_type = portal_type = 'BLSubsidiaryLedger'

    implements(ISubsidiaryLedger, IBLLedgerToolMultiple)
    
    __ac_permissions__ = LedgerBase.__ac_permissions__ + (
        (access_contents_information, ('controlAccount', 'controlAccounts',
                                       'controlEntry', 'controlEntries',
                                       'accountType')),
        (OperateBastionLedgers,('manage_recalculateControl', 'manage_recalculateControls',
                                'manage_applyAccountType')),
        (ManageBastionLedgers, ('manage_changeControl', 'manage_reset')),
        )

    account_types = ('BLSubsidiaryAccount',)
    transaction_types = ('BLSubsidiaryTransaction',)

    def __init__(self, id, title, controls, currencies, account_id=100000, 
                 account_prefix='SL', txn_id=1, txn_prefix='ST'):
        LedgerBase.__init__(self, id, title, currencies, account_id, account_prefix,
                          txn_id, txn_prefix)
        self._control_accounts = tuple(map(lambda x: x.getId(), controls))

    def manage_edit(self, title, description, txn_id, account_id, account_prefix,
                    txn_prefix, currencies, email='', instructions='', REQUEST=None):
        """
        update ordbook properties
        """
        # TODO - bodgy hack to ensure control account creation via Plone portal factories ...
        if self._control_accounts == ():
            self._control_accounts = (self.REQUEST['control_account'],)
            addSubsidiaryLedger(self, None)

        return LedgerBase.manage_edit(self, title, description, txn_id, account_id, account_prefix,
                                      txn_prefix, currencies, email, REQUEST)

    def controlAccount(self, accno):
        """
        return the ledger account which this account aggregates into
        """
        if accno:
            if accno in self._control_accounts:
                return self.Ledger._getOb(accno)
            raise LedgerError, 'Invalid/unknown control account: %s' % accno
        try:
            return self.Ledger._getOb(self._control_accounts[0])
        except:
            raise LedgerError, 'control account not found: %s' % self._control_accounts

    def controlAccounts(self):
        """
        return *all* control accounts
        """
        return filter(lambda x: x,
                      map(lambda x: self.Ledger._getOb(x, None), 
                          self._control_accounts))

    def controlEntry(self, accno):
        """
        return the summary entry for this journal in the GL's control account
        """
        return self.controlAccount(accno)._getOb(self.getId())

    def controlEntries(self):
        """
        """
        return map(lambda x: self.controlEntry(x), self._control_accounts)

    def manage_changeControl(self, control_accounts, effective=None, REQUEST=None):
        """
        go change the control account to a different account
        """
        control_id = self.getId()

        for control_account in control_accounts:
            control = self.Ledger._getOb(control_account)
            if getattr(aq_base(control), control_id, None) is None:
                # we don't do events - control entry doesn't have proper workflow
                # and we don't need to index them ...
                control._setObject(control_id,
                                   BLControlEntry(control_id,
                                                  'Subsidiary Ledger (%s)' % control_id,
                                                  control_account,
                                                  self.total(currency=control.base_currency,
                                                             effective=(control.openingDate(),
                                                                        effective or DateTime()))),
                                   suppress_events=True)

        for control_account in self._control_accounts:
            if control_account not in control_accounts:
                # remove old entry if present
                try:
                    controlEntry = self.controlEntry(control_account)
                    controlEntry.aq_parent._delObject(control_id, suppress_events=True)
                except:
                    pass
        
        self._control_accounts = tuple(control_accounts)
        self.manage_applyAccountType()

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Changed Control Accounts')
            return self.manage_main(self, REQUEST)

    def defaultCurrency(self):
        """ the currency of the control account"""
        return self.controlAccount(self._control_accounts[0]).base_currency

    def createTransaction(self, effective=None, title='', entries=[], tags=[], ref=None, control=None):
        """
        return a newly created BLTransaction
        """
        txn_id = manage_addBLSubsidiaryTransaction(self,
                                                   title=title,
                                                   effective=effective or DateTime(),
                                                   ref=ref,
                                                   entries=entries,
                                                   tags=tags,
                                                   control=control or self._control_accounts[0])
        return self._getOb(txn_id)

    def manage_recalculateControl(self, controlid, effective=None, force=False, REQUEST=None):
        """
        Hmmm - 'useful' admin function - only for Manager permissions ...

        force means to recalculate from the very start instead of the opening balance record
        """
        controlEntry = self.controlEntry(controlid)
        control = self.controlAccount(controlid)
        if force:
            opening = EPOCH
        else:
            opening = control.openingDate()

        if effective is None:
            last_txn = self.lastTransaction()
            if last_txn:
                effective = last_txn.effective()
            else:
                effective = DateTime()
        dt = ceiling_date(effective)

        amt = control.zeroAmount()
        currency = amt.currency()
        for txn in self.transactionValuesAdv(Eq('accountId', controlid) & Between('effective', opening, dt)):
            for entry in txn.objectValues('BLSubsidiaryEntry'):
                # the posting amount should be the correct currency ...
                amt += entry.amountAs(currency)

        if force:
            controlEntry.amount = amt
        else:
            bal = self.bastionLedger().periods.balanceForAccount(opening, 'Ledger', controlid)
            if bal:
                controlEntry.amount = amt + bal
            else:
                controlEntry.amount = amt

        controlEntry._setEffectiveDate(dt)

        if REQUEST:
            REQUEST.set('management_view', 'Properties')
            REQUEST.set('manage_tabs_message',
                        "Recalculated %s" % str(controlEntry))
            return self.manage_propertiesForm(self, REQUEST)
                               
    def manage_recalculateControls(self, effective=None, force=False, REQUEST=None):
        """
        Hmmm - 'useful' admin function - only for Manager permissions ...

        force means to recalculate from the very start instead of the opening balance record
        """
        for control in self._control_accounts:
            self.manage_recalculateControl(control, effective, force)
        if REQUEST:
            REQUEST.set('management_view', 'Properties')
            REQUEST.set('manage_tabs_message', "Recalculated controls")
            return self.manage_propertiesForm(self, REQUEST)

    def accountType(self):
        """
        indicate what type of account is assumed to go into this ledger
        """
        return self.controlAccount(self._control_accounts[0]).type

    def manage_applyAccountType(self, REQUEST=None):
        """
        """
        count = 0
        acctype = self.accountType()
        for acc in self.accountValuesAdv(~Eq('type', acctype)):
            acc.manage_changeProperties(type=acctype)
            count += 1
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Fixed %i accounts' % count)
            return self.manage_main(self, REQUEST)

    def _reset(self):
        """ remove all account/txn entries """
        LedgerBase._reset(self)
        self._reset_controls()

    def _reset_controls(self):
        # recreate control entries, set zero amount
        for accno in self._control_accounts:
            control = self.controlAccount(accno)
            entry = self.controlEntry(accno)
            entry.amount = ZCurrency(control.base_currency, 0)
            entry._setEffectiveDate(EPOCH)

    def manage_reset(self, REQUEST=None):
        """
        """
        self._reset()
        self.bastionLedger().refreshCatalog()
        if REQUEST:
            return self.manage_transactions(self, REQUEST)

    def _repair(self):
        if getattr(aq_base(self), '_control_account', None):
            control = self._control_account
            self._control_accounts = (control,)
            for txn in self.transactionValues():
                txn._control_account = control
                txn.reindexObject()
            delattr(self, '_control_account')

AccessControl.class_init.InitializeClass(BLSubsidiaryLedger)

def addSubsidiaryLedger(ob, event):
    # seems that importing from old-style control may barf ...
    if not getattr(aq_base(ob), '_control_accounts', None):
        ob.manage_repair()
    # OLD-CATALOG
    try:
        ob.manage_changeControl(ob._control_accounts)
    except:
        # this only fails for imports of old-style catalog'd ledgers ...
        pass

def delSubsidiaryLedger(ob, event):
    try:
        # remove the control account's subsidiary entry ...
        for control in ob._control_accounts:
            try:
                ob.controlAccount(control)._delObject(ob.getId())
            except:
                # oh well - not there ...
                pass
    except AttributeError:
        # old style/unmigrated ledger
        pass

