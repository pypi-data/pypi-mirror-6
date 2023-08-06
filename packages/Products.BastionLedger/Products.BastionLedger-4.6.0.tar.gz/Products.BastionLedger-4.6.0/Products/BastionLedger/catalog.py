#
#    Copyright (C) 2012-2013  Corporation of Balclutha. All rights Reserved.
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
import logging, time
from Acquisition import aq_base
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import CatalogError
from Products.ManagableIndex import FieldIndex, KeywordIndex, RangeIndex
from Products.TextIndexNG3.TextIndexNG3 import TextIndexNG3

LOG = logging.getLogger('BastionLedger::cataloging')


def removeAllIndexes(catalog):
    """ helper to clean out catalog """
    if getattr(aq_base(catalog), '_catalog', None) is None:
        LOG.info('%s initializing catalog' % catalog.absolute_url())
        ZCatalog.__init__(catalog, catalog.id, catalog.title)
    else:
        catalog.manage_delIndex(catalog.indexes())
        # below is catalog.schema() - but unfortunately it's being overridden by AT, so
        # it's the underlying implementation ...
        catalog.manage_delColumn(catalog._catalog.schema.keys())

def makeFieldIndex(catalog, indexName):
    """
    return a Field Index (exact match) unicode to internationlise type/subtype etc
    """
    if indexName in catalog.indexes():
        return
    index = FieldIndex(indexName)
    #index.PrenormalizeTerm = 'value/lower'
    index.PrenormalizeTerm = ''
    index.TermType = 'ustring'
    catalog.addIndex(indexName, index)
    return index

def makeKeywordIndex(catalog, indexName):
    """
    return a case-sensitive unicode Keyword Index
    """
    if indexName in catalog.indexes():
        return
    index = KeywordIndex(indexName)
    #index.PrenormalizeTerm = 'value/lower'
    index.PrenormalizeTerm = ''
    index.TermType = 'ustring'
    index.TermTypeExtra = 'latin-1'
    catalog.addIndex(indexName, index)
    return index

def makeDateIndex(catalog, indexName, termType='DateTime'):
    """
    return a Date(Range) Index
    """
    if indexName in catalog.indexes():
        return
    index = FieldIndex(indexName)
    index.TermType = termType
    catalog.addIndex(indexName, index)
    return index

def makeTextIndex(catalog, indexName,extra={}):
    """
    """
    if indexName in catalog.indexes():
        return
    index = TextIndexNG3(indexName, extra, None)
    catalog.addIndex(indexName, index)
    return index
    

def makeLedgerCatalog(blLedger, reindex=False):
    """
    NOTE - ledger catalogs have *moved* to the BastionLedger ...
    """
    now = time.time()
    if getattr(aq_base(blLedger), '_catalog', None) is None:
        LOG.info('%s initializing catalog' % blLedger.absolute_url())
        ZCatalog.__init__(blLedger, blLedger.id, blLedger.title)

    makeKeywordIndex(blLedger, 'tags')
    makeDateIndex(blLedger, 'created')
    makeDateIndex(blLedger, 'effective', 'DateInteger') # DateTime, DateTimeInteger, DateInteger
    makeTextIndex(blLedger, 'title')
    for field in ('id', 'type', 'subtype', 'accno', 'status', 'meta_type', 'entered_by', 
                  'accountId', 'ledgerId', 'transactionId'):
        makeFieldIndex(blLedger, field)

    # seems some Ledger stuff is copied from master
    for field in ('id', 'meta_type', 'title', 'type', 'subtype', 'accno'):
        if field not in blLedger._catalog.schema:
            blLedger.addColumn(field)

    if reindex:
        LOG.info('%s reindexing' % blLedger.absolute_url())
        for ledger in blLedger.ledgerValues():
            for ob in ledger.accountValues() + ledger.transactionValues():
                ob.indexObject()
                for entry in ob.entryValues():
                    entry.indexObject()

    LOG.info('%s recataloged in %0.6f seconds' % (blLedger.absolute_url(), time.time() - now))

def removeBLLedgerCatalog(ledger):
    """
    """
    for old in ('Accounts', 'Transactions'):
        if getattr(aq_base(ledger), old, None):
            removeAllIndexes(getattr(ledger, old))
            delattr(ledger, old)
    removeAllIndexes(ledger)

def makeBLInventoryCatalog(inventory):
    """
    """
    cat = inventory.catalog
    makeTextIndex(cat, 'SearchableText')
    makeFieldIndex(cat, 'id')
    makeFieldIndex(cat, 'meta_type')
    makeDateIndex(cat, 'created')
    makeTextIndex(cat, 'title')
    for name in ('id', 'meta_type', 'title'):
        cat.addColumn(name)

    dispatcher = inventory.dispatcher
    makeFieldIndex(dispatcher, 'id')
    makeFieldIndex(dispatcher, 'meta_type')
    makeFieldIndex(dispatcher, 'status')
    for name in ('id', 'path', 'status'):
        dispatcher.addColumn(name)

def removeBLInventoryCatalog(inventory):
    removeAllIndexes(inventory.catalog)
    removeAllIndexes(inventory.dispatcher)
    

def makeBLAssociationsCatalog(associations):
    makeFieldIndex(associations, 'id')
    makeFieldIndex(associations,'ledger')
    makeKeywordIndex(associations, 'accno')
    associations.addColumn('id')
    
def removeBLAssociationsCatalog(associations):
    removeAllIndexes(associations)

def makeBLQuoteManagerCatalog(quotemgr):
    makeFieldIndex(quotemgr, 'status')
    makeFieldIndex(quotemgr, 'Creator')
    quotemgr.addColumn('meta_type')

def removeBLQuoteManagerCatalog(quotemgr):
    removeAllIndexes(quotemgr)

def makeBLTaxTableCatalog(tt, dimensions):
    makeDateIndex(tt, 'effective_date')
    for d in dimensions:
        if len(d) > 2:
            tt.addIndex(d[0], d[1], extra=d[2])
        else:
            tt.addIndex(d[0], d[1])

def removeBLTaxTableCatalog(tt):
    removeAllIndexes(tt)
        

def rebuildLedgerCatalogs(ledger, reindex=False):
    """
    remove and rebuild all ledger catalogs - this feature is used to implement
    a new cataloging policy
    """
    LOG.info('%s rebuilding catalogs' % ledger.absolute_url())
    removeBLLedgerCatalog(ledger)
    makeLedgerCatalog(ledger, reindex)

    # clean out any old-style catalogs
    for l in ledger.ledgerValues():
        removeBLLedgerCatalog(l)

    for i in ledger.objectValues('BLInventory'):
        removeBLInventoryCatalog(i)
        makeBLInventoryCatalog(i)

    for q in ledger.objectValues('BLQuoteManager'):
        removeBLQuoteManagerCatalog(q)
        makeBLQuoteManagerCatalog(q)


def recatalogLedger(ledger, zfind=True):
    ledger.manage_catalogClear()
    for ob in ledger.ledgerValues():
        ob.manage_catalogClear()
        # some non-ledger types barf when attempting cataloging (mostly due to Archetypes 'type'
        # field ...
        LOG.info('%s %s find and apply' % (ledger.absolute_url(), ob.getId()))
        if zfind:
            ledger.ZopeFindAndApply(ob,
                                    obj_metatypes=ob.account_types + ob.transaction_types + ('BLEntry', 'BLSubsidiaryEntry', 'BLTimeSheet', 'BLPaySlip', 'BLReport'),
                                    search_sub=1,
                                    apply_path='/'.join(ob.getPhysicalPath()),
                                    apply_func=ledger.catalog_object)
        else:
            ob.indexObject()
            for txn in ob.transactionValues():
                LOG.info(txn.getId())
                ledger.catalog_object(txn, '/'.join(txn.getPhysicalPath()))
                for entry in txn.entryValues():
                    ledger.catalog_object(entry, '/'.join(entry.getPhysicalPath()))
            for account in ob.accountValues():
                LOG.info(account.getId())
                ledger.catalog_object(account, '/'.join(account.getPhysicalPath()))
                for ent in account.objectValues():
                    if not ent.meta_type in ('BLControlEntry', 'BLSubsidiaryEntry', 'BLEntry'):
                        LOG.info('%s - %s' % (ent.getId(), ent.meta_type))
                        ledger.catalog_object(ent, '/'.join(ob.getPhysicalPath()))

    for ob in ledger.objectValues('BLInventory'):
        ob.catalog.manage_catalogClear()
        LOG.info('%s find and apply' % ob.getId())
        ob.catalog.ZopeFindAndApply(ob,
                                    obj_metatypes=['BLPart', 'BLPartFolder'],
                                    search_sub=1,
                                    apply_path='/'.join(ob.getPhysicalPath()),
                                    apply_func=ob.catalog.catalog_object)
        dispatcher = ob.dispatcher
        dispatcher.manage_catalogClear()
        LOG.info('inventory dispatcher find and apply')
        dispatcher.ZopeFindAndApply(ob,
                                    obj_metatypes=['BLDispatchable'],
                                    search_sub=1,
                                    apply_path='/'.join(dispatcher.getPhysicalPath()),
                                    apply_func=dispatcher.catalog_object)
        
    for ob in ledger.objectValues('BLQuoteManager'):
        ob.manage_catalogClear()
        LOG.info('%s find and apply' % ob.getId())
        ob.ZopeFindAndApply(ob,
                            obj_metatypes=['BLQuote'],
                            search_sub=1,
                            apply_path='/'.join(ob.getPhysicalPath()),
                            apply_func=ob.catalog_object)
    LOG.info('completed')


def rebuildControllerCatalogs(controllertool):
    if getattr(aq_base(controllertool), '_catalog', None) is None:
        LOG.info('%s initializing catalog' % controllertool.absolute_url())
        ZCatalog.__init__(controllertool, controllertool.id, controllertool.title)
        makeLedgerCatalog(controllertool, reindex=True)
 
    for tt in controllertool.objectValues('BLTaxTable'):
        dimensions = []
        for d in tt.dimensions():
            dimensions.append(tt.indexInfo(d))

        removeBLTaxTableCatalog(tt)
        makeBLTaxTableCatalog(tt, dimensions)
        tt.ZopeFindAndApply(tt,
                            obj_metatypes=['BLTaxTableRec'],
                            search_sub=0,
                            apply_path='/'.join(tt.getPhysicalPath()),
                            apply_func=tt.catalog_object)

    for assoc in controllertool.objectValues('BLAssociationFolder'):
        removeBLAssociationsCatalog(assoc)
        makeBLAssociationsCatalog(assoc)
        assoc.ZopeFindAndApply(assoc,
                               obj_metatypes=['BLAssociation'],
                               search_sub=0,
                               apply_path='/'.join(assoc.getPhysicalPath()),
                               apply_func=assoc.catalog_object)

    for ledger in controllertool.objectValues('BLLedger'):
        removeBLLedgerCatalog(ledger)
