## Controller Python Script "blorder_new_account"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=create a new account from this order
##
account = context.upgradeToAccount(context.blLedger().getId())

context.plone_utils.addPortalMessage('Created Account')
return state.set(context=account)
