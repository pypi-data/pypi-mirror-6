## Controller Python Script "blledger_change_controlAccount"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=control_accounts=[],effective=None
##title=change the control account for a subsidiary ledger
##

if not control_accounts:
    state.setError('controlAccounts', 'Account Number Required', 'accno_required')

controls = context.Ledger.accountValues(id=control_accounts)
if len(controls) != len(control_accounts):
    state.setError('controlAccounts', 'Unknown Account Number(s)', 'accno_unknown')

control_type = ''
for acc in controls:
    if control_type and acc.type != control_type:
        state.setError('controlAccounts', 'Incompatible Account Types', 'accno_unknown')
    if control_type == '':
        control_type = acc.type

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')

context.manage_changeControl(control_accounts, effective)

context.plone_utils.addPortalMessage('Control Account Changed')
return state

