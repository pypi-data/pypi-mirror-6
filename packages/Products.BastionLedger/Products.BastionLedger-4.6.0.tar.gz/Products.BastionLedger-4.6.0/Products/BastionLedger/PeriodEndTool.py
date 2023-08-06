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
import AccessControl, logging, os, string
from Acquisition import aq_parent, aq_inner, aq_base
from DateTime import DateTime
from AccessControl.Permissions import access_contents_information
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject
from Products.AdvancedQuery import Between, Eq
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from BLBase import PortalFolder as Folder
from BLGlobals import EPOCH
from utils import ceiling_date, floor_date
from Permissions import ManageBastionLedgers
from BLReport import BLReport
from Exceptions import PostingError, InvalidPeriodError

from interfaces.tools import IBLControllerTool
from zope.interface import implements

#
# heh - just generate plain-text reports of our plone-skinned general reports
#
PLAIN_REPORT='''
<html metal:use-macro="context/blstandard_template.pt/macros/page">
   <div metal:fill-slot="body">
      <div metal:use-macro="context/blreporting_macros/macros/%s-multi"/>
   </div>
</html>
'''

#REPORTS = ('balance-sheet', 'revenue-statement', 'cashflow-statement')
REPORTS = ('balance-sheet', 'revenue-statement',)

def manage_addPeriodEndTool(self, id='periodend_tool', REQUEST=None):
    """
    """
    self._setObject(id, PeriodEndTool())
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))


class _Entry(dict):
    """
    helper to create transaction(s)
    """
    def __init__(self, amount, account, title=''):
        self.title = title
        self.amount = amount
        self.account = account

class PeriodEndTool(UniqueObject, Folder, ActionProviderBase):
    """
    This tool provides process, control, management, and plugins to run
    end of period processing on BastionLedger's.
    """

    implements(IBLControllerTool)

    id = 'periodend_tool'
    meta_type = 'BLPeriodEndTool'
    portal_type = 'BLTool'
    icon = 'misc_/BastionLedger/blquill'

    __ac_permissions__ = (
        (access_contents_information, ('reportingInfos',)),
        (ManageBastionLedgers, ('manage_periodEnd', 'manage_generateReports',
                                'manage_regenerateReports', 'manage_undo',
                                'manage_adjust', 'manage_dailyEnd',
                                'beforeActionsForLedger',
                                'afterActionsForLedger', 'manage_reset',
                                'postClosingEntries')),
        ) + Folder.__ac_permissions__ + ActionProviderBase.__ac_permissions__

    _properties = Folder._properties + (
        {'id':'periods_to_report',    'type':'int', 'mode':'w'},
        )

    _actions = ()
    periods_to_report = 3

    manage_options = ( 
        Folder.manage_options[0], ) + \
        ActionProviderBase.manage_options + Folder.manage_options[2:]

    def __init__(self, id='', title=''):
        self.title = title

    def all_meta_types(self):
        return []

    def Description(self):
	return self.__doc__

    def manage_undo(self, ledger, effective):
        """
        undo all traces of a period end run
        """
        infos = ledger.periods.infosForDate(effective)
        if infos:
            # remove reports
            rf = ledger.Reports
            for report in REPORTS:
                rid = '%s-%s' % (report, infos.getId())
                if getattr(aq_base(rf), rid, None):
                    rf._delObject(rid)
            
            # remove period cache info (and back out period txns)
            ledger.periods.manage_delObjects([infos.getId()])
        else:
            raise InvalidPeriodError, effective
 
    def manage_periodEnd(self, ledger, effective, force=False, REQUEST={}):
        """
        do end-of-period closing entries, ledger-specific end-of-period processing
        and bump opening balance entries in all accounts
        """
        REQUEST = REQUEST or self.REQUEST

        if not isinstance(effective, DateTime):
            effective = DateTime(effective)

        #effective = floor_date(effective.toZone(ledger.timezone))
        effective = floor_date(effective)

        # ensure daily rollover's have been done
        self.manage_dailyEnd(ledger, effective)

        # we need to do the ledger last so that any subsidiary ledger changes are reflected
        # in the control entry
        ledgers = [x for x in filter(lambda x: x.getId() != 'Ledger', ledger.ledgerValues())]
        ledgers.append(ledger.Ledger)

        start_date = ledger.periods.nextPeriodStart(effective)
        end_date = ledger.periods.nextPeriodEnd(effective)

        assert start_date < end_date, 'Invalid date(s) %s -> (%s, %s)' % (effective, start_date, end_date)

        for led in ledgers:

            id = led.getId()
            tids = []

            arguments = dict(REQUEST.get(id, {}))

            # post all auto-correction entries (and tweak reporting lines)
            for func in self.beforeActionsForLedger(led, start_date, end_date):
                tids.extend(func(led, start_date, end_date, force, **arguments))

            # now snapshot balances and reporting amounts 
            pinfo = ledger.periods.addPeriodLedger(led, start_date, end_date, force)

            # roll journals
            tids.extend(self.postClosingEntries(led, end_date, pinfo))
            
            # do anything else (reporting etc)
            for func in self.afterActionsForLedger(led, start_date, end_date):
                tids.extend(func(led, start_date, end_date, pinfo, force, **arguments))

            pinfo._updateProperty('transactions', tids)

        #if not force:
        #    # ensure everything's kosher (ie no previous period unprocessed entries etc etc)
        #    # TODO - ensure genuine txns posted in/for the next day don't get picked up ...
        #    errors = []
        #    for account in ledger.Ledger.accountValues(type=('Income', 'Expense')):
        #        bal = account.balance(effective=end_date+1)
        #        if bal != 0:
        #            errors.append('%s %s' % (account.prettyTitle(), bal))
        #    if errors:
        #        raise PostingError, ', '.join(errors)
        if REQUEST is not None:
            REQUEST.set('manage_tabs_message', 'ran period end for %s' % effective)
            return self.manage_main(self, REQUEST)

    def manage_dailyEnd(self, ledger, effective=None, now=None, REQUEST=None):
        """
        run end-of-day for a ledger
        we allow setting now such that date-based playbacks are possible
        """
        now = now or DateTime()
        effective = ceiling_date(effective or now)
        days = int(effective - ledger.accrued_to)
        if days > 0:
            # process forward-dated transactions ...
            for txn in ledger.transactionValuesAdv(Between('effective', ledger.accrued_to, effective) & Eq('status', 'posted')):
                for entry in txn.entryValues():
                    entry.blAccount()._totalise(entry, now)

            # do anything else ...
            for l in ledger.ledgerValues():
                l.manage_endOfDay(ledger.accrued_to, effective)

            ledger.accrued_to = effective

        if REQUEST is not None:
            REQUEST.set('manage_tabs_message', 'rolled over %i days' % max(days, 0))
            return self.manage_main(self, REQUEST)
        return max(days, 0)

    def reportingInfos(self, ledger, effective):
        """
        return a list of info(s) ids to do multi-reporting upon
        """
        infos = []
        for info in ledger.periods.objectValues('BLPeriodInfos'):
            if effective >= floor_date(info.effective()):
                infos.append(info.getId())
        infos.sort()
        if len(infos) > self.periods_to_report:
            return infos[-self.periods_to_report:]
        return infos

    def manage_regenerateReports(self, ledger, base_id, effective, reports=REPORTS, REQUEST=None):
        """
        update underlying period info to latest ledger charts etc and rerun reports
        """
        for periodid in self.reportingInfos(ledger, effective):
            ledger.periods._getOb(periodid).update()

        return self.manage_generateReports(ledger, base_id, effective, reports, REQUEST)
                
    def manage_generateReports(self, ledger, base_id, effective, reports=REPORTS, REQUEST=None):
        """
        create (or recreate) the Balance sheet, P&L, Cashflow statement et al
        """
        periodids = self.reportingInfos(ledger, effective)
        rf = ledger.Reports
        for report in reports:
            template = ZopePageTemplate(report, PLAIN_REPORT % report).__of__(ledger)
            id = '%s-%s' % (report, base_id)
            if getattr(aq_base(rf), id, None):
                rf._delObject(id)
            rf._setObject(id, 
                          BLReport(id, 
                                   '%s %s' % (string.capwords(report.replace('-', ' ')), effective.strftime('%B %Y')), 
                                   effective, 
                                   str(template(effective=effective, periodids=periodids)),
                                   tags=('EOP',)))

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Generated %i reports' % len(reports))
            return self.manage_main(self, REQUEST)

    def manage_adjust(self, ledger, effective, acc1, acc2, amount, REQUEST=None):
        """
        'adjust' a period-end (and flow results forward) to future period-ends
        """
        infos = ledger.periods.infosForDate(effective)

        rec1 = infos.Ledger._getObCreate(acc1)
        rec2 = infos.Ledger._getObCreate(acc2)

        rec1.manage_changeProperties(balance=rec1.balance + amount,
                                     reporting_balance = rec1.reporting_balance + amount)

        rec2.manage_changeProperties(balance=rec2.balance - amount,
                                     reporting_balance = rec2.reporting_balance - amount)

        pl_id = ledger.Ledger.accountValues(tags='profit_loss')[0].getId()

        # do P & L adjustments ??
        if rec1.type in ('Income', 'Expense') or rec2.type in ('Income', 'Expense'):

            txns = infos.Ledger.blTransactions()
            closing_txn = filter(lambda x: x.Title().find('Closing') != -1, txns)[0]
            profit_txn = filter(lambda x: x.Title().find('P & L') != -1, txns)[0]

            if rec1.type in ('Income', 'Expense'):
                infos.adjustProfit(amount)
                #profitinfo = infos.Ledger._getOb(pl_id)
                #profitinfo.manage_changeProperties(balance=profitinfo.balance + amount,
                #                                   reporting_balance = profitinfo.reporting_balance + amount)
                closing_txn.blEntry(rec1.id).amount += amount
                closing_txn.blEntry(pl_id).amount -= amount

            if rec2.type in ('Income', 'Expense'):
                infos.adjustProfit(-amount)
                #profitinfo = infos.Ledger._getOb(pl_id)
                #profitinfo.manage_changeProperties(balance=profitinfo.balance - amount,
                #                                   reporting_balance = profitinfo.reporting_balance - amount)
                closing_txn.blEntry(rec2.id).amount += amount
                closing_txn.blEntry(pl_id).amount -= amount
                
            for entry in profit_txn.entryValues():
                # TODO - zero amounts wtf??
                if entry.amount != 0:
                    entry.amount += amount

        # tweak forwards for A, L, P
        finfos = infos.nextPeriod()
        while finfos is not None:
            if finfos.losses_forward > 0 and rec1.type == 'Income' or rec2.type == 'Expense':
                finfos.losses_forward += amount

            rec1 = finfos.Ledger._getOb(acc1)
            rec2 = finfos.Ledger._getOb(acc2)

            profitinfo = finfos.Ledger._getOb(pl_id)
            if rec1.type in ('Asset', 'Liability', 'Proprietorship'):
                rec1.manage_changeProperties(balance=rec1.balance + amount,
                                             reporting_balance = rec1.reporting_balance + amount)
                profitinfo.manage_changeProperties(balance=profitinfo.balance - amount,
                                                   reporting_balance = profitinfo.reporting_balance - amount)

            if rec2.type in ('Asset', 'Liability', 'Proprietorship'):
                rec2.manage_changeProperties(balance=rec2.balance - amount,
                                             reporting_balance = rec2.reporting_balance - amount)
                profitinfo.manage_changeProperties(balance=profitinfo.balance + amount,
                                                   reporting_balance = profitinfo.reporting_balance + amount)
                
            finfos = finfos.nextPeriod()

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def postClosingEntries(self, ledger, effective, pinfo):
        """
        create and post a closing transaction for the ledger - and all subsidiary
        journals
        """
        tids = []
        profit = 0
        led = ledger.Ledger

        entries = []

        #
        # close out all income and expenses ...
        #
        for account in ledger.accountValues(type=('Income', 'Expense')):
            # don't use balance because it relies on us for opening entries - but _sum doesn't compute
            # control entries properly !!!
            #balance = account.total(effective=(beginning, effective))
            balance = account.balance(effective=effective)
            if balance != 0:
                entries.append(_Entry(-balance, account.getId()))

        if entries:
            txn = ledger.createTransaction(title="EOP - Closing Entries",
                                           effective=effective,
                                           entries=entries)
            txn.createEntry(led.accountValues(tags='profit_loss')[0], -txn.total())
            txn.manage_post()
            tids.append(txn.getId())

            # ensure posted balances are correct (but not reported)
            pinfo.postTransactions(tids, reporting=False)

        return tids

    def beforeActionsForLedger(self, ledger, beginning, effective):
        """
        return a list of functors to do end-of-period processing
        """
        if ledger.meta_type in ('BLLedger',):
            return [ self._beforeLedger ]
        if ledger.meta_type in ('BLPayroll', 'FSPayroll'):
            return [ self._beforePayroll ]
        return []

    def afterActionsForLedger(self, ledger, beginning, effective):
        """
        return a list of functors to do end-of-period processing
        """
        if ledger.meta_type in ('BLLedger',):
            return [ self._afterLedger ]
        if ledger.meta_type in ('BLPayroll', 'FSPayroll'):
            return [ self._afterPayroll ]
        return []

    #
    # general file-system end-of-period functions ...
    #
    def _beforePayroll(self, ledger, beginning, effective, force, **kw):
        if kw.get('tax_certs', False):
            ledger.manage_taxCertificates(beginning, effective, send=False)
        # no txns
        return []

    def _afterPayroll(self, ledger, beginning, effective, pinfo, force, **kw):
        # adjust future-dated payment totals
        for employee in ledger.accountValues(status='open'):
            map(lambda x: x.calculateRunningTotals(),
                filter(lambda x: x.blTransaction().effective_date >= effective,
                       employee.objectValues('BLPaySlip')))
        # no txns
        return []

    def _beforeLedger(self, ledger, beginning, effective, force, **kw):
        """
        Apply depreciation to general ledger
        Calculate and post company tax, losses recognised, losses forward etc
        """
        tids = []
        bastionledger = ledger.aq_parent

        for assetregister in kw.get('assetregisters', []):
            # only optionally generate txn ... - and don't mangle effective dates
            tid = bastionledger._getOb(assetregister)._applyDepreciation([beginning, effective],
                                                                         description='EOP - Depreciation',
                                                                         force=force)
            if tid:
                tids.append(tid)

        gross = bastionledger.grossProfit((beginning, effective))
        losses_available = attributable = losses_fwd = ledger.zeroAmount()
        try:
            # fetch losses available from prior period
            losses_available = bastionledger.periods.infosForDate(beginning-1).losses_forward
        except:
            pass

        # we've suffered a loss, how much can we attribute to this period
        if gross > 0:
            attributable = bastionledger.lossesAttributable((beginning, effective), gross)
            
        tax = bastionledger.corporationTax((beginning, effective), 
                                           gross_profit=gross, 
                                           attributable_losses=attributable)

        net = bastionledger.netProfit((beginning, effective), 
                                      gross_profit=gross, 
                                      corporation_tax=tax, 
                                      attributable_losses=attributable)
            
        # actual losses forward need to be computed
        if net < 0:
            losses_fwd = max(losses_available - attributable - net, losses_fwd)
        else:
            losses_fwd = max(losses_available - attributable, losses_fwd)

        bastionledger.periods.addPeriodProfits(beginning, 
                                               effective, 
                                               gross, 
                                               net, 
                                               tax, 
                                               attributable, 
                                               losses_fwd)

        tax_exp = ledger.accountValues(tags='tax_exp')[0]
        tax_accr = ledger.accountValues(tags='tax_accr')[0]
        tax_recv = ledger.accountValues(tags='tax_recv')[0]

        tax_paid = tax_exp.balance(effective=effective)

        if tax_paid != tax:
            txn = ledger.createTransaction(title="EOP - Corporation Tax",
                                           effective=effective)
            tax_diff = tax_paid - tax

            if tax_diff > 0:
                # we've paid too much, adjust tax exp downward, and into current asset
                #accrued = tax_accr.balance(effective=effective)
                #if accrued < 0:
                #    txn.createEntry(tax_accr, -accrued)
                txn.createEntry(tax_recv, tax_diff)
                txn.createEntry(tax_exp, -tax_diff)
            else:
                txn.createEntry(tax_accr, tax_diff)
                txn.createEntry(tax_exp, -tax_diff)
                    
            txn.manage_post()
            tids.append(txn.getId())

        #if attributable > 0:
        #    txn = ledger.createTransaction(title="EOP - Losses Carried Forward",
        #                                   effective=effective)
        #    txn.createEntry(ledger.accountValues(tags='profit_loss')[0], -attributable)
        #    txn.createEntry(ledger.accountValues(tags='loss_fwd')[0], attributable)
        #    txn.manage_post()
        #    tids.append(txn.getId())

        return tids
            
    def _afterLedger(self, ledger, beginning, effective, pinfo, force, **kw):
        """
        General Ledger post-processing - clear our dividends declared, post
        corporation tax, and move current earnings to retained
        """
        tids = []
        bastionledger = ledger.aq_parent
        profit_acc = ledger.accountValues(tags='profit_loss')[0]

        # we need to carry P & L amount over into reporting
        adjustment = pinfo.net_profit + pinfo.losses_recognised
        if adjustment != 0:
            pinfo.manage_updateReportingBalances([{'id':profit_acc.getId(), 
                                                   'amount': pinfo.reportedBalance(profit_acc.getId()) - adjustment}],
                                                 force=True)

        self.manage_generateReports(bastionledger, 
                                    pinfo.aq_parent.getId(), 
                                    effective, kw.get('reports',[]))

        # roll P & L forward
        profit = profit_acc.balance(effective=effective)
        retained = ledger.accountValues(tags='retained_earnings')[0]
        txn = None
        if profit != 0:
            txn = ledger.createTransaction(title="EOP - P & L",
                                           effective=effective + 1)
            txn.createEntry(profit_acc, -profit)
            if profit < 0:
                txn.createEntry(retained, profit)
            else:
                # bummer it's a loss, make it a deferred tax credit
                #txn.createEntry(ledger.accountValues(tags='tax_defr')[0], profit)
                txn.createEntry(ledger.accountValues(tags='loss_fwd')[0], profit)

        # apply any losses recognised against future losses available
        if pinfo.losses_recognised > 0:
            if txn is None:
                txn = ledger.createTransaction(title="EOP - P & L",
                                               effective=effective + 1)
            txn.createEntry(ledger.accountValues(tags='loss_fwd')[0], -pinfo.losses_recognised)
            txn.createEntry(retained, pinfo.losses_recognised)

        if txn:
            txn.manage_post()
            tids.append(txn.getId())

        return tids

    def manage_reset(self, ledger, REQUEST=None):
        """
        roll back the entire thing and start again ...
        """
        # roll back all the txns
        periods = ledger.periods
        for pid in periods.periodIds():
            periods.manage_delObjects([pid])

        # unset all depreciations
        for reg in ledger.objectValues('BLAssetRegister'):
            reg.manage_reset()

AccessControl.class_init.InitializeClass(PeriodEndTool)


