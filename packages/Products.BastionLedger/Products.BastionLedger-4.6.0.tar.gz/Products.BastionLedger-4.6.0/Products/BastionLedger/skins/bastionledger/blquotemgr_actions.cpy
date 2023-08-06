## Controller Python Script "blquotemgr_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email='',ids=[]
##title=BLQuoteManager actions
##
from Products.CMFCore.utils import getToolByName

request = context.REQUEST

if request.has_key('form.button.Delete') and ids:
     context.manage_delObjects(ids)
elif request.has_key('form.button.Paste'):
     context.manage_pasteObjects(REQUEST=request)
elif request.has_key('form.button.Copy') and ids:
     cp = context.manage_copyObjects(ids)
     request.RESPONSE.setCookie('__cp', cp, path='%s' % request.get('BASEPATH1', '/'))
elif request.has_key('form.button.Email'):
     member = getToolByName(context, 'portal_membership').getAuthenticatedMember()
     if member.hasProperty('email'):
         mfrom = member.getProperty('email')
     else:
         mfrom = getToolByName(context, 'portal_url').getPortalObject().getProperty('email_from_address')
     company = context.getLedgerProperty('title')
     context.manage_sendmail(ids, mfrom, email, '%s - Quote(s)' % company)
     getToolByName(context, 'plone_utils').addPortalMessage('Emailed quotes(s) to %s' % email)

return state

