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

import AccessControl, string, copy, operator, types, logging, sys, StringIO
from Acquisition import aq_base, aq_parent
from AccessControl.Permissions import view_management_screens, access_contents_information
from DateTime import DateTime
from Acquisition import aq_base, aq_inner, aq_self
from OFS.ObjectManager import BeforeDeleteException
from OFS.PropertyManager import PropertyManager
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.AdvancedQuery import In, Eq
from zope.publisher.interfaces import IPublishTraverse
from webdav.Lockable import ResourceLockedError

from BLBase import *
from Products.BastionLedger.BLGlobals import EPOCH, ACC_TYPES
from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES

from interfaces.ledger import ILedger, IBLLedger
from BLAccount import BLAccount
from BLTransaction import BLTransaction, manage_addBLTransaction
from BLEntry import BLEntry
from BLProcess import BLProcess
from BLReport import BLReportFolder
from Exceptions import MissingAssociation
from Permissions import ManageBastionLedgers, OperateBastionLedgers
from Products.CMFCore import permissions

MARKER = []
LOG = logging.getLogger('BLLedger')

def assoc_cmp(x,y):
    t1 = x['tag']
    t2 = y['tag']
    if t1 < t2: return -1
    if t1 > t2: return 1
    return 0

manage_addBLLedgerForm = PageTemplateFile('zpt/add_blledger', globals())
def manage_addBLLedger(self, id, title, currencies, REQUEST=None):
    """ a double entry ledger - you shouldn't be able to directly create one of these ... """

    try:
        self._setObject(id, BLLedger(id, title, currencies))
    except:
        # TODO: a messagedialogue ..
        raise
    
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class LedgerBase(LargePortalFolder, ZCatalog):
    """
    A ledger.  The common sheet is to define extension fields to all account objects.
    """
    implements(IPublishTraverse)

    Types = ACC_TYPES

    account_types = ('BLAccount',)
    transaction_types = ('BLTransaction',)

    _properties = LargePortalFolder._properties + (
        {'id':'currencies',         'type':'lines',     'mode':'w'},
        {'id':'account_prefix',     'type':'string',    'mode':'w'},
        {'id':'txn_prefix',         'type':'string',    'mode':'w'},
        {'id':'email',              'type':'string',    'mode':'w'},
        {'id':'account_types',      'type':'lines',     'mode':'r'}, 
        {'id':'transaction_types',  'type':'lines',     'mode':'r'}, 
        )

    __ac_permissions__ = LargePortalFolder.__ac_permissions__ + (
        (OperateBastionLedgers, ('createTransaction', 'createTransactions',
                                 'manage_reverse',
                                 'manage_post', 'manage_cancel', 
                                 'nextAccountId', 'nextTxnId')),
        (ManageBastionLedgers, ('manage_edit', 'manage_delTags', 'manage_addTag',
                                'manage_renameTags', 'manage_repost', 'manage_fixAccountId',
                                'manage_endOfDay') ),
        (view_management_screens, ('manage_accounts', 'manage_transactions',
                                   'manage_processes', 'manage_Reports',) ),
        (access_contents_information, ('accountValues', 'accountIds', 'accountValuesAdv', 'subtypes',
                                       'sum', 'debitTotal', 'creditTotal', 'total',
                                       'add', 'asCSV', 'totals', 'asXML', 
                                       'accountXML', 'transactionXML',
                                       'syndicationQuery',
                                       'manage_downloadCSV', 'itAssociations',
                                       'accnosForTag', 'zeroAmount',
                                       'lastTransaction', 'firstTransaction',
                                       'transactionValues', 'transactionIds', 
                                       'transactionValuesAdv', 'defaultCurrency', 'supportedCurrencies',
                                       'entryValues', 'allCurrencies', 'nextAccountId', 'nextTxnId',
                                       'currentAccountId', 'currentTxnId',
                                       'emailAddress', 'thisLedger')),
        )
    #dontAllowCopyAndPaste=0
    #__allow_access_to_unprotected_subobjects__ = 1

    manage_options = (
        #{'label': 'Extensions',   'action': 'manage_common_sheet',
        #             'help':('BastionLedger', 'account_attrs.stx')},
        {'label': 'Accounts',     'action': 'manage_accounts' },
        {'label': 'View',         'action': '' },
        {'label': 'Associations', 'action': 'manage_associations' },
        {'label': 'Transactions', 'action': 'manage_transactions' },
        {'label': 'Properties',   'action': 'manage_propertiesForm',
         'help':('BastionLedger', 'ledger.stx') },
        {'label': 'Reports',      'action': 'manage_Reports' },
        {'label': 'Processes',    'action': 'manage_processes' },
    ) + PortalFolder.manage_options[1:]

    manage_propertiesForm = PageTemplateFile('zpt/edit_ledger', globals())
    manage_associations = PageTemplateFile('zpt/associations', globals())
    manage_accounts = PageTemplateFile('zpt/view_chart', globals())
    manage_main = PageTemplateFile('zpt/view_chart', globals())
    manage_transactions = PageTemplateFile('zpt/view_transactions', globals())
    manage_processes = PageTemplateFile('zpt/processes', globals())
    
    manage_btree = LargePortalFolder.manage_main
    manage_zpropertiesForm = LargePortalFolder.manage_propertiesForm

    asXML = PageTemplateFile('zpt/xml_blledger', globals())

    def manage_Reports(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect('Reports/manage_main')

    def __init__(self, id, title, currencies, account_id=1, account_prefix='A',
                 txn_id=1, txn_prefix='T'):
        LargePortalFolder.__init__(self, id)
        ZCatalog.__init__(self, id, title)
        self.Reports = BLReportFolder('Reports','')
        LedgerBase.manage_edit(self, title, title,  txn_id, account_id, 
                               account_prefix, txn_prefix, currencies)

    def thisLedger(self):
        """
        find the ledger by acquisition
        """
        return self

    def displayContentsTab(self):
        """ 
        we don't allow copy/paste/delete etc
        """
        return False

    def blAccountStatuses(self):
        """
        """
        statuses = getToolByName(self, 'portal_workflow')._getOb('blaccount_workflow').states.objectIds()
        statuses.sort()
        return statuses

    def createTransaction(self, effective=None, title='',entries=[], tags=[], ref=None):
        """
        return a newly created BLTransaction
        """
        txn_id = manage_addBLTransaction(self, 
                                         title=title, 
                                         effective=effective or DateTime(),
                                         ref=ref,
                                         entries=entries,
                                         tags=tags)
        return self._getOb(txn_id)

    def createTransactions(self, entries, accno, ledger='', post=True):
        """
        create a bunch of transactions on given accno (in given ledger - otherwise this ledger), 
        returning the list of transactions 
        all the entries are on accounts in this ledger
        """
        txns = []
        if ledger and ledger != self.getId():
            account = self.aq_parent._getOb(ledger).accountValues(accno=accno)[0]
        else:
            account = self.accountValues(accno=accno)[0]
        for entry in entries:
            other = self.accountValues(accno=entry['accno'])[0]
            txn = account.createTransaction(effective=entry['effective'],
                                            title=entry['title'])
            account.createEntry(txn, -entry['amount'])
            other.createEntry(txn, entry['amount'])

            if post:
                txn.manage_post()
            txns.append(txn)
        return txns

    def manage_edit(self, title, description, txn_id, account_id, account_prefix,
                    txn_prefix, currencies, email='', REQUEST=None):
        """
        """
        self.title = title
        self.description = description
        self.currencies = currencies
        self.account_prefix = account_prefix
        self.txn_prefix = txn_prefix
        self._next_txn_id = int(txn_id)
        self._next_account_id = int(account_id)
        self.email = email
        if REQUEST is not None:
            REQUEST.set('manage_tabs_message', 'Updated')
            REQUEST.set('management_view', 'Properties')
            return self.manage_propertiesForm(self, REQUEST)

    #
    # WARNING!!!
    #
    # we *cannot* create a __getattr__ and *still* use getToolByName
    # to find our portal_bastionledger - death by (silent) recursion
    # failure ...
    #
    def publishTraverse(self, REQUEST, name):
        """
        if we can't find the object - go see if it's a BLProcess and then dispatch
        it ala this ledger
        """
        #LOG.info('publishTraverse(%s)' % name)
        ob = LargePortalFolder.publishTraverse(self, REQUEST, name)
        return ob or self._getProcess(name)

    def _getProcess(self, name):
        """
        go see if the name is a process, and if so, return it in our acquisition context
        """
        if not name.startswith('_'):
            LOG.debug('_getProcess(%s)' % name)
            tool = getToolByName(aq_parent(self), 'portal_bastionledger')
            try:
                obj = tool._getOb(name)
                if isinstance(obj, BLProcess):
                    return aq_base(obj).__of__(self)
            except (AttributeError, KeyError):
                pass
        return None

    def all_meta_types(self):
        """
        this is needed to identify pasteable types (for non-visibles ...)
        """
        return filter(lambda x: x,
                      map(lambda x: ProductsDictionary(x),
                          self.account_types + self.transaction_types)) 

    def accountValues(self, **kw):
        """
        return all the accounts - if you pass kw, it does a catalog search
        """
        if kw:
            query = dict(kw)
            if query.has_key('tags'):
                accnos = self.accnosForTag(query['tags'])
                del query['tags']
                if accnos:
                    if query.has_key('accno'):
                        query['accno'].extend(accnos)
                    else:
                        query['accno'] = accnos
                elif not query:
                    # if no accnos from tags, and no other query, bail because
                    # otherwise we'll get an unrestricted query
                    return []
            query['meta_type'] = self.account_types
            query['ledgerId'] = self.getId()
            #return map(lambda x: x._unrestrictedGetObject(), 
            #           self.bastionLedger().searchResults(**query))
            results = []
            for brainz in self.bastionLedger().searchResults(**query):
                try:
                    acc = brainz._unrestrictedGetObject()
                except:
                    # user permissions??
                    continue
                results.append(acc)
            return results
        return self.objectValues(self.account_types)

    def accountValuesAdv(self, query, sortSpecs=(), withSortValues=None):
        """
        return all the accounts meeting the AdvancedQuery criteria
        """
        # TODO - withSortValues ...
        results = []
        for brainz in self.bastionLedger().evalAdvancedQuery(query & \
                                                                 In('meta_type', self.account_types) & \
                                                                 Eq('ledgerId', self.getId(), filter=True), 
                                                             sortSpecs):
            try:
                acc = brainz._unrestrictedGetObject()
            except:
                # wtf - user permissions ...
                continue
            results.append(acc)
        return results

    def transactionValues(self, REQUEST={}, **kw):
        """
        return all the transactions - if you pass kw, it does a catalog search
        """
        if kw or REQUEST:
            query = {'meta_type':self.transaction_types}
            if REQUEST:
                query.update(REQUEST.form)
            # overwrite any form parameters ...
            if kw:
                query.update(kw)

            from_date = to_date = None
            if query.has_key('from_date') and not query.has_key('effective'):
                try:
                    from_date = DateTime(query['from_date'])
                except:
                    pass
            if query.has_key('to_date') and not query.has_key('effective'):
                try:
                    to_date = DateTime(query['to_date'])
                except:
                    pass

            if from_date and to_date:
                query['effective'] = {'query': (from_date, to_date), 'range':'min:max'}
            elif from_date:
                query['effective'] = {'query': from_date, 'range':'min'}
            elif to_date:
                query['effective'] = {'query': to_date, 'range':'max'}
                
            query['ledgerId'] = self.getId()
            #LOG.info('Querying Transactions: %s' % str(query))
            return map(lambda x: x._unrestrictedGetObject(), 
                       self.bastionLedger().searchResults(**query))
        return self.objectValues(self.transaction_types)

    def transactionValuesAdv(self, query, sortSpecs=(), withSortValues=None):
        """
        return all the transactions meeting the AdvancedQuery criteria
        """
        # TODO - withSortValues ...
        return map(lambda x: x._unrestrictedGetObject(), 
                   self.bastionLedger().evalAdvancedQuery(query & \
                                                              In('meta_type', self.transaction_types) & \
                                                              Eq('ledgerId', self.getId(), filter=True), 
                                                          sortSpecs))

    def entryValues(self, REQUEST={}, **kw):
        """
        return all the entries - if you pass kw, it does a catalog search,
        sort order is as per txn sorting
        """
        results = []
        for txn in self.transactionValues(REQUEST, **kw):
            results.extend(txn.entryValues())
        return results

    def accountIds(self, **kw):
        if kw:
            return map(lambda x: x.getId(), self.accountValues(**kw))
        return self.objectIds(self.account_types)

    def transactionIds(self, **kw):
        if kw:
            return map(lambda x: x.getId(), self.transactionValues(**kw))
        return self.objectIds(self.transaction_types)
    
    def lastTransaction(self):
        """
        return the last transaction (by date) in a ledger
        """
        brainz = self.bastionLedger().searchResults(meta_type=self.transaction_types,
                                                    ledgerId=self.getId(),
                                                    sort_on='effective',
                                                    sort_order='descending')
        if brainz:
            return brainz[0]._unrestrictedGetObject()

        return None

    def firstTransaction(self):
        """
        return the first transaction (by date) in a ledger
        """
        brainz = self.bastionLedger().searchResults(meta_type=self.transaction_types,
                                                    ledgerId=self.getId(),
                                                    sort_on='effective',
                                                    sort_order='ascending')
        if brainz:
            return brainz[0]._unrestrictedGetObject()

        return None

    def nextTxnId(self):
        id = str(self._next_txn_id)
        self._next_txn_id += 1
        return "%s%s" % (self.txn_prefix, string.zfill(id, 12))

    def nextAccountId(self):
        id = str(self._next_account_id)
        self._next_account_id += 1
        return "%s%s" % (self.account_prefix, string.zfill(id, 6))

    def _resetNextAccountId(self, value):
        """ hmmm - if you really *must* tweak our private data """
        self._next_account_id = value

    def generateUniqueId(self, type=None):
        """
        ham it up for Plone's createObject and portal_factory
        """
        if type.find('Transaction') != -1:
            return self.nextTxnId()
        elif type.find('Account') != -1 or type in ('BLShareholder', 'BLEmployee'):
            return self.nextAccountId()
        else:
            # ok we want to call the plone skin and have to throw it up past all this
            # BL stuff ....
            return getToolByName(self, 'portal_url').generateUniqueId(type)

    def defaultCurrency(self):
        """ either the first currency in the list, or the Ledger's """
        if len(self.currencies) > 0:
            return self.currencies[0]
        return self.aq_parent.currency
    
    def supportedCurrencies(self):
        """
        BastionBanking/Payee API
        """
        return self.currencies

    def allCurrencies(self):
	""" list acceptable currencies (with the ledger default first in list)"""
        currencies = list(self.portal_bastionledger.Currencies())
        default = self.aq_parent.currency
        # hmmm - hackery in case our parent isn't really a Ledger ;)
        if callable(default):
            default = default()
        try:
            currencies.remove(default)
        except:
            pass
        return [ default ] + currencies

    def _delObject(self, id, tp=1, suppress_events=False):
        ob = self._getOb(id)
        if not self.expertMode() and issubclass(ob.__class__, BLAccount) and not ob.balance() == 0:
            raise BeforeDeleteException, 'Account(%s) has a balance!' % ob.getId()
        LargePortalFolder._delObject(self, id, tp, suppress_events=suppress_events)

    def currentAccountId(self):
        return self._next_account_id

    def currentTxnId(self):
        return self._next_txn_id
    
    #
    # reroute these guys (from OFS.CopySupport) ....
    #
    def manage_cutObjects(self, ids=None, REQUEST=None):
        """Put a reference to the objects named in ids in the clip board"""
        cp = LargePortalFolder.manage_cutObjects(self, ids)
        if REQUEST is not None:
            resp=REQUEST['RESPONSE']
            resp.setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
            REQUEST['__cp'] = cp
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))
        return cp

    def manage_copyObjects(self, ids=None, REQUEST=None, RESPONSE=None):
        """Put a reference to the objects named in ids in the clip board"""
        cp = LargePortalFolder.manage_copyObjects(self, ids)
        if REQUEST is not None:
            resp=REQUEST['RESPONSE']
            resp.setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
            REQUEST['__cp'] = cp
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))
        return cp
    
    def manage_pasteObjects(self, cb_copy_data=None, REQUEST=None):
        """Paste previously copied objects into the current object.
           If calling manage_pasteObjects from python code, pass
           the result of a previous call to manage_cutObjects or
           manage_copyObjects as the first argument."""
        if cb_copy_data is not None:
            cp=cb_copy_data
        else:
            if REQUEST and REQUEST.has_key('__cp'):
                cp=REQUEST['__cp']
        try:
            result = LargePortalFolder.manage_pasteObjects(self, cp)
        except:
            raise
        
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))
        return result
    
    def manage_renameObjects(self, ids=[], new_ids=[], REQUEST=None):
        """Rename several sub-objects"""
        LargePortalFolder.manage_renameObjects(self, ids, new_ids)
        #
        # hmmm - there is no dispatch_to here because we'd have to edit the rename form ...
        #
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))


    def manage_renameObject(self, id, new_id, REQUEST=None):
        """Rename a particular sub-object (account, txn)"""
        
        LargePortalFolder.manage_renameObject(self, id, new_id)
        #
        # hmmm - there is no dispatch_to here because we'd have to edit the rename form ...
        #
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))

    def manage_fixAccountId(self, id, REQUEST=None):
        """
        helper to fix/serialise account numbers - you probably don't need this unless you've
        been screwing with the API's
        """
        ob = self._getOb(id)

        if ob.wl_isLocked():
            raise ResourceLockedError('Object "%s" is locked via WebDAV'
                                      % ob.getId())
        LargePortalFolder._delObject(self, id)
        ob = aq_base(ob)

        new_id = self.nextAccountId()
        ob._setId(new_id)
        ob.manage_changeProperties(accno=new_id)
        self._setObject(new_id, ob, set_owner=0)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))



    def emailAddress(self):
        """
        return email address
        """
        email = self.email
        if email.find('<') != -1:
            return email
        return '"%s" <%s>' % (self.getId(), email)

    def __str__(self):
        return "<%s instance %s at %s)>" % (self.meta_type,
                                            self.getId(),
                                            self.absolute_url())

    __repr__ = __str__


    def _reset(self):
        """ remove everything except accounts """
        ledger = self.bastionLedger()
        zero = ledger.zeroAmount()
        baseurl = '/'.join(self.getPhysicalPath())

        # TODO - wtf OIBTree should step through ...
        for txnid in list(self.transactionIds()):
            # event suppression for both speed and unsupported currencies in fx conversions
            self._delObject(txnid, suppress_events=True)
            ledger.uncatalog_object('%s/%s' % (baseurl, txnid))

        for account in self.accountValues():
            # delete all the Orders, Payslips etc stuffed in the account(s)
            account.manage_delObjects(filter(lambda x: x not in account.objectIds('BLControlEntry'), 
                                             account.objectIds()))
            # be paranoid and ensure everything is zero
            account.manage_setBalance(zero, EPOCH)
        self._next_txn_id = 1

    def manage_delObjects(self, ids=[], REQUEST=None):
        """
        """
        for id in ids:
            try:
                LargePortalFolder._delObject(self, id)
            except KeyError:
                pass
        # dispatch get's f**ked up - need to identify what came from txn view ...
        if REQUEST:
            if REQUEST.get('sort_on','') == 'effective':
                return self.manage_transactions(self, REQUEST)

            return self.manage_main(self, REQUEST)

    def manage_delTags(self, ids, REQUEST=None):
        """
        Remove tags from underlying accounts
        """
        # we're only blitzing local tags :)
        for account in self.accountValues(tags=ids):
            tags = list(account.tags)
            for tag in ids:
                if tag in tags:
                    tags.remove(tag)
            account.updateTags('tags', tags)
        if REQUEST:
            REQUEST.set('management_view', 'Associations')
            REQUEST.set('manage_tabs_message', 'Deleted %s' % ', '.join(ids))
            return self.manage_associations(self, REQUEST)

    def manage_addTag(self, tag, accnos=[], REQUEST=None):
        """
        add the tag to the specified list of account ids
        """
        assoc = getToolByName(self, 'portal_bastionledger').associations.get(tag)

        if not assoc and accnos:
            for account in self.accountValues(accno=accnos):
                tags = list(account.tags)
                if tag not in tags:
                    tags.append(tag)
                    account.updateTags(tags)
        if REQUEST:
            REQUEST.set('management_view', 'Associations')
            return self.manage_associations(self, REQUEST)

    def manage_renameTags(self, ids, tag, REQUEST=None):
        """
        rename tags in underlying accounts
        """
        for id in ids:
            for account in self.accountValues(tags=id):
                tags = list(account.tags)
                tags.remove(id)
                tags.append(tag)
                account.updateTags(tags)
        if REQUEST:
            REQUEST.set('management_view', 'Associations')
            return self.manage_associations(self, REQUEST)

    def itsAssociations(self):
        """
        return a hash of local and global associations (tags)
        """
        results = {}
        bltool = getToolByName(self, 'portal_bastionledger', None)
        if bltool:
            associations = getattr(bltool, 'associations', None)
            if associations:
                for assoc in map(lambda x: {'tag':x.getId(),
                                            'title': x.title,
                                            'description': x.description,
                                            'accno': x.accno,
                                            'global':True},
                                 map(lambda x: x._unrestrictedGetObject(), 
                                     associations.searchResults(ledger=self.getId()))):
                    results[assoc['tag']] = assoc
        # f**k knows why we get None in this ...
        bl = self.bastionLedger()
        for tag in filter(lambda x:x,bl.uniqueValuesFor('tags')):
            if results.has_key(tag):
                accnos = results[tag]['accno']
                for accno in map(lambda x:x['accno'], 
                                 bl.evalAdvancedQuery(In('tags', [tag]) & \
                                                          Eq('ledgerId', self.getId(), filter=True))):
                    if accno not in accnos:
                        accnos.append(accno)
            else:
                results[tag] = {'tag': tag,
                                'title':'',
                                'description':'',
                                'accno': map(lambda x:x['accno'],
                                             bl.evalAdvancedQuery(In('tags', [tag]) & \
                                                                      Eq('ledgerId', self.getId(), filter=True))),
                                'global':False}
        results = results.values()
        results.sort(assoc_cmp)
        return results

    def missingAssociations(self):
        """
        return any associations that aren't present in this ledger
        """
        bltool = getToolByName(self, 'portal_bastionledger', None)
        if bltool:
            associations = getattr(bltool, 'associations', None)
            if associations:
                return associations.missingForLedger(self)
        return []

    def accnosForTag(self, tag):
        """
        return a list of accno's that meet the tag requirement (useful for advanced
        query filtering)
        """
        # local tags
        accnos = map(lambda x: x['accno'], 
                     self.bastionLedger().searchResults(ledgerId=self.getId(),
                                                        tags=tag))

        # global tags
        bltool = getToolByName(self, 'portal_bastionledger')
        for af in bltool.objectValues('BLAssociationFolder'):
            accnos.extend(af.accnosForLedger(tag, self))

        return accnos

    def subtypes(self, type=''):
        if type:
            ret = []
            for stype in map(lambda x: x['subtype'], self.bastionLedger().evalAdvancedQuery(Eq('type',type))):
                if stype == '':
                    continue
                if ret.count(stype) == 0:
                    ret.append(stype)
            return ret
        else:
            return self.bastionLedger().uniqueValuesFor('subtype')

    def debitTotal(self, effective=None, *args, **kw):
        """
        return the debit side of the query
        """
        return self.add(self.accountValues(**kw), 
                        self.defaultCurrency(), 
                        effective, 
                        BLAccount.debitTotal)

    def creditTotal(self, effective=None, *args, **kw):
        """
        return the credit side of the query
        """
        return self.add(self.accountValues(**kw), 
                        self.defaultCurrency(), 
                        effective, 
                        BLAccount.creditTotal)

    # TODO - this should degenerate into sum() with a date-ranged effective...
    def total(self, currency=None, effective=None):
        """
        calculate the value of the ledger
        effective should be a date range
        """
        # TODO - directly use ledger cache values in period infos
        return self.add(self.accountValues(), 
                        currency or self.defaultCurrency(), 
                        effective, 
                        BLAccount.total)

    def add(self, acclist, currency, effective, function):
        """
        apply function to acclist, adding the results
        """
        amount = ZCurrency(currency, 0)
        for account in acclist:
            amount += function(account, currency=currency, effective=effective)
        return amount

    def sum(self, currency=None, effective=None, tags=[], query={}, **kw):
        """
        sums and returns a ZCurrency amount for an account query.
        if the effective date is a list, it will summate only the entries
        valid in that list range, otherwise it'll do balances as per that 
        date (or now)
        you can pass in an advanced query, or you can pass in a dict - if
        you pass in a dict, any key words will also be incorporated into
        the query
        """
        accnos = []
        if tags:
            if type(tags) not in (types.ListType, types.TupleType):
                tags = [tags]
            for t in tags:
                for accno in self.accnosForTag(t):
                    if accno not in accnos:
                        accnos.append(accno)

        if type(query) == types.DictType:
            query.update(kw)
            if accnos:
                if not query.has_key('accno'):
                    query['accno'] = accnos
                else:
                    query['accno'].extend(accnos)
            #print "sum: Normal query(%s)" % query
            acclist = self.accountValues(**query)
        else:
            acclist = self.accountValuesAdv(query)
        if effective and type(effective) in (types.TupleType, types.ListType):
            func = BLAccount.total
        else:
            func = BLAccount.balance
        return self.add(acclist, 
                        currency or self.defaultCurrency(), 
                        effective or DateTime(), 
                        func)
    # TODO
    #total = sum

    def manage_reverse(self, ids=[], REQUEST=None):
        """ generate and apply reversal entries """
        for id in ids:
            self._getOb(id).manage_reverse()
        if REQUEST:
            return self.manage_transactions(self, REQUEST)

    def manage_post(self, ids=[], REQUEST=None):
        """
        set Unposted transaction(s) status to posted
        """
        for id in ids:
            txn = self._getOb(id)
            txn.manage_post()

        if REQUEST:
            return self.manage_transactions(self, REQUEST)
            
    def manage_cancel(self, ids=[], REQUEST=None):
        """
        set Unposted transaction(s) status to cancelled
        """
        for id in ids:
            txn =self._getOb(id)
            if txn.status() == 'posted':
                txn.manage_reverse()
	    elif txn.status() in ('incomplete', 'complete'):
		txn.manage_cancel()
        if REQUEST:
            return self.manage_transactions(self, REQUEST)

    def manage_repost(self, ids=[], REQUEST=None):
        """
        hmmm - repost transactions - shouldn't be necessary, but useful
        if copy/pasting between ledger instances and may form part of a
        future 'playback' feature
        """
        for id in ids:
            txn = self._getOb(id)
            txn.manage_repost()

        if REQUEST:
            return self.manage_transactions(self, REQUEST)

    def manage_endOfDay(self, from_date, to_date, REQUEST=None):
        """
        specific end-of-day processing
        """
        # TODO - make this registration/utility stuff ...
        pass

    def zeroAmount(self):
        """
        return a zero amount in the default currency of the ledger
        """
        return ZCurrency('%s 0.00' % self.defaultCurrency())

    def asCSV(self, datefmt='%Y/%m/%d', curfmt='%0.2f', txns=True, REQUEST=None):
        """
        comma-separated transaction/account entries

        the default currency representation is float - use %a (or something with %c) for
        currency code inclusion
        """
        if txns:
            return '\n'.join(map(lambda x: x.asCSV(datefmt, curfmt),
                                 self.transactionValues()))
        else:
            return '\n'.join(map(lambda x: x.asCSV(datefmt, curfmt),
                                 self.accountValues()))

    def manage_downloadCSV(self, REQUEST, RESPONSE, datefmt='%Y/%m/%d', curfmt='%0.2f', txns=True):
        """
        comma-separated transaction/account entries

        the default currency representation is float - use %a (or something with %c) for
        currency code inclusion
        """
        RESPONSE.setHeader('Content-Type', 'application/octetstream')
        RESPONSE.setHeader('Content-Disposition',
                           'inline; filename=%s.csv' % self.getId().lower())
        RESPONSE.write(self.asCSV(datefmt, curfmt, txns))

    #
    # Syndication Stuff
    # 
    searchObjects = accountValues

    def syndicationQuery(self):
        """
        """
        return {'meta_type':self.account_types,
                'created':{'query':DateTime() - 1,
                           'range':'min'}}

    def _postCopy(self, container, op=0):
        # Called after the copy is finished to accomodate special cases.
        # The op var is 0 for a copy, 1 for a move.
        self.manage_catalogClear()
        self.ZopeFindAndApply(self,
                              obj_metatypes=self.account_types + self.transaction_types,
                              obj_ids=None,
                              obj_searchterm=None,
                              obj_expr=None,
                              obj_mtime=None,
                              obj_mspec=None,
                              obj_permission=None,
                              obj_roles=None,
                              search_sub=1,
                              REQUEST={},
                              apply_func=self.aq_parent.catalog_object,
                              apply_path= '/'.join(self.getPhysicalPath()))

    def totals(self, dates, format=None):
        """
        return balance information for a date range
        if supplied, format should be a currency format eg ('%0.2f')
        """
        if format:
            return map(lambda x: self.total(effective=x).strfcur(format), dates)
        return map(lambda x: self.total(effective=x), dates)
        
    def accountXML(self):
        """
        the accounts in XML format
        """
        output = StringIO.StringIO('<accounts>')
        for account in self.accountValues():
            output.write(account.asXML())
            output.write('\n')
        output.write('</accounts>')
        return output.getvalue()

    def transactionXML(self):
        """
        the transactions in XML format
        """
        output = StringIO.StringIO('<transactions>')
        for txn in self.transactionValues():
            output.write(txn.asXML())
            output.write('\n')
        output.write('</transactions>')
        return output.getvalue()

    def numberAccounts(self):
        return len(self.bastionLedger().searchResults(meta_type=self.account_types, 
                                                      ledgerId=self.getId()))

    def numberTransactions(self):
        return len(self.bastionLedger().searchResults(meta_type=self.transaction_types, 
                                                      ledgerId=self.getId()))                          

    def ledgerId(self):
        """
        indexing
        """
        return self.getId()

    def _repair(self):
        if not getattr(aq_base(self), '_catalog', None):
            ZCatalog.__init__(self, self.id, self.title)

        if getattr(aq_base(self), 'Processes', None):
            try:
                delattr(self, 'Processes')
            except:
                pass

        if not getattr(aq_base(self),'Reports', None):
            self.Reports = BLReportFolder('Reports')

        for fn in (self.accountValues, self.transactionValues):
            for entry in fn():
                entry._repair()



class BLLedger(LedgerBase):
    """
    A ledger.  The common sheet is to define extension fields to all account objects.

    """
    meta_type = portal_type = 'BLLedger'

    implements(IBLLedger)

AccessControl.class_init.InitializeClass(BLLedger)


def cookie_path(request):
    # Return a "path" value for use in a cookie that refers
    # to the root of the Zope object space.
    return request['BASEPATH1'] or "/"

def accno_field_cmp(x, y):
    if x.accno == y.accno: return 0
    if x.accno > y.accno: return 1
    return -1

