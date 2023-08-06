## Controller Python Script "bltransactions_bulkload"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=accno, currency, entries, ledger='', post=True
##title=bulk-load entries into txn's against account
##
from Products.BastionBanking.ZCurrency import ZCurrency

#
# verify main form fields
#
try:
    account = context.accountValues(accno=accno)[0]
except:
    state.setError('accno', 'Account not found', 'not_found')
    return state.set(status='failure')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')

now = DateTime()
parsed_entries = []

#
# parse all the inputs, returning error(s) as discovered
#
for entry in entries:
    effective = entry['effective']

    # empty form fields ...
    if not effective:
        continue

    if len(effective) == 4:
        effective = '%i/%s/%s' % (now.year(), effective[0:2], effective[2:])
    elif len(effective) != 10:
        effective = '%s/%s/%s' % (effective[0:4], effective[4:6], effective[6:8])

    try:
        effective = DateTime(effective)
    except Exception, e:
        context.plone_utils.addPortalMessage('Effective Date Error: %s' % str(e), 'error')
        return state.set(status='failure')

    try:
        other = context.accountValues(accno=entry['accno'])[0]
    except Exception, e:
        context.plone_utils.addPortalMessage('Account not found: %s' % entry['accno'], 'error')
        return state.set(status='failure')

    try:
        amount = ZCurrency('%s %s' % (currency, entry['amount']))
    except Exception, e:
        context.plone_utils.addPortalMessage('Invalid currency: %s %s' % (currency, entry['amount']), 'error')
        return state.set(status='failure')

    parsed_entries.append({'title': entry['description'], 
                           'effective': effective, 
			   'amount': amount,
			   'accno': entry['accno']})

#
# we're good to go, create the transactions
#
txns = context.createTransactions(parsed_entries, accno, ledger, post)


context.plone_utils.addPortalMessage('Posted %i transactions' % len(txns))
return state

