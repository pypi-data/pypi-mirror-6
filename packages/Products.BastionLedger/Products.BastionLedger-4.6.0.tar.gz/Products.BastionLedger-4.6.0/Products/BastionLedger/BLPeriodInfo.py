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
import AccessControl, types
from DateTime import DateTime
from Acquisition import Implicit, aq_base
from AccessControl.Permissions import access_contents_information, view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.AdvancedQuery import Between, In, Le
from Products.BastionBanking.ZCurrency import ZCurrency
from BLBase import LargePortalFolder as Folder
from BLBase import PortalContent as SimpleItem
from BLGlobals import EPOCH, ACC_TYPES
from Exceptions import InvalidPeriodError, UnbalancedError
from Permissions import ManageBastionLedgers
from utils import floor_date, ceiling_date

from zope.interface import implements
from interfaces.periodend import IPeriodEndInfo, IPeriodEndInfos

class BLPeriodRec(SimpleItem):
    """
    Stores balances for period-ends, and separately, reporting amounts.  These balances
    are used elsewhere to quickly compute account totals.  The reporting amounts are
    independent of this, and used to collate prior-period reports.
    """
    meta_type = 'BLPeriodRec'
    icon = 'misc_/BastionLedger/blaccount'
    Types = ACC_TYPES

    __ac_permissions__ = SimpleItem.__ac_permissions__ + (
        (access_contents_information, ('effective', 'tweaked', 'blAccount')),
         )

    _properties = (
        {'id':'accno',             'type':'string',      'mode':'w'},
        {'id':'title',             'type':'string',      'mode':'w'},
        {'id':'type',              'type':'selection',   'mode':'w', 'select_variable':'Types'},
        {'id':'balance',           'type':'currency',    'mode':'w'},
        {'id':'reporting_balance', 'type':'currency',    'mode':'w'},
        )

    def __init__(self, id, title, accno, typ, balance):
        self.id = id
        self.accno = accno
        self.title = title
        self.type = typ
        self.balance = balance            # cached for opening balance enquiries
        self.reporting_balance = balance  # used in financial reports - might be tweaked ...

    def effective(self):
        """ the effective date of the *cached* entry """
        return self.aq_parent.period_ended

    def tweaked(self):
        """ whether or not the reporting balance differs from the actual account balance """
        if self.type in ('Income', 'Expense'):
            return self.balance != 0
        return self.balance != self.reporting_balance

    def blAccount(self):
        """
        the underlying BLAccount
        """
        return self.aq_parent.blAccount(self.getId())

    def __cmp__(self, other):
        if not isinstance(other, BLPeriodRec):
            return -1
        if self.accno < other.accno:
            return -1
        elif self.accno > other.accno:
            return 1
        return 0

AccessControl.class_init.InitializeClass(BLPeriodRec)
    

class BLPeriodInfo(Folder):
    """
    statistics info for ledger for a reporting period
    """
    meta_type = portal_type = 'BLPeriodInfo'
    icon = 'misc_/BastionLedger/blledger'

    implements(IPeriodEndInfo)

    manage_main = PageTemplateFile('zpt/period_chart', globals())
    manage_transactions = PageTemplateFile('zpt/period_txns', globals())

    manage_options = (
        {'label':'Accounts',     'action':'manage_main'},
        {'label':'Transactions', 'action':'manage_transactions'},
        {'label':'View',         'action':''},
        {'label':'Reload',       'action':'manage_updateChart'},
        {'label':'Properties',   'action':'manage_propertiesForm'},
        ) + Folder.manage_options[1:]

    __ac_permissions__ = Folder.__ac_permissions__ + (
        (view_management_screens, ('manage_transactions',)),
        (ManageBastionLedgers, ('postTransactions', 'reverseTransactions',
                                'manage_updateChart')),
        (access_contents_information, ('blLedger', 'blLedgerTransactions', 'blAccount', 'balance', 
                                       'getAccountInfos', 'prevPeriodInfo', 'sum', 'reportedBalance',
                                       'nextPeriodInfo', 'beginning', 'ended',
                                       'numberAccounts', 'numberTransactions')),
        )
    
    _properties = (
        {'id':'total',            'type':'currency', 'mode':'w'},
        {'id':'transactions',     'type':'lines',    'mode':'w'},
       )

    def __init__(self, id, total, tids=()):
        Folder.__init__(self, id)
        self.total = total
        self.transactions = tids

    def Title(self):
        return "%s - %s" % (self.aq_parent.getId(), self.getId())

    def _getObCreate(self, id):
        """
        get the info rec, or create it from the underlying ledger
        """
        rec = self._getOb(id, None)
        if rec is None:
            account = self.blLedger()._getOb(id)
            # TODO - balance is probably zero ...
            self._setObject(id, BLPeriodRec(id, 
                                            account.title, 
                                            account.accno, 
                                            account.type, 
                                            account.balance(effective=self.ended())))
            rec = self._getOb(id)
        return rec
                          
    def numberAccounts(self):
        """
        the number of (active) accounts in this period
        """
        ledger = self.blLedger()
        return len(ledger.accountValuesAdv(Le('created', self.ended())))

    def numberTransactions(self):
        """
        the number of transactions in this period
        """
        return len(self.blLedgerTransactions(sort=()))

    def beginning(self):
        """
        the beginning date
        """
        return self.aq_parent.period_began

    def ended(self):
        """
        the ending date
        """
        return self.aq_parent.period_ended

    def sum(self, attr, type=[]):
        """
        return the addition of the attr from the underlying objects
        """
        total = ZCurrency('%s 0.00' % self.currency())
        for rec in self.objectValues():
            if type and rec.type in type:
                total += rec.getProperty(attr)
        return total

    def om_icons(self):
        """
        """
        icons = ()

        # by definition, subsidiary ledgers only balance against their control
        # in the ledger ...
        if self.getId() == 'Ledger' and \
                (self.sum('balance') != 0 or self.sum('reporting_balance') != 0):
            icons = icons + ({'path': 'misc_/SiteErrorLog/error.gif',
                              'alt': 'broken', 
                              'title': 'Broken'},)
        icons = icons + ({'path': 'misc_/BastionLedger/blledger',
                          'alt': self.meta_type, 
                          'title': self.meta_type},)
        
        return icons

    def blLedger(self):
        """
        returns the underlying ledger (or None if it's no longer present)
        """
        try:
            return self.bastionLedger()._getOb(self.getId())
        except:
            pass
        return None

    def blLedgerTransactions(self, sort=(('effective', 'desc'),)):
        """
        the individual transactions incorporated within this period
        """
        ledger = self.blLedger()
        if ledger:
            return ledger.transactionValuesAdv(Between('effective', self.beginning(), self.ended()), 
                                               sort)
        return []

    def _balance(self, accountid, attr):
        """
        return our cached balance for the account
        """
        try:
            return self._getOb(accountid).getProperty(attr)
        except:
            pass
        return self.zeroAmount()

    def balance(self, accountid):
        return self._balance(accountid, 'balance')

    def reportedBalance(self, accountid):
        return self._balance(accountid, 'reporting_balance')

    def blAccount(self, accountid):
        """
        return the ledger account (if found)
        """
        try:
            return self.blLedger()._getOb(accountid)
        except:
            pass
        return None

    def manage_updateReportingBalances(self, balances, force=False, REQUEST=None):
        """ 
        balances is a list of id,amount records of accountid/new balance's ...
        """
        total = ZCurrency('%s 0.00' % self.currency())
        for rec in balances:
            total += rec['amount']
            self._getOb(rec['id'])._updateProperty('reporting_balance', rec['amount'])

        if not force and total != 0:
            raise UnbalancedError, total

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Updated reporting balances')
            return self.manage_main(self, REQUEST)

    def getAccountInfos(self):
        """
        collate and return account information
        """
        infos = []
        my_url = self.absolute_url()
        prev_info = self.prevPeriodInfo()

        # return them in accno order
        recs = list(self.objectValues())
        recs.sort(BLPeriodRec.__cmp__)

        for rec in recs:

            if prev_info:
                opening = prev_info.balance(rec.getId())
            else:
                opening = self.zeroAmount()

            try:
                account = self.blAccount(rec.getId())
                infos.append({'id':rec.getId(),
                              'absolute_url':account.absolute_url(),
                              'real_url':'%s/%s' % (my_url, rec.getId()),
                              'icon':account.getIcon(1),
                              'accno':rec.accno,
                              'type': rec.type,
                              'title':rec.title,
                              'opening': opening,
                              'change': opening - rec.balance,
                              'balance':rec.balance,
                              'reporting_balance':rec.reporting_balance,
                              'tweaked':rec.tweaked()})
            except:
                infos.append({'id':rec.getId(),
                              'absolute_url':my_url,
                              'real_url':'%s/%s' % (my_url, rec.getId()),
                              'icon': 'broken.gif',
                              'type':rec.type,
                              'accno': rec.accno,
                              'title': rec.title,
                              'opening': opening,
                              'change': opening - rec.balance,
                              'balance':rec.balance,
                              'reporting_balance':rec.reporting_balance,
                              'tweaked':rec.tweaked()})

        return infos

    def blTransactions(self):
        """
        return all the transactions associated with (ie generated by) this period end
        """
        return self.blLedger().transactionValuesAdv(In('id', self.transactions), 
                                                    (('effective','asc'),))

    def postTransactions(self, ids, reporting=False, REQUEST=None):
        """
        adjust cached balances by amounts in (closing) transactions
        """
        ledger = self.blLedger()
        for tid in ids:
            for entry in ledger._getOb(tid).entryValues():
                rec = self._getOb(entry.accountId())
                rec.balance += entry.amount
                if reporting:
                    rec.reporting_balance += entry.amount
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Posted %i transactions' % len(ids))
            return self.manage_main(self, REQUEST)

    def reverseTransactions(self, ids, reporting=False, REQUEST=None):
        """
        adjust cached balances by amounts in (closing) transactions
        """
        ledger = self.blLedger()
        for tid in ids:
            for entry in ledger._getOb(tid).entryValues():
                self._getOb(entry.accountId()).balance -= entry.amount
                if reporting:
                    self._getOb(entry.accountId()).reporting_balance -= entry.amount
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reversed %i transactions' % len(ids))
            return self.manage_main(self, REQUEST)

    def manage_updateChart(self, all=False, REQUEST=None):
        """
        get/fetch account information for any *new* accounts added post
        period-end run, or if *all*, go recompute
        """
        ledger = self.blLedger()
        currency = ledger.defaultCurrency()
        count = 0
        total = ledger.zeroAmount()

        if all:
            self.manage_delObjects(list(self.objectIds()))
            previnfo = self.prevPeriodInfo()
            for a in ledger.accountValues():
                if previnfo:
                    opening_bal = previnfo.balance(a.getId())
                else:
                    opening_bal = ledger.zeroAmount()
                amount = opening_bal + a.total(effective=(self.beginning(), self.ended()), currency=currency)
                self._setObject(a.getId(), BLPeriodRec(a.getId(), a.title, a.accno, a.type, amount))
                total += amount
                count += 1
        else:
            seen = {}

            for accid in self.objectIds():
                seen[accid] = True

            for a in filter(lambda x: not seen.has_key(x.getId()), ledger.accountValues()):
                amount = a.balance(effective=self.effective(), currency=currency)
                self._setObject(a.getId(), BLPeriodRec(a.getId(), a.title, a.accno, a.type, amount))
                total += amount
                count += 1

        self.total = total

        if REQUEST:
            if all:
                REQUEST.set('manage_tabs_message', 'Processed %i accounts' % count)
            else:
                REQUEST.set('manage_tabs_message', 'Added %i accounts' % count)
            return self.manage_main(self, REQUEST)

    def __cmp__(self, other):
        """
        return a sorted list of these
        """
        if not isinstance(other, BLPeriodInfo): return -1
        
        try:
            mine = self.ended()
            theirs = other.ended()
        except:
            # old-style periodinfo ...
            return -1

        if mine > theirs: return 1
        if mine < theirs: return -1
        return 0

    def prevPeriodInfo(self):
        """
        return the period info for the period prior to this
        """
        prev = self.prevPeriod()
        return prev and prev._getOb(self.getId()) or None

    def nextPeriodInfo(self):
        """
        return the period info for the period after this
        """
        next = self.nextPeriod()
        return next and next._getOb(self.getId()) or None

AccessControl.class_init.InitializeClass(BLPeriodInfo)


class BLPeriodInfos(Folder):
    """
    a container of PeriodInfo's for a ledger - the id is the same as the
    ledger it maps
    """
    meta_type = portal_type = 'BLPeriodInfos'
    icon = 'misc_/BastionLedger/period'

    implements(IPeriodEndInfos)

    _properties = (
       {'id':'period_began',      'type':'date',     'mode':'w'},
       {'id':'period_ended',      'type':'date',     'mode':'w'},
       {'id':'gross_profit',      'type':'currency', 'mode':'w'},
       {'id':'net_profit',        'type':'currency', 'mode':'w'},
       {'id':'company_tax',       'type':'currency', 'mode':'w'},
       {'id':'losses_recognised', 'type':'currency', 'mode':'w'},
       {'id':'losses_forward',    'type':'currency', 'mode':'w'},
       )

    __ac_permissions__ = Folder.__ac_permissions__ + (
        (ManageBastionLedgers, ('update', 'adjustProfit')),
        (view_management_screens, ('manage_transactions', 'manage_statistics')),
        (access_contents_information, ('blTransactions', 'blLedgerTransactions', 
                                       'transactionValues', 'entryValues', 'effective', 'duration',
                                       'currency', 'netProfit', 'companyTax', 'lossesRecognised',
                                       'lossesForward', 'prevPeriod', 'nextPeriod')),
        )

    manage_statistics = PageTemplateFile('zpt/period_stats', globals())
    manage_transactions = PageTemplateFile('zpt/period_txns', globals())

    manage_options = (
        Folder.manage_options[0],
        {'label':'View',         'action':''},
        {'label':'Statistics',   'action':'manage_statistics'},
        {'label':'Properties',   'action':'manage_propertiesForm'},
        {'label':'Transactions', 'action':'manage_transactions'},
        ) + Folder.manage_options[1:]

    def __init__(self, id, period_began, period_ended, zero):
        Folder.__init__(self, id)
        self.period_began = period_began
        self.period_ended = period_ended
        self.gross_profit = zero
        self.net_profit = zero
        self.company_tax = zero
        self.losses_recognised = zero
        self.losses_forward = zero

    def displayContentsTab(self): return False

    def duration(self):
        """ the number of days in the period """
        return self.period_began - self.period_ended

    def netProfit(self):
        """
        profit as derived from underlying closing amounts
        """
        profit = ZCurrency('%s 0.00' % self.currency())
        for rec in self.Ledger.objectValues():
            if rec.type in ('Income', 'Expense'):
                profit += rec.reporting_balance
        return profit

    def companyTax(self):
        """
        company tax, as per balance in tax account(s)
        """
        tax = ZCurrency('%s 0.00' % self.currency())
        # just look through expenses to reduce overhead ...
        for rec in self.Ledger.objectValues():
            if rec.type == 'Expense' and rec.blAccount().hasTag('tax_exp'):
                tax += rec.reporting_balance
        return tax

    def lossesRecognised(self):
        """
        the losses from prior periods applied to this period
        """
        loss = ZCurrency('%s 0.00' % self.currency())
        # just look through expenses to reduce overhead ...
        for rec in self.Ledger.objectValues():
            if rec.type == 'Proprietorship' and rec.blAccount().hasTag('loss_fwd'):
                loss += rec.reporting_balance
        return loss

    def lossesForward(self):
        """
        deferred tax attributable to future profits
        """
        tax = ZCurrency('%s 0.00' % self.currency())
        # just look through expenses to reduce overhead ...
        for rec in self.Ledger.objectValues():
            if rec.type == 'Asset' and rec.blAccount().hasTag('tax_defr'):
                tax += rec.reporting_balance
        return tax

    def currency(self):
        """
        return the base currency of the info record
        """
        return self.gross_profit.currency()

    def Title(self):
        """
        """
        yy,mm,dd = self.getId().split('-')
        # hmmm DateTime screws up timezones ...
        return '%s %s' % (dd, DateTime(self.getId()).strftime('%B %Y'))

    def blTransactions(self):
        """
        return list of closing transactions across all ledgers
        """
        txns = []
        for ledger in self.objectValues():
            txns.extend(ledger.blTransactions())

        return txns
        
    def blLedgerTransactions(self):
        """
        *all* the transactions incorporated within this period
        """
        txns = []
        for ledger in self.objectValues():
            txns.extend(ledger.blLedgerTransactions())
        txns.sort()
        return txns

    # transaction API ...
    def transactionValues(self, REQUEST={}, **kw):
        """
        the list of period-end generated transactions
        """
        # ignore filter
        return self.blTransactions()

    def entryValues(self, REQUEST={}, **kw):
        """
        show full journal entries for transactions
        """
        results = []
        for txn in self.blTransactions():
            results.extend(txn.entryValues())
        return results

    def effective(self):
        """
        the effective date for the period-end record, this is *most* important
        in determinining *which* transactions get placed in the periods
        """
        #return floor_date(DateTime('%s %s' % (self.getId(), self.timezone)))
        return self.period_ended

    def update(self):
        """
        adjust charts/reporting amounts based upon latest ledger
        """
        self.Ledger.manage_updateChart()

    def nextPeriod(self):
        """
        return the next period info
        """
        pids = self.aq_parent.objectIds()
        for i in xrange(0, len(pids)-1):
            if pids[i] == self.getId():
                return self.aq_parent._getOb(pids[i+1])
        return None
            
    def prevPeriod(self):
        """
        return the previous period info
        """
        pids = self.aq_parent.objectIds()
        for i in xrange(1, len(pids)):
            if pids[i] == self.getId():
                return self.aq_parent._getOb(pids[i-1])
        return None
            
    def adjustProfit(self, amount):
        """
        tweak profit by amount (leave tax alone because we may already have submitted a 
        return) apply to gross, net, losses etc as appropriate
        """
        self.gross_profit += amount
        # TODO - think about all this ...
        if self.net_profit != 0:
            self.net_profit += amount
        else:
            self.losses_recognised += amount
        # TODO - what if losses less than amount - need to flow into net profit ...
        if self.losses_forward != 0:
            self.losses_forward -= amount

    def _repair(self):
        self.period_began = self.Ledger.period_began
        self.period_ended = ceiling_date(self.Ledger.period_ended)
        self.gross_profit = self.Ledger.gross_profit
        self.net_profit = self.Ledger.net_profit
        self.company_tax = self.Ledger.company_tax
        self.losses_forward = self.Ledger.losses_forward
        self.losses_recognised = self.Ledger.blLedger().zeroAmount()

AccessControl.class_init.InitializeClass(BLPeriodInfos)


class BLLedgerPeriodsFolder(Folder):
    """
    a container of LedgerPeriod's for a set of ledger's
    """

    id = 'periods'
    meta_type = 'BLLedgerPeriodsFolder'

    __ac_permissions__ = Folder.__ac_permissions__ + (
        (view_management_screens, ('manage_balanceSheet', 
                                   'manage_revenueStatement', 
                                   'manage_trialBalance')),
        (access_contents_information, ('periodsForLedger', 'periodForLedger', 
                                       'periodForLedgerAmt', 'lastPeriodForLedger', 
                                       'infosForDate', 'lastClosingForLedger', 
                                       'balanceForAccount', 'periodEnds', 
                                       'nextPeriodEnd', 'nextPeriodStart',
                                       'ledgerInfos',)),
        (ManageBastionLedgers, ('addPeriodProfits', 'addPeriodLedger', 'adjustAccounts')),
        )

    manage_runend = PageTemplateFile('zpt/period_runend', globals())
    manage_balanceSheet = PageTemplateFile('zpt/balance_sheet_multi', globals())
    manage_revenueStatement = PageTemplateFile('zpt/revenue_statement_multi', globals())
    manage_trialBalance = PageTemplateFile('zpt/periods_trialbalance', globals())
    manage_ledgers = PageTemplateFile('zpt/periods_ledgers', globals())

    manage_options = (
        {'label':'Periods', 'action':'manage_main'},
        {'label':'Run',  'action':'manage_runend'},
        {'label':'Ledgers', 'action':'manage_ledgers'},
        {'label':'BSheet', 'action':'manage_balanceSheet'},
        {'label':'P & L',  'action':'manage_revenueStatement'},
        {'label':'Balances',  'action':'manage_trialBalance'},
        ) + Folder.manage_options[2:]

    def __init__(self):
        Folder.__init__(self, self.id)

    def infosForDate(self, effective):
        """
        return the period information for the effective date (or None)
        """
        for infos in self.objectValues('BLPeriodInfos'):
            if effective <= infos.effective():
                return infos

        return None

    def periodsForLedger(self, ledgerid):
        """
        returns the folder of BLPeriodInfo objects for the indicated ledger id
        """
        periods = []
        for info in self.objectValues('BLPeriodInfos'):
            try:
                periods.append(info._getOb(ledgerid))
            except KeyError:
                pass

        # we're invariably going to do date-based ranking ...
        periods.sort()
        return periods
    
    def lastPeriodForLedger(self, ledgerid):
        """
        returns the latest BLPeriodInfo for the indicated ledger id
        """
        try:
            return max(self.periodsForLedger(ledgerid))
        except:
            return None

    def lastClosingForLedger(self, ledgerid, effective=None):
        """
        returns the period end date for the latest BLPeriodInfo of the indicated
        ledger

        effective date is for (forced) reruns etc
        """
        if effective:
            periods = self.periodsForLedger(ledgerid)
            periods.reverse()
            eff_max = ceiling_date(effective)
            for period in periods:
                # if it's the end date ...
                if eff_max >= period.period_ended:
                    return period.period_ended
            return EPOCH

        try:
            return self.lastPeriodForLedger(ledgerid).period_ended
        except:
            pass

        return EPOCH

    def periodForLedger(self, ledgerid, effective):
        """
        return the period record for the ledger, immediately prior to effective
        """
        periods = self.periodsForLedger(ledgerid)
        periods.reverse()

        for period in periods:
            # if it's outside all periods, or within a specific period
            #if effective >= period.period_ended or effective >= period.period_began:
            if ceiling_date(effective) >= period.period_ended:
                return period
        return None

        
    def balanceForAccount(self, effective, ledgerid, accountid):
        """
        returns the closing balance for the indicated in the indicated ledger
        for the BLPeriodInfo in which the effective date falls

        if there is no period-end, it returns None
        """
        info = self.periodForLedger(ledgerid, effective)
        return info and info.balance(accountid) or None

    def addPeriodProfits(self, period_began, period_ended, gross, net, tax, losses, losses_fwd):
        """
        add/update period statistics
        """
        infosid = period_ended.strftime('%Y-%m-%d')
        infos = self._getOb(infosid)
        infos.manage_changeProperties(gross_profit=gross,
                                      net_profit=net,
                                      company_tax=tax,
                                      losses_recognised=losses,
                                      losses_forward=losses_fwd)

    def adjustAccounts(self, drledger, draccount, crledger, craccount, amount, effective):
        """
        roll adjustment(s) from old periods into newer periods
        """
        for pinfos in filter(lambda x: x.effective() > effective,
                             self.objectValues('BLPeriodInfos')):
            dr = pinfos._getOb(drledger)._getOb(draccount)
            dr.manage_changeProperties(balance=dr.balance + amount,
                                       reporting_balance=dr.reporting_balance + amount)
            cr = pinfos._getOb(crledger)._getOb(craccount)
            cr.manage_changeProperties(balance=cr.balance - amount,
                                       reporting_balance=cr.reporting_balance - amount)

    def addPeriodLedger(self, ledger, period_began, period_ended, force=False):
        """
        static period-end record for a ledger/subsidiary ledger
        """
        # hmmm - start/end is a bit dubious ...
        if period_began > period_ended:
            raise InvalidPeriodError, 'began greater than ended %s > %s!' % (period_began, period_ended)

        # hmmm - we've got shite tz issues around this ...
        infosid = period_ended.strftime('%Y-%m-%d')
        ledgerid = ledger.getId()

        last_infos = self.periodsForLedger(ledgerid)
        if last_infos:
            last = max(last_infos)
            if period_began < last.ended() and not force:
                raise InvalidPeriodError, 'date overlap!'

        zero = ledger.zeroAmount()

        if getattr(aq_base(self), infosid, None) is None:
            self._setObject(infosid, 
                            BLPeriodInfos(infosid, 
                                          period_began, 
                                          period_ended, 
                                          zero))

        infos = self._getOb(infosid)

        # remove the results of any previous run (auto-removing txns)...
        if getattr(aq_base(infos), ledgerid, None):
            infos.manage_delObjects([ledgerid])

        infos._setObject(ledgerid, BLPeriodInfo(ledgerid, zero))
        return infos._getOb(ledgerid)

    def infoForType(self, account_types, periodids, ledger='Ledger', attr='reporting_balance', exclude=[], all=False):
        """
        return a dict of stuff from Ledger periods for multi-period reporting
        exclude is a list of accno's
        if all is set, then we report on zero-balance stuff as well (but we *always* report zero-balance control accounts)
        """
        accno_id = {}
        id_balances = {}
        totals = []
        dates = []
        stats = []
        
        if type(account_types) in (types.ListType, types.TupleType):
            acctypes = account_types
        else:
            acctypes = [account_types]

        periodids.sort()
        periodids.reverse()
        periods = map(lambda x: x._getOb(ledger), map(lambda x: self._getOb(x), periodids))
        ndx = 0

        # parse and collate the Ledger info's
        for period in map(lambda x: getattr(x, ledger), periods):

            zero = total = period.zeroAmount()

            for rec in filter(lambda x: x.type in acctypes, period.objectValues()):

                if rec.accno in exclude:
                    continue

                key = rec.getId()
                
                if accno_id.has_key(rec.accno) and accno_id[rec.accno] != key:
                    raise AssertionError, 'You have an inconsistent accno (%s)!!' % rec.accno

                accno_id[rec.accno] = key

                if not id_balances.has_key(key):
                    balances = [zero for i in periods]
                    id_balances[key] = balances

                id_balances[key][ndx] = rec.getProperty(attr)
                
                total = rec.getProperty(attr) + total

            # look behind to get the losses
            try:
                losses = self.periodForLedger(ledger, period.beginning()-1).losses_forward
            except:
                losses = zero

            totals.append(total)
            dates.append(period.period_ended)
            stats.append({'gross_profit':period.gross_profit,
                          'net_profit':period.net_profit,
                          'company_tax':period.company_tax,
                          'losses_recognised':period.losses_recognised,
                          'losses_forward':period.losses_forward})
            ndx += 1

        results = []
        
        sort_order = accno_id.keys()
        sort_order.sort()

        # data mine the actual ledger
        theledger = self.aq_parent._getOb(ledger)

        for key in map(lambda x: accno_id[x], sort_order):
            # TODO - not found?
            account = theledger._getOb(key, None)
            # decide to report account?
            if all or account.isControl() or filter(lambda x: x != 0, id_balances[key]):
                rec = [account]
                rec.extend(id_balances[key])
                results.append(rec) 

        return {'accounts':results,      # ordered list
                'balances': id_balances, # keyed on accountids
                'totals':totals,         # list of summations
                'dates':dates,           # list of dates for which the above relates
                'stats':stats}           # gross, net, tax

    def periodEnds(self):
        """
        a list of end dates for which periods have been run
        """
        ends =  map(lambda x: x.period_ended, self.objectValues('BLPeriodInfos'))
        ends.sort()
        return ends

    def periodIds(self):
        """
        return a list of ids for the period records we have - in latest to earliest order
        """
        ids = list(self.objectIds('BLPeriodInfos'))
        ids.reverse()
        return ids

    def getAccountInfos(self, periodid=''):
        """
        get a complete set of infos across all journals for a period
        """
        if not periodid:
            infos = self.objectValues('BLPeriodInfos')[0]
        else:
            infos = self._getOb(periodid)

        results = []
        for ledger in infos.objectValues('BLPeriodInfo'):
            results.extend(ledger.getAccountInfos())

        return results

    def nextPeriodStart(self, effective=None):
        """
        return the beginning period date for the next period-end run
        """
        ends = self.periodEnds()
        return ends and floor_date(ends[-1] + 1) or EPOCH

    def nextPeriodEnd(self, effective=None):
        """
        return the date for the next period end
        """
        # first try and compute day from existing intra-period runs
        ends = self.periodEnds()
        if ends:
            last = ends[-1]
            return DateTime('%i/%s/%s 23:59:59 %s' % (last.year() + 1, 
                                                      last.month(), 
                                                      last.day(), 
                                                      last.timezone()))

        # grab it from the ledger tool
        lt = getToolByName(self, 'portal_bastionledger')
        return lt.yearEnd(effective or DateTime())
        

    def manage_reset(self, REQUEST=None):
        """
        hmmm - reset periods if it's in a funk
        """
        Folder.__init__(self, self.id)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reinitialized periods')
            return self.manage_main(self, REQUEST)

    def ledgerInfos(self, REQUEST=None):
        """
        a list of ledger period-ended information
        """
        results = {}
        for period in self.objectValues('BLPeriodInfos'):
            for ledger in period.objectValues('BLPeriodInfo'):
                id = ledger.getId()
                if results.has_key(id):
                    results[id]['periods'][period.getId()] = period
                else:
                    results[id] = {'ledger': id,
                                   'periods': { period.getId(): period },}

        return tuple(results.values())

AccessControl.class_init.InitializeClass(BLLedgerPeriodsFolder)

def delPeriodEndInfo(ob, event):
    """
    roll back period end effects
    """
    tids = list(ob.getProperty('transactions'))
    if tids:
        ob.blLedger().manage_delObjects(tids)

def addPeriodEndInfo(ob, event):
    """
    compute account balances
    """
    ob.manage_updateChart(all=True)


def delPeriodEndInfos(ob, event):
    """
    remove any reports for a full period-end run

    note - you must also delete period-infos in last-to-first order
    """
    ledger = ob.bastionLedger()

    if ob.getId() != ledger.periods.periodIds()[0]:
        raise InvalidPeriodError, 'Not last Period'

    for brainz in ledger.searchResults(meta_type='BLReport', 
                                       effective=ob.effective(),
                                       tags='EOP'):
        try:
            report = brainz.getObject()
        except:
            # wtf???
            continue
        report.aq_parent.manage_delObjects([report.getId()])

    # TODO - remove any depreciations etc

# deprecated
class BLLedgerPeriods(Folder): pass
