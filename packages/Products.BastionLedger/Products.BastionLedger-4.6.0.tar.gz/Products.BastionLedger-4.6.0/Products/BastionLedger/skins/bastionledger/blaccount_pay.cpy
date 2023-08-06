##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective,amount,reference='',bms=None
##title=do a payment on account
##
from Products.CMFCore.utils import getToolByName
from Products.BastionBanking import ZReturnCode
from Products.BastionBanking.Exceptions import *
from Products.BastionLedger.BLEntry import manage_addBLEntry

# acquire the GL
ledger = context.Ledger
bms = bms or context.getBastionMerchantService()

if bms:
    bank_account = ledger.accountValues(tags='merchant')[0]
else:
    bank_account = ledger.accountValues(tags='bank_account')[0]

#
# go create our Payment transaction
#
txn = context.blLedger().createTransaction(title='Payment - Thank You',
                                           effective=effective,
                                           ref=reference)
manage_addBLEntry(txn, bank_account, amount)
txn.createEntry(context, -amount)

#
# let the Merchant Service pay and post the txn (if successfully paid)
#
if bms:
    # we presently still need to complete via the BMS return url :(
    #bms.manage_payTransaction(txn, reference, return_url=context.absolute_url())
    try:
        bms.manage_payTransaction(txn, reference or context.prettyTitle())
    except InvalidAmount:
        state.setError('amount', 'Invalid Amount')
    except UnsupportedCurrency:
        state.setError('amount', 'Invalid Currency')
    except CreditCardInvalid:
        state.setError('cardinvalid', 'Invalid Card Number')
    except CreditCardExpired:
        state.setError('cardexpired', 'Card Expired')
    except ProcessingFailure, e:
        state.setError('processing', str(e))
else:
    txn.manage_post()

if state.getErrors():
    state.set(status='failure')
    context.plone_utils.addPortalMessage('Please correct indicated errors')

else:
    context.plone_utils.addPortalMessage('Thank you for your payment')

return state
