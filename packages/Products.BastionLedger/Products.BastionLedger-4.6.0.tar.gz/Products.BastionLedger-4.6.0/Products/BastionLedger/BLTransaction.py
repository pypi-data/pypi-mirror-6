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

import AccessControl, types, operator, string, sys, traceback
from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens, change_permissions, \
     access_contents_information
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from DocumentTemplate.DT_Util import html_quote
from ExtensionClass import Base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.BastionBanking.ZCurrency import ZCurrency
from OFS.ObjectManager import BeforeDeleteException
from zope.interface import implements

from BLBase import *
from utils import assert_currency, floor_date, ceiling_date
from BLAttachmentSupport import BLAttachmentSupport
from Permissions import OperateBastionLedgers, OverseeBastionLedgers, ManageBastionLedgers
from Exceptions import PostingError, UnpostedError, IncorrectAmountError, \
    IncorrectAccountError, InvalidTransition, UnbalancedError
from interfaces.transaction import ITransaction
import logging

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

LOG = logging.getLogger('BLTransaction')

manage_addBLTransactionForm = PageTemplateFile('zpt/add_transaction', globals()) 
def manage_addBLTransaction(self, id='', title='',effective=None,
                            ref=None, entries=[], tags=[], REQUEST=None):
    """ add a transaction """
    if ref:
        try:
            ref = '/'.join(ref.getPhysicalPath())
        except:
            pass

    if not id:
        id = self.nextTxnId()

    effective = effective or DateTime()
    if type(effective) == types.StringType:
        effective = DateTime(effective)
    effective.toZone(self.timezone)

    self._setObject(id, BLTransaction(id, title, effective, ref, tags))

    txn = self._getOb(id)

    # don't do entries with blank amounts ...
    for entry in filter(lambda x: getattr(x, 'amount', None), entries):
        try:
            assert_currency(entry.amount)
        except:
            entry.amount = ZCurrency(entry.amount)
        if entry.get('credit', False):
            entry.amount = -abs(entry.amount)
        try:
            manage_addBLEntry(txn, entry.account, entry.amount, entry.title)
        except NameError:
            # doh - more cyclic dependencies ...
            from BLEntry import manage_addBLEntry
            manage_addBLEntry(txn, entry.account, entry.amount, entry.title)
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % txn.absolute_url())

    return id


def addBLTransaction(self, id, title=''):
    """
    Plone constructor - we generated this id via our own generateUniqueId function
    in BLLedger ...
    """
    id = manage_addBLTransaction(self, id=id, title=title)
    return id

class BLTransaction(LargePortalFolder, BLAttachmentSupport):

    meta_type = portal_type = 'BLTransaction'

    implements(ITransaction)
    
    __ac_permissions__ = LargePortalFolder.__ac_permissions__ + (
        (view_management_screens, ('manage_verify',)),
        (access_contents_information, ('isMultiCurrency', 'faceCurrencies', 'isAgainst',
                                       'currencies', 'effective', 'hasTag', 'isForward')),
        (OperateBastionLedgers, ('manage_post', 'manage_editProperties', 'manage_toggleDRCR', 
                                 'manage_toggleAccount', 'createEntry',
                                 'manage_propertiesForm', 'setStatus', 'addEntries', 'editProperties',
				 'manage_statusModify',)),
        (OverseeBastionLedgers, ('manage_reverse','manage_cancel', 'manage_repost', 'manage_unpost')),
	(view, ('asXML', 'referenceUrl', 'referenceId', 'dateStr', 'blLedger', 'debitTotal',
		'creditTotal', 'total', 'modificationTime', 'created',
		'blEntry', 'entryItems', 'entryValues', 'postedValues', 'modifiable')),
       ) + BLAttachmentSupport.__ac_permissions__

    _v_already_looking = 0
    tags = ()

    manage_options = (
        { 'label': 'Entries',    'action' : 'manage_main',
          'help':('BastionLedger', 'transaction.stx') },
        { 'label': 'View',       'action' : '',},
        BLAttachmentSupport.manage_options[0],
        { 'label': 'Verify',       'action' : 'manage_verify',},
        { 'label': 'Properties', 'action' : 'manage_propertiesForm'},
        ) + PortalContent.manage_options

    manage_main = PageTemplateFile('zpt/view_transaction', globals())

    #manage_main = LargePortalFolder.manage_main

    asXML = PageTemplateFile('zpt/xml_txn', globals())
    
    _properties = ( 
        {'id':'title',          'type':'string',    'mode':'w' },
        {'id':'effective_date', 'type':'date',      'mode':'w' }, # this is Dublin Core!!
        {'id':'entered_by',     'type':'string',    'mode':'r' },
        {'id':'reference',      'type':'string',    'mode':'w' },
        {'id':'tags',           'type':'lines',     'mode':'w' },
        )
    
    def __init__(self, id, title, effective, reference, tags):
        LargePortalFolder.__init__(self, id)
        self.title = title
        self.effective_date = floor_date(effective)
        self.entered_by = getSecurityManager().getUser().getUserName()
        self.reference = reference
        self._updateProperty('tags', tags)

    #
    # a reference may or may not be a reference to an object on the system ...
    #
    def referenceObject(self):
        """
        return the object that's referenced to this transaction
        """
        if self.reference:
            try:
                return self.unrestrictedTraverse(self.reference)
            except:
                pass
        return None
            
    def referenceUrl(self):
        if self.reference:
            try:
                return self.unrestrictedTraverse(self.reference).absolute_url()
            except:
                pass
        return None

    def referenceId(self):
        return string.split(self.reference, '/').pop()

    def hasTag(self, tag):
        """
        """
        return tag in self.tags

    def dateStr(self): return self.day.strftime('%Y-%m-%d %H:%M:%S')

    def blLedger(self):
        #
        # Transactions are buried within the 'Transactions' folder of a Ledger ...
        #
        return self.aq_parent

    def transactionId(self):
        """
        indexing
        """
        return self.getId()

    def all_meta_types(self):
        """ """
        return [ ProductsDictionary('BLEntry') ]

    def filtered_meta_types(self, request=None):
        """ """
        if self.status() in ['incomplete', 'complete']:
            return [ ProductsDictionary('BLEntry') ]
        return []

    def defaultCurrency(self):
        """
        """
        return self.aq_parent.defaultCurrency()

    def isMultiCurrency(self):
        """
        return whether or not this transaction has entries in different currencies
        """
        return len(self.faceCurrencies()) > 1

    def faceCurrencies(self):
        """
        return a tuple of the currencies represented in the transaction
        """
        currencies = {}
        for amt in map(lambda x: x.amount, self.entryValues()):
            currencies[amt.currency()] = True

        return currencies.keys()

    def currencies(self):
        """
        return all the currencies in which this transaction can be historically valued in
        """
        currencies = self.faceCurrencies()
        for currency in self.foreignCurrencies():
            if currency not in currencies:
                currencies.append(currency)

        return currencies
        
    def debitTotal(self, currency=''):
        """ sum all the debits """
        base = currency or self.aq_parent.defaultCurrency()
        total = ZCurrency(base, 0.0)
        for entry in filter(lambda x: x.amount > 0, self.entryValues()):
            total += entry.amountAs(base)

        return total
    
    def creditTotal(self, currency=''):
        """ sum all the credits - effective is for currency rate(s)"""
        base = currency or self.aq_parent.defaultCurrency()
        total = ZCurrency(base, 0.0)
        for entry in filter(lambda x: x.amount < 0, self.entryValues()):
            total += entry.amountAs(base)

        return total
    
    def total(self, currency=''):
        """ sum all the debits and credits - effective is for currency rate(s) """
        base = currency or self.aq_parent.defaultCurrency()
        return self.debitTotal(currency) + self.creditTotal(currency)

    def modificationTime(self):
        """ """
        return self.bobobase_modification_time().strftime('%Y-%m-%d %H:%M')

    def _status(self, state):
        LargePortalFolder._status(self, state)
        self.reindexObject(idxs=['status'])
        # now we have to ensure all entries indexes are correct
        for entry in self.entryValues():
            entry.reindexObject(idxs=['status'])

    def setReference(self, ob):
        if not self.reference:
            self._updateProperty('reference', '/'.join(ob.getPhysicalPath()))
            
    def setStatus(self, REQUEST=None):
        """
        does automatic status promotions - as all these functions are private :(
        """
        wftool = getToolByName(self, 'portal_workflow')
        status = self.status()

        base = self.defaultCurrency()

        if not len(self.objectIds()):
            if status != 'incomplete':
                self._status('incomplete')
            return

        if status == 'incomplete':
            if self.debitTotal(currency=base) == abs(self.creditTotal(currency=base)):
                wf = wftool.getWorkflowsFor(self)[0]
                wf._executeTransition(self, wf.transitions.complete)
                status = self.status()

        elif status == 'complete':
            if self.debitTotal(currency=base) != abs(self.creditTotal(currency=base)):
                wf = wftool.getWorkflowsFor(self)[0]
                wf._executeTransition(self, wf.transitions.incomplete)
                status = self.status()

        if status != 'reversed':
            self._status('posted')

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def type(self):
        # ensure no cataloging of this field
        return None

    def _updateProperty(self, name, value):
        LargePortalFolder._updateProperty(self, name, value)
        if name in ('effective',):
            self.reindexObject(['effective'])
        if name == 'title':
            # go set untitled entries to this description ...
            for entry in self.entryValues():
                if not entry.title:
                    entry._updateProperty('title', value)

    def addEntries(self, entries):
        """
        Allow scripts to add entries ...
        entries may be BLEntry-derived, or a list of hash's keyed on account, amount, title (optional)
        """
        for e in entries:
            if isinstance(e, dict):
                self.createEntry(e['account'], e['amount'], e.get('title', ''))
            else:
                self._setObject(e.getId(), e)
            
    def createEntry(self, account, amount, title=''):
        """
        create an entry without having to worry about entry type
        """
        if amount == 0:
            return None
        if type(account) == types.StringType:
            account = self.aq_parent._getOb(account)
        return self.manage_addProduct['BastionLedger'].manage_addBLEntry(account, amount, title)


    def entryValues(self):
        """
        list of entries
        """
        return self.objectValues(('BLEntry', 'BLSubsidiaryEntry'))

    def entryItems(self):
        """
        """
        return self.objectItems(('BLEntry', 'BLSubsidiaryEntry'))

    def blEntry(self, account_id, ledger_id=''):
        """ retrieve an entry that should be posted to indicated account in indicated ledger"""
	for v in self.entryValues():
            if v.accountId() == account_id:
                if ledger_id == '' or v.blLedger().getId() == ledger_id:
                    return v
        return None

    def isAgainst(self, accnos, ledger_id):
        """
        return if this transaction affects any of the accounts from specified ledger
        """
        for v in self.entryValues():
            if v.accountId() in accnos and v.blLedger().getId() == ledger_id:
                return True
        return False

    def manage_post(self, REQUEST=None):
        """
        post transaction entries  - note we do not post zero-amount entries!
        """
	status = self.status()

        if status in ('reversed', 'cancelled'):
            if REQUEST:
                return self.manage_main(self, REQUEST)
            return

        # we're flicking the status to posted in the workflow too soon in order to
        # ensure correct status when cataloging the account entries
        if status in ('incomplete', 'posted'):
            message = 'Transaction %s %s != %s' % (status, self.debitTotal(), self.creditTotal())
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return self.manage_main(self, REQUEST)
            raise PostingError, "%s\n%s" % (message, str(self))

        if self.effective_date > DateTime():
            if not getToolByName(self, 'portal_bastionledger').allow_forwards:
                message = 'Future-dated transactions not allowed!'
                if REQUEST is not None:
                    REQUEST.set('manage_tabs_message', message)
                    return self.manage_main(self, REQUEST)
                raise PostingError, "%s\n%s" % (message, str(self))
            self._forward = True

        try:
            map (lambda x: x._post(), filter(lambda x: x.absAmount() > 0.005, self.entryValues()))
        except PostingError:
            raise
        except:
            # raise a very meaningful message now!!
            typ, val, tb = sys.exc_info()
            fe=traceback.format_exception (typ, val, tb)
            raise AttributeError, '%s\n%s' % ('\n'.join(fe), str(self))

        # adjust status in index ...
        self._status('posted')
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

    def manage_toggleDRCR(self, ids=[], REQUEST=None):
        """
        flip the dr/cr on selected entries - useful to correct keying errors
        """
        if ids:
            for id, entry in filter(lambda x,ids=ids: x[0] in ids, self.entryItems()):
                entry._updateProperty('amount', -entry.amount)
            #self.setStatus()

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_toggleAccount(self, old, new, REQUEST=None):
        """
        remove the old entry (account id), replacing amount with new entry
        """
        status = self.status()
        entry = self.blEntry(old)

        # only bother with reposting posted stuff - otherwise it's eye candy
        if entry:
            if status == 'posted':
                self.manage_unpost()
            self._delObject(entry.getId())
            self.createEntry(new, entry.amount, entry.title)
            if status == 'posted':
                self.manage_post()

        if self.status() != status:
            self._status(status)

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_verify(self, precision=0.05, REQUEST=None):
        """
        verify the transaction has been applied correctly to the ledger(s)

        precision defaults to five cents

        this function deliberately *does not* use the underlying object's methods
        to check this - it's supposed to independently check the underlying
        library - or consequent tamperings via the ZMI

        it returns a list of (Exception, note) tuples
        """
        bad_entries = []

        entries = self.entryValues()
        status = self.status()

        if status in ('posted', 'reversed'):
                
            #
            # make sure the transaction balanced (within 5 cents) in the first place ...
            #
            if abs(self.total()) > precision:
                bad_entries.extend(map(lambda x: (UnbalancedError(x), self.total()), entries))
            else:
                #
                # check that the posted entries are consistent with the balanced txn ...
                #
                base_currency = self.defaultCurrency()
                for  unposted in entries:
                    account = unposted.blAccount()
                    try:
                        posted = account.blEntry(self.getId())
                    except:
                        # hmmm - dunno why we should have posted zero-amount transactions,
                        # but they're not wrong ...
                        if unposted.amount == 0:
                            continue
                        bad_entries.append((UnpostedError(unposted), ''))
                        continue

                    posted_acc = posted.blAccount() 
                    if posted_acc != account:
                        bad_entries.append((IncorrectAccountError(unposted), 
                                            '%s/%s' % (posted_acc.ledgerId(), posted_acc.getId())))
                        continue

                    posted_amt = posted.amount
                    unposted_amt = unposted.amount

                    # find/use common currency base
                    if posted_amt.currency() != base_currency:
                        posted_amt = posted.amountAs(base_currency)

                    if unposted_amt.currency() != base_currency:
                        unposted_amt = unposted.amountAs(base_currency)

                    # 5 cent accuracy ...
                    if abs(posted_amt - unposted_amt) > 0.05:
                        #raise AssertionError ((unposted.getId(), unposted.blAccount(), unposted.amount, unposted_amt), 
                        #                      (posted.getId(), posted.blAccount(), posted.amount, posted_amt))
                        bad_entries.append((IncorrectAmountError(unposted), 
                                            '%s/%s' % (posted_amt, posted_amt - unposted_amt)))

        #
        # we shouldn't be posting these ...
        #
        if status in ('cancelled', 'incomplete'):
            for entry in entries:
                try:
                    posted = entry.blAccount()._getOb(self.getId())
                    bad_entries.append((PostingError(posted), ''))
                except:
                    continue

        if status in ('complete'):
            for entry in entries:
                try:
                    posted = entry.blAccount()._getOb(self.getId())
                    bad_entries.append((PostingError(posted), ''))
                except:
                    continue

        if REQUEST:
            if bad_entries:
                REQUEST.set('manage_tabs_message',
                            '<br>'.join(map(lambda x: "%s: %s %s" % (x[0].__class__.__name__,
                                                                     html_quote(str(x[0].args[0])),
                                                                     x[1]), bad_entries)))
            else:
                REQUEST.set('manage_tabs_message', 'OK')
            return self.manage_main(self, REQUEST)

        return bad_entries

    def __getattr__(self, name):
        """
        returns the attribute or matches on title of the entries within ...
        """
        if not self._v_already_looking:
            try:
                #LOG.debug( "__getattr__(%s)" % name)
                self._v_already_looking = 1
                if self.__dict__.has_key(name):
                    return self.__dict__[name]

                # we are expecting just BLEntry deriviatives ...
                for entry in self.objectValues():
                    if entry.title == name:
                        return entry
            finally:
                self._v_already_looking = 0
        # not found - pass it on ...
        return Base.__getattr__(self, name)

    def manage_unpost(self, force=False, REQUEST=None):
        """
        remove effects of posting
        """
        if force or self.status() == 'posted':
            for entry in self.entryValues():
                entry._unpost()

                if getattr(aq_base(self), '_forward', None):
                    delattr(self, '_forward')

            self._status('complete')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_editProperties(self, REQUEST):
        """ Overridden to make sure recataloging is done """
        for prop in self._propertyMap():
            name=prop['id']
            if 'w' in prop.get('mode', 'wd'):
                value=REQUEST.get(name, '')
                self._updateProperty(name, value)

        self.reindexObject(idxs=['effective', 'tags'])

    def editProperties(self, title, description, effective, tags=[]):
        """
        Plone form updates
        """
        self.title = title
        self.description = description
        self.effective_date = floor_date(effective)
        self._updateProperty('tags', tags)
        self.reindexObject()

    def indexObject(self, idxs=[]):
        """ Handle indexing """
        cat = self.bastionLedger()
        url = '/'.join(self.getPhysicalPath())
        cat.catalog_object(self, url, idxs)
        
    def unindexObject(self):
        """ Handle unindexing """
        cat = self.bastionLedger()
        url = '/'.join(self.getPhysicalPath())
        cat.uncatalog_object(url)

    def reindexObject(self, idxs=[]):
        cat = self.bastionLedger()
        url = '/'.join(self.getPhysicalPath())
        try:
            cat.catalog_object(self, url, idxs)
        except KeyError:
            # Plone workflow reindexing ...
            pass

    def modifiable(self):
        """
        returns whether or not this transaction is still editable.  This means
        either in a non-posted state, or you've roles enough to repost it.
        """
        return self.status() in ('complete', 'incomplete') or \
            self.SecurityCheckPermission(ManageBastionLedgers)

    def manage_reverse(self, description='', effective=None, REQUEST=None):
        """
        create a reversal transaction
        """
        status = self.status()
        if status != 'posted':
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Transaction not in Posted state!')
                return self.manage_main(self, REQUEST)
            raise PostingError, '%s: Transaction not in Posted state (%s)!' % (self.getId(), status)

        txn = self.createTransaction(title=description or 'Reversal: %s' % self.title,
                                     effective=effective or self.effective_date)
        txn.setReference(self)

        for id,entry in self.entryItems():
            e = entry._getCopy(entry)
            e.amount = entry.amount * -1
            e.title = 'Reversal: %s' % entry.title
            # ensure the new entry does proper fx ...
            if getattr(entry, 'posted_amount', None):
                e.posted_amount = entry.posted_amount * -1
            txn._setObject(id, e)

        txn.manage_post()
        txn._status('postedreversal')
        
        self.setReference(txn)
	self._status('reversed')

        if not REQUEST:
            return txn
        return self.manage_main(self, REQUEST)


    def manage_cancel(self, REQUEST=None):
        """
        cancel a transaction
        """
        status = self.status()
        if status in ('incomplete', 'complete'):
            self._status('cancelled')
        else:
            raise InvalidTransition, 'cancel'
        
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_repost(self, force=False, REQUEST=None):
        """
        hmmm, sometimes/somehow stuff gets really f**ked up ...

        we also post complete txns - which could be processed via manage_post

        force causes fx/posted amounts to be recalculated and account totalisation
        to recur
        """
        status = self.status()
        if status in ('posted',):
            for entry in self.entryValues():
                try:
                    #if entry.absAmount() > 0.005:
                    entry._post(force=force)
                except PostingError:
                    raise
        if REQUEST:
            return self.manage_main(self, REQUEST)
        
    def manage_statusModify(self, workflow_action, REQUEST=None):
        """
        perform the workflow (very Plone ...)
        """
        try:
            self.content_status_modify(workflow_action)
        finally:
            pass

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'State Changed')
            return self.manage_main(self, REQUEST)

    def __str__(self):
        """ useful for debugging ... """
        return "<%s instance %s (%s) - %s>" % (self.meta_type, self.getId(),self.status(),
                                          str( map( lambda x: str(x), self.entryValues() ) ) )

    def __cmp__(self, other):
        """
        transactions are only the same if they've the same txn no. 
        this function is mainly for sorting based on effective date
        note that it's a *descending* (latest first) sort
        """
        if not isinstance(other, BLTransaction):
            return 1
        if self.getId() == other.getId():
            return 0
        if self.effective_date < other.effective_date:
            return 1
        else:
            return -1

    def asCSV(self, datefmt='%Y/%m/%d', REQUEST=None):
        """
        """
        return '\n'.join(map(lambda x: x.asCSV(datefmt), self.entryValues()))


    def _repair(self):
        if getattr(aq_base(self), 'entered_date', None):
            delattr(self, 'entered_date')
        map( lambda x:x._repair(), self.objectValues() )

    def manage_migrateFX(self, REQUEST=None):
        """
        in the past, we posted the fx rate into the fx_rate attribute of the posted entry
        now, we're actually going to post the txn's entry amount into the posted entry
        """
        if self.isMultiCurrency():
            # recalculate fx_rate
            self.manage_repost(force=True)

            for entry in self.entryValues():
                posted_amount = getattr(aq_base(entry),'posted_amount', None)
                if posted_amount:
                    delattr(entry, 'posted_amount')

            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Fixed up FX')
        else:
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Non-FX transaction - nothing to do')

        if REQUEST:
            return self.manage_main(self, REQUEST)
    
    def isForward(self):
        """
        return whether or not this is/was a forward-posted transaction
        """
        return self.status() == 'posted' and getattr(aq_base(self), '_forward', None)

AccessControl.class_init.InitializeClass(BLTransaction)


# deprecated API ...
class BLTransactions(LargePortalFolder, ZCatalog): pass


def addTransaction(ob, event):
    ob.indexObject()
    # f**k!! on import we have to recompute state so indexes (and the entire app)
    # aren't f**ked
    ob.setStatus()

def delTransaction(ob, event):
    try:
        # 'delete' anything posted to the account
        ob.manage_unpost()

        # remove from catalog
        ob.unindexObject()
    except AttributeError:
        # old-style unconverted ledger
        pass
