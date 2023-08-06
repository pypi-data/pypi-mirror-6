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

# import stuff
import AccessControl, base64, logging, operator, os, time, types
from xhtml2pdf.document import pisaDocument
from StringIO import StringIO
from AccessControl.Permissions import view_management_screens, access_contents_information
from DateTime import DateTime, Timezones
from Acquisition import aq_base
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.ObjectManager import REPLACEABLE
from OFS.PropertyManager import PropertyManager
from DocumentTemplate.DT_Util import html_quote
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES
from Products.AdvancedQuery import In
#
# get our local sub-helpers ...
#
from BLBase import *
from BLLedger import LedgerBase
from BLInventory import manage_addBLInventory
from BLOrderBook import manage_addBLOrderBook
from BLSubsidiaryLedger import BLSubsidiaryLedger, manage_addBLSubsidiaryLedger
from BLShareholderLedger import manage_addBLShareholderLedger
from BLQuoteManager import manage_addBLQuoteManager

from catalog import makeLedgerCatalog

#
# Payroll is moving to a separate framework
#
try:
    from BLPayroll import manage_addBLPayroll
    DO_PAYROLL = True
except:
    DO_PAYROLL = False
from BLReport import BLReportFolder
from BLPeriodInfo import BLLedgerPeriodsFolder
from BLTransaction import manage_addBLTransaction
from BLEntry import manage_addBLEntry
from BLGlobals import EPOCH
from utils import ceiling_date, floor_date
from Permissions import OperateBastionLedgers, ManageBastionLedgers, GodAccess
from Exceptions import PostingError, MissingAssociation, UnbalancedError
from interfaces.tools import IBLLedgerTool, IBLLedgerToolMultiple
from interfaces.ledger import IBastionLedger
from catalog import rebuildLedgerCatalogs, recatalogLedger, removeAllIndexes
from zope.interface import Interface, implements

LOG = logging.getLogger('BastionLedger')


from lxml import etree
from lxml import objectify

parser = etree.XMLParser(remove_blank_text=False,
                         dtd_validation=False,
                         resolve_entities=False,
                         encoding='UTF-8', 
                         ns_clean=True, 
                         compact=False, 
                         recover=True)


manage_addLedgerForm = PageTemplateFile('zpt/add_Ledger', globals())

def manage_addLedger(self, id, title='', currency='', accrued_to=None, REQUEST=None, submit=None):
    """ adds a ledger """
    if not currency:
        currency = getToolByName(self, 'portal_bastionledger').Ledger.defaultCurrency()

    self._setObject(id, Ledger(id, title, 'Default', 666, currency, accrued_to=accrued_to))

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect("%s/%s/manage_workspace" % (REQUEST['URL3'], id))
        
    return self._getOb(id)


def addBastionLedger(self, id, title=''):
    """
    Plone add ledger
    """
    ledger = manage_addLedger(self, id, title)
    return id

def attrCompare(x, y, attr):
    """
    compare named attribute from objects x and y
    """
    x_attr = getattr(x, attr)
    y_attr = getattr(y, attr)

    if callable(x_attr):
        x_attr = x_attr()
    if callable(y_attr):
        y_attr = y_attr()

    if x_attr > y_attr:
        return 1
    if x_attr < y_attr:
        return -1

    return 0

class Ledger(PortalFolder, ZCatalog, PropertyManager, PortalContent):
    """
    The Accountancy offering.

    This class is a container for other BastionLedger sub-products and
    the chart of accounts.
    """
    implements(IBastionLedger)
    
    __replaceable__ = REPLACEABLE
    dontAllowCopyAndPaste = 0
    meta_type = portal_type = 'Ledger'
    _reserved_names = ('Ledger', )
    timezone = 'UTC'
    industry_code = ''

    __ac_permissions__ = ZCatalog.__ac_permissions__ + (
        (access_contents_information, ('zeroAmount', 'ledgerLocalizedTime', 'inventoryValues', 'saveSearch',
                                       'ledgerValues', 'transactionValues', 'transactionValuesAdv', 'entryValues',
                                       'accountValues',
                                       'defaultCurrency', 'numberTransactions', 'emailAddress',  'blTransactionStatuses',
                                       'normalizedDate', 'requiresEOD')),
        (View, ('grossProfit', 'lossesAttributable', 'netProfit', 'corporationTax',
                'profitLossAcc', 'accruedIncomeTaxAcc', 'bastionLedger',
                'manage_downloadCSV', 'getLedgerProperty', 'directorInfo', 'secretaryInfo')),
        (view_management_screens, ('manage_edit', 'ledgerUniqueId', 'manage_periods', 'manage_reports',
                                   'manage_verify', 'verifyExceptions', 'manage_transactions')),
        (GodAccess, ('manage_reset',)),
        (OperateBastionLedgers, ('manage_navigationIndex', 'moveTransaction')),
        (ManageBastionLedgers, ('manage_post', 'manage_repost', 'manage_repostAll', 'manage_reverse', 'manage_dailyEnd'
                                'manage_periodEnd', 'manage_periodEndReports', 'manage_recalculateControls',
                                'manage_recalculateBalances', 
                                'manage_refreshCatalog', 'manage_replaceLedger', 'manage_fixupCatalogs',
                                'manage_resetPeriods', 'manage_verifyRepost', 'manage_periodUndo')),
    ) + PropertyManager.__ac_permissions__ + PortalContent.__ac_permissions__

    property_extensible_schema__ = 1
    _properties = (
	 { 'id':'title',              'type':'string', 'mode':'w' },
         { 'id':'company_number',     'type':'string', 'mode':'w' },
         { 'id':'incorporation_date', 'type':'date',   'mode':'w' },
         { 'id':'address',            'type':'text',   'mode':'w' },
         { 'id':'directors',          'type':'lines',  'mode':'w' },
         { 'id':'secretary',          'type':'string', 'mode':'w' },
         { 'id':'tax_number',         'type':'string', 'mode':'w' },
         { 'id':'industry_code',      'type':'string', 'mode':'w' },
         { 'id':'currency',           'type':'string', 'mode':'r' },
         { 'id':'timezone',           'type':'selection', 'mode':'w',
           'select_variable': 'TimeZones'},
         { 'id':'unique_identifier',  'type':'string', 'mode':'r' },
         { 'id':'accrued_to',         'type':'date',   'mode':'w' },
    )
                    
    manage_options =  (
        {'label': 'Contents',       'action': 'manage_main',
         'help':('BastionLedger', 'system.stx')  }, 
        {'label': 'View',           'action': ''},
        {'label': 'Properties',     'action': 'manage_propertiesForm',
         'help':('BastionLedger', 'system_props.stx') },
        {'label': 'Verify',         'action': 'manage_verify' },
        {'label': 'Transactions',   'action': 'manage_transactions' },
        {'label': 'Balance Sheet',  'action': 'blbalance_sheet' },
        {'label': 'Revenue Stmt',   'action': 'blrevenue_statement'},
        {'label': 'Cashflow Stmt',  'action': 'blcashflow_statement'},
        {'label': 'Periods',        'action': 'manage_periods'},
        {'label': 'Reports',        'action': 'manage_reports'},
        ) + PortalContent.manage_options

    manage_verify = PageTemplateFile('zpt/verify_ledger', globals())
    manage_transactions = PageTemplateFile('zpt/view_transactions', globals())
    asXML = PageTemplateFile('zpt/xml_ledger', globals())

    #
    # this needs lots more thought ...
    #
    #manage_sync = PageTemplateFile('zpt/view_reports', globals())

    def __init__(self, id, title, locale_id, unique_id, currency='USD', timezone='UTC', accrued_to=None):
        ZCatalog.__init__(self, id, title)
        self._locale = locale_id
        self.currency = currency
        self.timezone = timezone
        self.unique_identifier = unique_id
        self.company_number = ''
        self.incorporation_date = ''
        self.address = ''
        self.tax_number = ''
        self.industry_code = ''
        self.directors = []
        self.secretary = ''
        self.accrued_to = ceiling_date(accrued_to or self.bobobase_modification_time())
        self.Reports = BLReportFolder('Reports', 'Reports')
        self.periods = BLLedgerPeriodsFolder()

    def normalizedDate(self, effective):
        """
        return a date that's timezone-normalised
        """
        return DateTime('%s %s' % (effective.strftime('%Y/%m/%d'), self.timezone))

    def manage_editProperties(self, REQUEST):
        """ correctly handle redirect """
        PropertyManager.manage_editProperties(self, REQUEST)
        REQUEST.set('manage_tabs_message', 'Updated')
        REQUEST.set('management_view', 'Properties')
        return self.manage_propertiesForm(self, REQUEST)

    def manage_reports(self, REQUEST, RESPONSE):
        """
        goto reports folder
        """
        RESPONSE.redirect('Reports/manage_workspace')

    def manage_periods(self, REQUEST, RESPONSE):
        """
        goto periods folders
        """
        RESPONSE.redirect('periods/manage_workspace')

    def saveSearch(self, request):
        """
        Our canned txn query
        """
        request.set('entered_by', request.get('entered_by', ''))
        request.set('status', request.get('status', ''))
        request.set('effective_start', request.get('effective_start', DateTime() - 1))
        request.set('effective_end', request.get('effective_end', DateTime()))
        request.set('batchsize', request.get('batchsize', 20))
        request.set('sort_on', 'effective')
        request.set('sort_order', 'descending')
        request.SESSION['txns'] = request.form


    def _applyTransactions(self, ids, funcname):
        for txn in filter(lambda x: x.getId() in ids, self.transactionValues()):
            getattr(txn, funcname)()

    def manage_post(self, ids, REQUEST=None):
        """
        """
        self._applyTransactions(ids, 'manage_post')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_repostAll(self, REQUEST=None):
        """
        repost all transactions
        """
        count = 0
        for sub in filter(lambda x: isinstance(x, BLSubsidiaryLedger), self.objectValues()):
            sub._reset_controls()
        for txn in self.transactionValues(status=('posted',)):
            txn.manage_repost()
            count += 1
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reposted %i transactions' % count)
            return self.manage_main(self, REQUEST)

    def manage_repost(self, ids, REQUEST=None):
        """
        """
        self._applyTransactions(ids, 'manage_repost')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_reverse(self, ids, REQUEST=None):
        """
        """
        self._applyTransactions(ids, 'manage_reverse')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_recalculateControls(self, effective=None, force=False, REQUEST=None):
        """
        recompute control account balances
        """
        for sub in filter(lambda x: isinstance(x, BLSubsidiaryLedger), self.objectValues()):
            sub.manage_recalculateControls(effective, force)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Recalculated control accounts')
            return self.manage_main(self, REQUEST)

    def manage_replaceLedger(self, REQUEST=None):
        """
        If you set up a ledger via a different portal_bastionledger, you may want to
        recreate your Ledger with new currency and accounts - this function does that
        """
        txns = 0
        for ledger in self.ledgerValues():
            txns += len(ledger.transactionIds())

        if txns != 0:
            msg = 'There are %i transactions in your BastionLedger, you cannot replace it' % txns
            if REQUEST:
                REQUEST.set('manage_tabs_message', msg)
                return self.manage_main(self, REQUEST)
            raise ValueError, msg

        self._delObject('Ledger')

        #
        # copy stuff from our (new) global locale repository ...
        #
        locale = getToolByName(self, 'portal_bastionledger')

        ledger = locale.Ledger._getCopy(self)
        ledger._setId('Ledger')
        self._setObject('Ledger', ledger)
        ledger = self._getOb('Ledger')
        ledger._postCopy(self)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Replaced Ledger')
            return self.manage_main(self, REQUEST)

    def edit(self, title, description, company_number, incorporation_date,
             address, directors,secretary,tax_number, industry_code, currency, timezone):
        """ plone property edit """
        self.title = title
        self.description = description
        self.company_number = company_number
        self.incorporation_date = incorporation_date
        self.address = address
        self.directors = directors
        self.secretary = secretary
        self.tax_number = tax_number
        self.industry_code = industry_code
        self.currency = currency
        self.timezone = timezone
        

    def manage_edit(self, title, currencies=[], REQUEST=None):
        """ """
        self.title = title
        self.currencies = currencies
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

    def ledgerUniqueId(self):
        return self.unique_identifier

    def ledgerLocalizedTime(self, dt, long_format=None):
        """
        return a timezone-corrected date
        """
        if not isinstance(dt, DateTime):
            dt = DateTime(dt)
        return self.toLocalizedTime(dt.toZone(self.timezone), long_format)

    def _memberInfo(self, memberids):
        """
        """
        infos = []
        mt = getToolByName(self, 'portal_membership')
        for director in memberids:
            if director.find(' ') == -1:
                member = mt.getMemberById(director)
                if member:
                    infos.append({'id': director,
                                  'member': member})
                    continue
            infos.append({'id': director,
                          'member': None})
        return infos

    def directorInfo(self):
        """
        return a tuple of hashes of id, member with member info of any director id
        """
        return self._memberInfo(self.directors)

    def secretaryInfo(self):
        """
        """
        if self.secretary:
            return self._memberInfo([self.secretary])
        return []

    def getLedgerProperty(self, prop, default=''):
        """
        allow sub-objects to acquire our properties
        """
        return self.getProperty(prop, default)

    def bastionLedger(self):
        """
        return the BastionLedger toplevel instance
        """
        return self

    def zeroAmount(self):
        return ZCurrency('%s 0.00' % self.currency)

    def ledgerValues(self):
        """
        return a list of things that are ledgers ...
        """
        return filter(lambda x: isinstance(x, LedgerBase), self.objectValues())

    def inventoryValues(self):
        """
        return a list of inventories
        """
        return self.objectValues('BLInventory')

    def ledgerIds(self):
        """
        return id's of all ledgers
        """
        return map(lambda x: x.getId(), self.ledgerValues())

    def accountValues(self, **kw):
        """
        return all the accounts - if you pass kw, it does a catalog search
        """
        results = []
        for ledger in self.ledgerValues():
            results.extend(ledger.accountValues(**kw))

        if kw:
            sort_on = kw.get('sort_on', '')
            if sort_on:
                results.sort(lambda x,y,sort_on=sort_on: attrCompare(x,y,sort_on))

        return results
                        

    def transactionValues(self, REQUEST={}, **kw):
        """
        return transactions across all ledgers
        """
        query = {'meta_type': ('BLTransaction', 'BLSubsidiaryTransaction')}
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

        sort_on = REQUEST.get('sort_on', kw.get('sort_on', 'effective'))
        sort_order = REQUEST.get('sort_order', kw.get('sort_order', 'descending'))

        return map(lambda x: x._unrestrictedGetObject(), self.searchResults(**query))

    def transactionValuesAdv(self, query, sortSpecs=(), withSortValues=None):
        """
        return all the accounts meeting the AdvancedQuery criteria
        """
        # TODO - withSortValues ...
        return map(lambda x: x._unrestrictedGetObject(),
                   self.bastionLedger().evalAdvancedQuery(query & In('meta_type', ('BLTransaction', 'BLSubsidiaryTransaction')), sortSpecs))


    def blTransactionStatuses(self):
        """
        """
        statuses = getToolByName(self, 'portal_workflow')._getOb('bltransaction_workflow').states.objectIds()
        statuses.sort()
        return statuses
                    
    def numberTransactions(self):
        """
        the number of transactions in all ledgers
        """
        return reduce(operator.add, map(lambda x: x.numberTransactions(), self.ledgerValues()))

    def entryValues(self, REQUEST=None, **kw):
        """
        return all the entries - if you pass kw, it does a catalog search,
        sort order is as per txn sorting
        """
        results = []
        for txn in self.transactionValues(REQUEST, **kw):
            results.extend(txn.entryValues())
        return tuple(results)

    def defaultCurrency(self):
        """
        """
        return self.currency

    def all_meta_types(self):
        """
        decide what's addable via our IBLLedgerTool/Multiple interfaces
        """
        instances = filter(lambda x: x.get('instance', None), Products.meta_types)

        multiples = filter(lambda x: IBLLedgerToolMultiple.implementedBy(x['instance']), instances)
        singletons = filter(lambda x: IBLLedgerTool.implementedBy(x['instance']), instances)

        if type(singletons) != types.TupleType:
            singletons = tuple(singletons)

        existing = map(lambda y: y.meta_type, self.objectValues())

        return filter( lambda x: x['name'] not in existing, singletons ) + multiples

    def expertMode(self):
        """
        returns whether or not all of the integrity constraints can be
        ignored because we're trying to perform some kind of remediation
        """
        try:
            return self.blledger_expert_mode()
        except:
            return False

    def TimeZones(self):
        """
        A list of available timezones for this ledger's effective
        dating mechanisms
        """
        return Timezones()

    def Currencies(self):
        """
        A list of available currencies for this ledger
        """
        return CURRENCIES
    
    def requiresEOD(self, effective=None):
        """
        return whether or not an end-of-day should be performed against this ledger
        """
        effective = effective or DateTime()
        return (effective - self.accrued_to) >= 1.0
 
    def moveTransaction(self, tid, ledgerid, accno, entryid, REQUEST=None):
        """
        move a transaction from the GL to a subsidiary ledger account
        """
        # TODO - make it move subsidiary txn's as well ...
        # TODO - some enforcement
        txn = self.Ledger._getOb(tid)
        ledger = self._getOb(ledgerid)
        account = ledger._getOb(accno)

        new_txn = ledger.createTransaction(txn.effective(), title=txn.title)
        for entry in txn.entryValues():
            if entry.getId() == entryid:
                new_txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(accno, entry.amount, entry.title)
            else:
                l,acc = entry.account.split('/')
                new_txn.manage_addProduct['BastionLedger'].manage_addBLEntry(acc, entry.amount, entry.title)

        if len(new_txn.objectValues('BLSubsidiaryEntry')) != 1:
            raise PostingError, new_txn

        # this should be postable...
        new_txn.manage_post()

        # remove/reverse old txn
        self.Ledger.manage_delObjects([tid])

        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/manage_main' % new_txn.absolute_url())

    def manage_fixupCatalogs(self, schema=False, reindex=True, REQUEST=None):
        """
        reload/repair catalogs
        """
        if schema:
            rebuildLedgerCatalogs(self, reindex)
        else:
            recatalogLedger(self)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Recataloged Ledger')
            return self.manage_main(self, REQUEST)

    def manage_reset(self, REQUEST=None):
        """
        clear down the entire ledger - useful after setting up your ledger and running a
        few test transactions proving it
        """
        # note that _reset is supposed to be able to run independently of _repair() so that
        # everything can be cleared down and thus easier to reconfigure without txn/currency
        # constraints ...

        # TODO - setting this is OLD-CATALOG ...
        zero = self.zeroAmount()
        for ledger in self.ledgerValues():
            for account in self.accountValues():
                account.manage_setBalance(zero, EPOCH)
            if ledger.getId() != 'Ledger':
                ledger._reset()

        # then reset the ledger
        self.Ledger._reset()

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reset Ledger!')
            return self.manage_main(self, REQUEST)

    def verifyExceptions(self, precision=0.05, bothways=True):
        """
        return a list of exceptions discovered (ie a tuple of exception name, entry, note)
        """
        bad_entries = []
        # first go check that all transactions posted properly
        for ledger in self.ledgerValues():
            for txn in ledger.transactionValues():
                bad_entries.extend(txn.manage_verify(precision))

        if bothways:
            # then go check that there are no other entries in any of the accounts that
            # weren't in one of the above transactions ...
            
            for ledger in self.ledgerValues():
                for account in ledger.accountValues():
                    bad_entries.extend(account.manage_verify(precision))

        if bad_entries:
            # exception class, entry, note/description
            return map(lambda x: (x[0].__class__.__name__, x[0].args[0], x[1]), bad_entries)

        
    def manage_verifyRepost(self, ids, force=False, REQUEST=None):
        """
        ids are txn paths, instantiate and repost them
        """
        count = 0
        for path in ids:
            txn = self.unrestrictedTraverse(path)
            txn.manage_repost(force=force)
            count += 1

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reposted %i transactions' % count)
            return self.manage_verify(self, REQUEST)

    def manage_inspect(self, REQUEST):
        """
        we've changed lots of underlying attributes - we can peak under the hood
        with this method
        """
        # we should really extend and format this very nicely - we could use this as
        # a user-based help tool ...
        keys = self.__dict__.keys()
        keys.sort
        output = []
        for k in keys:
            try:
                output.append('<tr><td>%s</td><td>%s</td></tr>' % (k, self.__dict__[k]))
            except Exception, e:
                output.append('<tr><td>%s</td><td>%s</td></tr>' % (k, str(e)))

        REQUEST.RESPONSE.write('<table>%s</table>' % ''.join(output))

    #
    # range of useful reporting functions ...
    #
    def grossProfit(self, effective=None, REQUEST=None):
        """
        report R - E for period indicated
        """
        gl = self.Ledger
        return -gl.sum(query=In('type',('Income', 'Expense')) & ~In('accno', gl.accnosForTag('tax_exp')),
                       effective=effective or DateTime().toZone(self.timezone))

    def lossesAttributable(self, effective=None, gross_profit=None, REQUEST=None):
        """
        capital and operating losses from previous periods able to be offset
        against income - note this prove jurisdiction-dependent with varying
        expiries on such.

        we also don't return more than can be applied against gross profit ...
        """
        effective = effective or DateTime().toZone(self.timezone)
        
        try:
            losses_forward = self.periods.periodForLedger('Ledger', effective).losses_forward
        except:
            losses_forward = 0

        if losses_forward > 0:
            # yep - we have losses ...
            if not gross_profit:
                gross_profit = self.grossProfit(effective)
            if gross_profit > 0:
                # this period *is* in profit so we can attribute a loss
                return min(losses_forward, abs(gross_profit))
        return self.zeroAmount()
                         

    def corporationTax(self, effective=[], gross_profit=None, attributable_losses=None, REQUEST=None):
        """
        calculate the corporation tax payable over the period
        """
        if not gross_profit:
            gross_profit = self.grossProfit(effective)
        if not attributable_losses:
            attributable_losses = self.lossesAttributable(effective)

        if isinstance(effective, DateTime):
            effective = [effective]
        elif not effective:
            effective = [DateTime().toZone(self.timezone)]

        if gross_profit > 0:
            btool = getToolByName(self, 'portal_bastionledger')
            company_tax = getattr(btool, 'company_tax', None)
            if company_tax:
                return company_tax.calculateTax(max(effective), gross_profit - attributable_losses)
        # eek a loss ...
        return self.zeroAmount()
    
    def netProfit(self, effective, gross_profit=None,
                  attributable_losses=None, corporation_tax=None, REQUEST=None):
        """
        calculate the net profit for the period
        """
        if not gross_profit:
            gross_profit = self.grossProfit(effective)
        if not attributable_losses:
            attributable_losses = self.lossesAttributable(effective)
        if not corporation_tax:
            corporation_tax = self.corporationTax(effective,
                                                  gross_profit,
                                                  attributable_losses)
        return gross_profit - attributable_losses - corporation_tax

    def profitLossAcc(self):
        """
        return the ledger account for current earnings
        """
        try:
            return self.Ledger.accountValues(tags='profit_loss')[0]
        except:
            raise MissingAssociation, 'profit_loss'
        
    def accruedIncomeTaxAcc(self):
        """
        return the ledger account to which we accrue corporation tax
        """
        try:
            return self.Ledger.accountValues(tags='tax_accr')[0]
        except:
            raise MissingAssociation, 'tax_accr'


    def asCSV(self, datefmt='%Y/%m/%d', txns=True, REQUEST=None):
        """
        return comma-separated variables of the entries

        you can select alternative date and currency formats, and the txns flag
        selects between choosing the entries from the BLTransactions or the BLAccounts
        of the ledgers
        """
        return '\n'.join(map(lambda x: x.asCSV(datefmt, txns), self.ledgerValues()))

    def manage_downloadCSV(self, REQUEST, RESPONSE, datefmt='%Y/%m/%d', txns=True):
        """
        a comma-separated list of *all* transaction entries, suitable for loading into Excel etc
        """
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition',
                           'inline; filename=%s.csv' % self.getId().lower())
        RESPONSE.write(self.asCSV(datefmt, txns))

    def manage_resetPeriods(self, REQUEST=None):
        """
        """
        pt = getattr(getToolByName(self, 'portal_bastionledger'), 'periodend_tool')
        pt.manage_reset(self)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reset periods')
            return self.manage_main(self, REQUEST)
        
    def manage_periodUndo(self, effective, REQUEST=None):
        """
        undo the period-end
        """
        pt = getattr(getToolByName(self, 'portal_bastionledger'), 'periodend_tool')
        pt.manage_undo(self, self.normalizedDate(effective))
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Undone period end for %s' % effective)
            return self.manage_main(self, REQUEST)

    def manage_dailyEnd(self, effective=None, now=None, REQUEST=None):
        """
        perform daily ledger rollover function
        """
        pt = getattr(getToolByName(self, 'portal_bastionledger'), 'periodend_tool')
        days = pt.manage_dailyEnd(self, effective, now or DateTime())
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Rolled over %i days' % days)
            return self.manage_main(self, REQUEST)
        return days


    def manage_periodEnd(self, effective, force=False, REQUEST=None):
        """
        hmmm - this needs a complex REQUEST in order to pass arguments to ledger
        period-ends ....
        """
        pt = getattr(getToolByName(self, 'portal_bastionledger'), 'periodend_tool')
        pt.manage_periodEnd(self, effective, force=force)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Done period end for %s' % effective)
            return self.manage_main(self, REQUEST)

    def manage_periodEndReports(self, effective, REQUEST=None):
        """
        generate/regenerate reports for a period
        """
        if not isinstance(effective, DateTime):
            effective = DateTime(effective)

        pinfos = self.periods.infosForDate(effective)
        if pinfos:
            pt = getattr(getToolByName(self, 'portal_bastionledger'), 'periodend_tool')
            pt.manage_regenerateReports(self, pinfos.getId(), effective)
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Done period end reports for %s' % effective)
        else:
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No period-end run for %s' % effective)
            else:
                raise ValueError, 'No period-end run for: %s' % effective
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_refreshCatalog(self, clear=1, REQUEST=None):
        """
        go and reindex *everything*
        """
        start = time.time()

        for ledger in self.ledgerValues():
            ledger.refreshCatalog(clear=clear)

        for inventory in self.objectValues('BLInventory'):
            inventory.catalog.refreshCatalog(clear=clear)
            inventory.dispatcher.refreshCatalog(clear=clear)

        for quotemgr in self.objectValues('BLQuoteManager'):
            quotemgr.refreshCatalog(clear=clear)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'refreshed catalogs in %0.2f seconds' % (time.time()-start))
            return self.manage_main(self, REQUEST)

    def manage_resetProperties(self, REQUEST=None):
        """
        """
        if getattr(aq_base(self),'_properties', None):
            try:
                delattr(self, '_properties')
            except:
                pass
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_navigationIndex(self, REQUEST=None):
        """
        ensure all these first-level objects are available to the navigation portlet
        """
        cat = getToolByName(self, 'portal_catalog', None)
        count = 0
        if cat:
            # remove *all* old paths
            for brain in cat.searchResults(path='/'.join(self.getPhysicalPath())):
                cat.uncatalog_object(brain.getURL(1))
            url = '/'.join(self.getPhysicalPath())
            cat.catalog_object(self, url)
            count += 1
            for ob in self.objectValues():
                url = '/'.join(ob.getPhysicalPath())
                cat.catalog_object(ob, url)
                count += 1
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Cataloged %i items' % count)
            return self.manage_main(self, REQUEST)

    def parseXML(self, file):
        """
        """
        if type(file) == types.StringType:
            body = file
        else:
            body = file.read()

        ledger = {}
        tree = etree.fromstring(body, parser)
        
        for attr in ('title', 'company_number', 'address', 'secretary', 'tax_number', 
                     'industry_code', 'currency', 'timezone'):
            ledger[attr] = tree.xpath(attr)[0].text

        ledger['incorporation_date'] = DateTime(tree.xpath('incorporated')[0].text)
        ledger['directors'] = map(lambda x: x.text, tree.xpath('directors'))

        return ledger


    def emailAddress(self):
        """
        return email address
        """
        # TODO 
        return ""
        
    def manage_emailStatement(self, email, sender, template, effective=None, REQUEST=None):
        """
        email a Revenue Statement, Balance Sheet, or Cashflow Statement to a recipient
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise ValueError, 'no MailHost found'
        
        # ensure 7-bit
        mail_text = str(getattr(self, template)(self, self.REQUEST, sender=sender, 
                                                email=email, effective=effective or DateTime()))

        mailhost._send(sender, email, mail_text)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Statement emailed to %s' % email)
            return self.manage_main(self, REQUEST)
        
    def html2pdf(self, html, encode=True):
        """
        return a pdf-representation of the html document
        if encode is set, returns base64 representation
        """
        out = StringIO()
        pdfcontext = pisaDocument(StringIO(html), out)
        if encode:
            return base64.encodestring(out.getvalue())
        return out.getvalue()

    def manage_recalculateBalances(self, effective=None, REQUEST=None):
        """
        regenerate all internal account running total counters
        """
        start = time.time()
        now = DateTime()
        effective = effective or now

        if effective > now:
            raise LedgerError, 'cannot future-date balances'

        currency = self.defaultCurrency()
        for ledger in self.ledgerValues():
            for account in ledger.accountValues():
                amount = account.openingBalance(effective, currency) + \
                    account.total((account.openingDate(effective), effective), currency)
                account.manage_setBalance(amount, min(account.lastTransactionDate(), effective))

        self.accrued_to = ceiling_date(effective)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Recalculated in %0.2f seconds' % (time.time()-start))
            return self.manage_main(self, REQUEST)

    def manage_removeAccountEntries(self, REQUEST=None):
        """
        big repair job for 4.4.x
        """
        start = time.time()
        count = 0
        for ledger in self.ledgerValues():
            removeAllIndexes(ledger)
            for account in ledger.accountValues():
                for id in list(account.objectIds(('BLEntry', 'BLSubsidiaryEntry'))):
                    account._delObject(id, suppress_events=True)
                    count += 1
            self.refreshCatalog()
            for txn in ledger.transactionValues():
                for entry in txn.entryValues():
                    if getattr(aq_base(entry), 'ledger', None):
                        delattr(entry, 'ledger')
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Removed %i entries in %0.2f seconds' % (count, time.time()-start))
            return self.manage_main(self, REQUEST)
        
    def _repair(self):
        self.manage_fixupCatalogs(schema=True, reindex=True)
        self.manage_removeAccountEntries()
        self.manage_recalculateBalances()

AccessControl.class_init.InitializeClass(Ledger)


def addLedger(ob, event):
    LOG.info('doing addLedger')

    makeLedgerCatalog(ob)
    #
    # if we're called from copy support/import, our catalog paths are probably borked ...
    #
    if getattr(aq_base(ob), 'Ledger', None):
        ob.manage_fixupCatalogs()
        ob.manage_navigationIndex()
        return

    #
    # copy stuff from our global locale repository ...
    #
    locale = getToolByName(ob, 'portal_bastionledger')

    # hand-craft manage_clone because we don't all_meta_types BLLedger ...
    if not getattr(aq_base(ob), 'Ledger', None):
        try:
            ledger = locale.Ledger._getCopy(ob)
        except CopyError:
            # there is no _p_jar - this is still just a faux object in portal_factory
            return
        ledger._setId('Ledger')
        ob._setObject('Ledger', ledger)
    ledger = ob._getOb('Ledger')
    ledger._postCopy(ob)

    # ensure indexes - otherwise accnoForTag with be borked ...
    #for account in ledger.accountValues():
    #    account.indexObject()

    associations = locale.associations

    manage_addBLInventory(ob, 'Inventory', 'Stock')

    try:
        manage_addBLOrderBook(ob, 'Receivables', 
                              associations.receivables.blAccount(ob),
                              'Inventory', prefix='R', title= 'Customer Ledger')
    except IndexError:
        raise MissingAssociation, 'receivables'
            
    try:
        manage_addBLOrderBook(ob, 'Payables',
                              associations.payables.blAccount(ob),
                              'Inventory', prefix='P', title='Supplier Ledger')
    except IndexError:
        raise MissingAssociation, 'payables'
    
    try:
       manage_addBLShareholderLedger(ob, 'Shareholders', 
                                     (associations.shareholders.blAccount(ob),
                                      associations.dividend_payable.blAccount(ob)),
                                     title='Shareholders Ledger/Register')
    except IndexError:
        raise MissingAssociation, 'shareholders'

    if DO_PAYROLL:
        try:
            wages_and_salaries = associations.wages.blAccount(ob)
            manage_addBLPayroll(ob, 'Payroll',
                                associations.wages.blAccount(ob),
                                'Friday', title='Employee Payroll')
        except IndexError:
            raise MissingAssociation, 'wages'

    # make sure Plone knows about these items ...
    ob.manage_navigationIndex()

    LOG.info('done addLedger')

from OFS.ObjectManager import BeforeDeleteException

def delLedger(ob, event):
    """
    hmmm - all our integrity constraints cause delete events to barf
    for non- expertMode users, so we commit suicide first to allow
    ourselves to be deleted normally
    """
    # hmmm - some old ledgers barf ...
    #try:
    #    ob.manage_reset()
    #except:
    #    pass
        
    # clean up any Plone stuff ...
    cat = getToolByName(ob, 'portal_catalog', None)
    if cat:
        for brain in cat.searchResults(path='/'.join(ob.getPhysicalPath())):
            cat.uncatalog_object(brain.getURL(1))
