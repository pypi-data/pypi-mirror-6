## Controller Python Script "blpayroll_run"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective,ids=[]
##title=run payroll for specified date
##
context.manage_payEmployees(ids, effective)

context.plone_utils.addPortalMessage('Payroll for %s completed' % context.toLocalizedTime(effective))
context.REQUEST.set('date', effective)

return state.set(status='success')

