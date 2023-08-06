## Controlled Python Script "validate_payroll_date"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective=''
##title=Validates payroll should be run for date, and that it's not been run for that date already
##
if not effective:
    context.plone_utils.addPortalMessage('No payroll date set.', 'error')
    return state.set(status='failure')

if context.isRun(effective):
    context.plone_utils.addPortalMessage('Payroll already run for date.', 'error')
    context.REQUEST.set('date', effective)
    return state.set(status='failure')

return state

