## Controlled Python Script "validate_accno"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=accno=''
##title=Validates accno
##
if not accno:
    state.setError('accno', 'Account Number Required', 'accno_required')

if self.bastionLedger().searchResults(accno=accno, ledgerId=context.ledgerId()):
    state.setError('accno', 'Duplicate Account Number', 'duplicate_accno')


if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

