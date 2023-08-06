## Controller Python Script "blorder_additems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=orderdate,reqdate,taxincluded=0,discount=0.0,notes='',title='',company='',contact='',email='',billingaddress='',shiptoaddress='',part_ids=[],id=''
##title=add BLOrderItem's
##

id = id or context.getId()
new_context = context.portal_factory.doCreate(context, id)

new_context.blorder_edit(orderdate=orderdate,
			 reqdate=reqdate,
                         taxincluded=taxincluded,
                         discount=discount,
                         notes=notes,
                         title=title,
			 company=company,
                         contact=contact,
                         email=email,
			 billingaddress=billingaddress,
			 shiptoaddress=shiptoaddress)

for part_id in part_ids:
    new_context.manage_addProduct['BastionLedger'].manage_addBLOrderItem(part_id)

return state.set(context=new_context)

