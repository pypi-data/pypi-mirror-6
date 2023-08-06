## Controller Python Script "part_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=urls=[],unit='',weight=0.0,onhand=0.0,sellprice=None,listprice=None,lastcost=None,inventory_accno='',income_accno='',expense_accno='',id='',text_format='',text='',title='',description=''
##title=edit part quantity and price details
##
REQUEST=context.REQUEST

if REQUEST.has_key('form.button.ContentEdit'):
    context.manage_changeProperties(title=title, description=description)
    context.manage_editDocument(text, text_format)
    context.plone_utils.addPortalMessage('Edited Part Description')
    return state.set(context=context)

if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)

new_context.edit_prices(unit, weight, onhand, sellprice, listprice, lastcost, 
    	                inventory_accno, income_accno, expense_accno)

new_context.manage_changeProperties(urls=urls)

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

