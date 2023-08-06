## Controller Python Script "blorderss_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=orders actions
##
REQUEST=context.REQUEST

ids = REQUEST['ids']

def run(func, ids):
    for order in map(lambda x: getattr(context, x)):
        getattr(order, func)()

if REQUEST.has_key('form.button.Delete'):
    context.manage_delObjects(ids)
    context.plone_utils.addPortalMessage('Deleted %i orders(s)' % len(ids))
elif REQUEST.has_key('form.button.Cancel'):
    run('manage_cancel', ids)
    context.plone_utils.addPortalMessage('Posted %i orders(s)' % len(ids))
elif REQUEST.has_key('form.button.Invoice'):
    run('manage_invoice', ids)
    context.plone_utils.addPortalMessage('Reposted %i orders(s)' % len(ids))
else:
    context.plone_utils.addPortalMessage('No action specified')

return state.set(status='success')

