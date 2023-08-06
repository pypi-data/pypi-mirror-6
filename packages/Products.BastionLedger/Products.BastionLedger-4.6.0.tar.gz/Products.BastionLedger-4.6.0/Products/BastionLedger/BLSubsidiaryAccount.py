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

import AccessControl, logging
from AccessControl import getSecurityManager
from AccessControl.Permissions import access_contents_information

from Acquisition import aq_base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.AdvancedQuery import Eq
from Products.BastionBanking.ZCurrency import ZCurrency
from DateTime import DateTime

from utils import floor_date
from BLBase import *
from BLAccount import BLAccount
from BLEntry import BLEntry
from BLSubsidiaryEntry import BLSubsidiaryEntry, manage_addBLSubsidiaryEntry
from BLSubsidiaryTransaction import manage_addBLSubsidiaryTransaction
from AccessControl.Permissions import manage_properties
from Permissions import OperateBastionLedgers, OverseeBastionLedgers
from email.Utils import parseaddr

manage_addBLSubsidiaryAccountForm = PageTemplateFile('zpt/add_subsidiaryaccount', globals()) 
def manage_addBLSubsidiaryAccount(self, title, currency, subtype='', accno='', tags=[], id='', 
                                  description='', REQUEST=None):
    """ an account in a subsidiary ledger """

    # portal_factory needs this to be settable...
    if not id:
        id = self.nextAccountId()

    self._setObject(id, BLSubsidiaryAccount(id, title, description, self.accountType(),
                                            subtype, currency,
                                            accno or id, tags))
    
    acct = self._getOb(id)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % acct.absolute_url())
        
    return acct

def addBLSubsidiaryAccount(self, id='', title='', description='', subtype='', accno='', tags=[]):
    """
    Plone constructor
    """
    account = manage_addBLSubsidiaryAccount(self,
                                            id = id,
                                            title=title,
                                            description=description,
                                            subtype=subtype,
                                            accno=accno or id,
                                            currency=self.defaultCurrency(),
                                            tags=tags)
    return account.getId()

    
class BLSubsidiaryAccount( BLAccount ):
    """ 
    An account in a subsidiary ledger/journal
    These types of account can be associated with emails and/or portal members
    """
    meta_type = portal_type = 'BLSubsidiaryAccount'

    __ac_permissions__ = BLAccount.__ac_permissions__ + (
        (access_contents_information, ('emailAddress', 'emailAddresses', 
                                       'getMemberIds', 'getMembers',
                                       'isJointAccount')),
        )

    _properties = BLAccount._properties + (
        {'id':'email',          'type':'string',    'mode': 'w'},
    )


    def createTransaction(self, title='',reference=None, effective=None):
        """
        polymorphically create correct transaction for ledger ...
        """
	transactions = self.blLedger()
        tid = manage_addBLSubsidiaryTransaction(transactions, '',
                                                title or self.getId(), 
                                                effective or DateTime(),
                                                reference)
        return transactions._getOb(tid)

    def createEntry(self, txn, amount, title=''):
        """ transparently create a transaction entry"""
        manage_addBLSubsidiaryEntry(txn, self, amount, title)

    def _entryQuery(self, aquery):
        return aquery & Eq('ledgerId', self.ledgerId()) & Eq('meta_type', 'BLSubsidiaryEntry')

    def getMemberIds(self, mt=None):
        """
        link account to member(s)
        """
        ids = []
        mt = mt or getToolByName(self, 'portal_membership')
        
        for raw_email in map(lambda x: parseaddr(x)[1],
                             self.emailAddresses()):
            if raw_email:
                ids.extend(map(lambda x: x['username'],
                               mt.searchMembers('email', raw_email)))
        if not ids:
            ids = [ self.getOwnerTuple()[1] ]

        return ids

    def getMembers(self, mt=None):
        """
        we link members based upon email address.  If the account is severally owned,
        you should add multiple email addresses
        """
        mt = mt or getToolByName(self, 'portal_membership')
  
        return map(lambda x: mt.getMemberById(x), self.getMemberIds(mt))

    def emailAddress(self):
        """
        the primary email address associated with the account
        """
        addresses = self.emailAddresses()
        if addresses:
            return addresses[0]
        return ''

    def emailAddresses(self):
        """
        return email address as a list, useful if multiple addresses stored in email field
        """
        email = self.email
        if email:
            for separator in (',', ';'):
                if email.find(separator) != -1:
                    return email.split(separator)
            return [ email ]
        return []

    def isJointAccount(self):
        """ returns whether or not this is a joint account """
        return len(self.getMemberIds()) > 1

    def _repair(self):
        BLAccount._repair(self)
        
AccessControl.class_init.InitializeClass(BLSubsidiaryAccount)
