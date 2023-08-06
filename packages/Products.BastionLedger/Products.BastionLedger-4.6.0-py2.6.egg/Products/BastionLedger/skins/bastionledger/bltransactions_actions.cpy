## Controller Python Script "bltransactions_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=transactions actions
##
REQUEST=context.REQUEST

ids = REQUEST['ids']

if REQUEST.has_key('form.button.Delete'):
    context.manage_delObjects(ids)
    context.plone_utils.addPortalMessage('Deleted %i transaction(s)' % len(ids))
elif REQUEST.has_key('form.button.Post'):
    context.manage_post(ids)
    context.plone_utils.addPortalMessage('Posted %i transaction(s)' % len(ids))
elif REQUEST.has_key('form.button.Repost'):
    context.manage_repost(ids)
    context.plone_utils.addPortalMessage('Reposted %i transaction(s)' % len(ids))
elif REQUEST.has_key('form.button.Reverse'):
    context.manage_reverse(ids)
    context.plone_utils.addPortalMessage('Reversed %i transaction(s)' % len(ids))
else:
    context.plone_utils.addPortalMessage('No action specified')

return state.set(status='success')

