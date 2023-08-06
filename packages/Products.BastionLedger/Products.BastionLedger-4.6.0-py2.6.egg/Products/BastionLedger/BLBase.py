#
#    Copyright (C) 2002-2014  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import AccessControl, Acquisition, Products, string
from App.special_dtml import DTMLFile
from Acquisition import aq_base
from AccessControl import getSecurityManager, ClassSecurityInfo, SecurityManagement
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime
from OFS.ObjectManager import ObjectManager, REPLACEABLE
from OFS.CopySupport import CopyError
from OFS.SimpleItem import SimpleItem
from OFS.owner import Owned
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import implements
from zope.i18nmessageid import MessageFactory

PLMF = MessageFactory('plonelocales')


# keep Plone support optional (at this stage)
#
# note that this trickery derives of PortalContent base types and thus expects
# portal_types/portal_skins tools in the aquisition path which may cause you
# some unpleasant surprises if this isn't so ....
#
try:
    from Acquisition import ImplicitAcquisitionWrapper
    from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
    #from Products.ATContentTypes.content.folder import ATBTreeFolder as BTreeFolder2
    from Products.CMFPlone.PloneFolder import PloneFolder
    from Products.CMFCore.permissions import ModifyPortalContent
    from Products.CMFCore.DynamicType import DynamicType
    from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
    from Products.CMFCore.WorkflowCore import WorkflowException
    from Products.CMFCore.utils import getToolByName
    from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
    from webdav.NullResource import NullResource

    from Products.Archetypes.interfaces import IReferenceable
    from Products.Archetypes.Referenceable import Referenceable
    from Products.Archetypes.public import ReferenceField, Schema
    from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
    from Products.Archetypes.public import Schema
    from Products.Archetypes.config import UUID_ATTR, REFERENCE_CATALOG

    from plone.portlets.interfaces import ILocalPortletAssignable
    from zope.publisher.interfaces import IPublishTraverse

    from Products.ATContentTypes.atct import ATFolder

    class OrderedFolder(PloneFolder):
         manage_main = DTMLFile('dtml/main', globals())

    AccessControl.class_init.InitializeClass(OrderedFolder)

    class BaseContent( DynamicType, DefaultDublinCoreImpl, SimpleItem, CMFCatalogAware, Referenceable):
        """
        Sort out our default views ...
        """
        implements(ILocalPortletAssignable, IReferenceable)
        #implements(ILocalPortletAssignable, IReferenceable, IPublishTraverse)

        isPortalContent = 1
        _isPortalContent = 1  # More reliable than 'isPortalContent'.

        # hmmm - a late addition ...
        description = ''

        relatedItems = ()
        relationship = 'relatesTo'

        schema = Schema((
                ReferenceField('relatedItems',
                               required=False,
                               searchable=True,
                               relationship='relatesTo',
                               languageIndependent = False,
                               multiValued=True,
                               index = 'KeywordIndex',
                               write_permission = ModifyPortalContent,
                               widget = ReferenceBrowserWidget(description = ("Urls of any related items."),
                                                               description_msgid = "help_related_items",
                                                               label = "Related Items",
                                                               label_msgid = "label_related_items",
                                                               i18n_domain = "plone")),
                ))

        __ac_permissions__ =  DefaultDublinCoreImpl.__ac_permissions__ + \
                             SimpleItem.__ac_permissions__ + \
                             CMFCatalogAware.__ac_permissions__

        manage_options = DefaultDublinCoreImpl.manage_options + (
            {'label':'View', 'action':'view' },
            ) + SimpleItem.manage_options

        def __init__(self, id, title='', description=''):
            DefaultDublinCoreImpl.__init__(self)
            self.id = id
            self.title = title
            self.description = description
            
        def _getPortalTypeName(self):
            """
            needed for the portal type view mechanism ...
            """
            return self.portal_type
 
        getPortalTypeName = _getPortalTypeName

        def getStatusOf(self, workflow):
            """
            return the status of ourselves in the context of this workflow (the corresponding
            WorkflowTool function is strangely declared private ...
            """
            try:
                return getToolByName(self, 'portal_workflow').getInfoFor(self, workflow.state_var)
            except WorkflowException:
                return 'Doh'

        def getActionsFor(self, workflow):
            """
            return a list of valid transition states
            """
            state = workflow._getWorkflowStateOf(self)
            return state.getTransitions()

        def publishTraverse(self, REQUEST, name):
            """
            This is copied from OFS/Application (__bobo_traverse__) and seems strangely necessary
            since Plone 3.0 upgrade (and still required for 4.x)...
            """
            try:
                return getattr(self, name)
            except:
                try:
                    return self[name]
                except:
                    pass
            method=REQUEST.get('REQUEST_METHOD', 'GET')
            if not method in ('GET', 'POST'):
                return NullResource(self, name, REQUEST).__of__(self)

            return None

        def Schema(self):
            """Return a (wrapped) schema instance for this object instance.
            """
            schema = self.schema
            return ImplicitAcquisitionWrapper(schema, self)

        def UID(self):
            """
            if we've not been fancily created via archetypes etc, then generate
            a UID on asking
            """
            uid = Referenceable.UID(self)
            if not uid:
                # this is _register()
                reference_manager = getToolByName(self, REFERENCE_CATALOG)
                reference_manager.registerObject(self)

                # also manually update UID catalog
                self._updateCatalog(self)

            return uid or Referenceable.UID(self)

        def referencedObjects(self):
            """
            a list of hashes, uid, relationship, isref (ref or backref flag), object
            """
            results = []
            for relationship in self.getRelationships():
                for ob in self.getReferences(relationship):
                    results.append({'uid':ob.UID(),
                                    'relationship':relationship,
                                    'isref': True,
                                    'object': ob})
            for relationship in self.getBRelationships():
                for ob in self.getBackReferences(relationship):
                    # hmmm - getting bad back refs ...
                    if ob:
                        results.append({'uid':ob.UID(),
                                        'relationship':relationship,
                                        'isref': False,
                                        'object': ob})
            return results

        def manage_afterAdd(self, item, container):
            isCopy = getattr(item, '_v_is_cp', None)
            # Before copying we take a copy of the references that are to be copied
            # on the new copy
            if isCopy:
                # If the object is a copy of a existing object we
                # want to renew the UID, and drop all existing references
                # on the newly-created copy.
                setattr(self, UUID_ATTR, None)
                self._delReferenceAnnotations()

            ct = getToolByName(container, REFERENCE_CATALOG, None)
            self._register(reference_manager=ct)
            self._updateCatalog(container)
            self._referenceApply('manage_afterAdd', item, container)
  
    AccessControl.class_init.InitializeClass(BaseContent)
    
    DO_PLONE = 1
except:
    raise

class __ProductsDictionary:
    """
    a naf cached dictionary of products
    
    this needs to be written this way because we have to be sure all products
    are known before defining the dictionary

    """
    def __call__(self, kw=''):

        if not getattr(self, '_v_dict', None):
            self._v_dict = {}
            for product in Products.meta_types:
                self._v_dict[product.get('name')] = product
        if kw == '':
            return self._v_dict
        
        # just return None if something's not been product-registered
        return self._v_dict.get(kw, None)

ProductsDictionary = __ProductsDictionary()


class PortalContent(BaseContent):
    """
    Adding future potential to customise behaviour and formatting ...
    Presently we're hiding workflow implementation.
    """
    _md = {}

    # force CMFCore stuff to defer to portal_types in copy/paste/rename ops
    __factory_meta_type__ = None

    __ac_permissions__ = (
	(view, ('status', 'getTypeInfo', 'actions')),
        ) + BaseContent.__ac_permissions__

    # hmmm - this was rather forgotten in Zope -> Plone port ...
    description = ''

    # Plone basic requirement ...
    _properties = (
        {'id':'title',       'type':'string', 'mode':'w' },
        {'id':'description', 'type':'text',   'mode':'w'},
        )
    
    manage_options = (
        {'label':'Dublin Core', 'action':'manage_metadata',},
        {'label':'Undo',        'action':'manage_UndoForm',  'help':('OFSP','Undo.stx')},
        {'label':'Security',    'action':'manage_access',    'help':('OFSP', 'Security.stx')},
        ) + Owned.manage_options + (
        {'label':'Interfaces',  'action':'manage_interfaces'},
	{'label':'Workflows',   'action':'manage_workflowsTab'},
    )

    manage_workflowsTab = PageTemplateFile('zpt/zmi_workflows', globals())

    def __str__(self):
        return self.__repr__()

    def status(self):
	"""
	return workflow status
	"""
	if not DO_PLONE:
	    raise NotImplementedError, 'Install Plone for workflow!'
	try:
            return getToolByName(self, 'portal_workflow').getInfoFor(self, 'review_state')
	except:
	    return ''

    def _status(self, status):
	"""
	set workflow status without calling workflow transition (use content_modify_status
	method if you want to do this ...
	"""
	if not DO_PLONE:
	    raise NotImplementedError, 'Install Plone for workflow!'
        wftool = getToolByName(self, 'portal_workflow')

	# TODO - figure out how to get the correct workflow ...
        try:
            wf = wftool.getWorkflowsFor(self)[0]
        except IndexError:
            raise WorkflowException, 'No Workflow found: %s' % self.absolute_url()

        if status not in wf.states.objectIds():
            raise WorkflowException, 'unknown state: %s' % status

        wftool.setStatusOf(wf.getId(), self, {'review_state':status})

    def actions(self):
        """
        return  a list of valid transitions for the object
        """
        return getToolByName(self, 'portal_actions').listFilteredActionsFor(self)['workflow']

    def chains(self):
	"""
	return workflow chains
	"""
	return getToolByName(self, 'portal_workflow').getWorkflowsFor(self)

    def manage_change_status(self, wfid, action, REQUEST=None):
	"""
	do a workflow transition from the ZMI
	"""
	wftool = getToolByName(self, 'portal_workflow')
        wftool.doActionFor(self, action, wfid)
	if REQUEST:
	    REQUEST.set('management_view', 'Workflows')
	    return self.manage_workflowsTab(self, REQUEST)

    def manage_download(self, REQUEST, RESPONSE):
        """
        convert the thing into a pdf and download it ...
        """
        # TODO - pass the (Plone) html thru a filter and render it as pdf ...
        pass

    def _csvHeader(self):
        """
        return a list of field names in the order they appear in the csv content
        """
        return self.propertyIds()

    def asCSVContent(self, REQUEST=None):
        """
        return a comma-separated view of the object, with fields returned in alphabetical
        order
        """
        return ','.join(map(lambda x: self.__dict__[x], self._csvHeader()))

    def asCSVHeader(self, REQUEST=None):
        """
        return a list of field names as they appear in the csv content
        """
        return ','.join(self._csvHeader())

    def as_xml(self, REQUEST=None):
        """
        """
        return "<%s>%s</%s>" % (self.meta_type,
                                self._xmlBody(),
                                self.meta_type)

    def _xmlBody(self):
        return '\n'.join(map(lambda x: '<%s type=%s>%s</%s>' % (x['id'],
                                                                x['type'],
                                                                self.getProperty(x['id'])),
                             self.propertyMap()))
        
AccessControl.class_init.InitializeClass(PortalContent)


class PortalFolder(PloneFolder, PortalContent):
    """
    Adding future potential to customise behaviour and formatting ...
    """
    meta_type = 'PortalFolder'
    _security = ClassSecurityInfo()
    __replaceable__ = REPLACEABLE
    icon = 'misc_/BastionLedger/folder'

    __ac_permissions__ = PloneFolder.__ac_permissions__ + (
	(view, ('SecurityCheckPermission', 'getSize',)),
	) + PortalContent.__ac_permissions__

    _properties = PortalContent._properties

    manage_options = (
        { 'label':'Contents', 'action':'manage_main',
          'help':('OFSP', 'ObjectManager_Contents.stx') },
        ) + PortalContent.manage_options

    _security.declarePublic('cb_dataValid')
    _security.declarePublic('dontAllowCopyAndPaste')
    def dontAllowCopyAndPaste(self): return 0

    def _checkId(self, id, allow_dups=1):
        """
        allow duplicates (in acquisition context) by default
        """
        return PloneFolder._checkId(self, id, allow_dups)

    #
    # the long term ambition is to customise this ...
    #
    manage_dtml = PloneFolder.manage_main
    manage_main = PageTemplateFile('zpt/view_main', globals())
    manage_importExportForm = PageTemplateFile('zpt/import_export', globals())

    def manage_exportObject(self, id='', download=None, toxml=None,
                            RESPONSE=None,REQUEST=None):
        """Exports an object to a file and returns that file."""
        download = 1
        return PloneFolder.manage_exportObject(self, id, download, toxml, RESPONSE, REQUEST)

    def manage_importObject(self, upload_file='', REQUEST=None, set_owner=1):
        """ import an object from a local file system """
        #
        # total overcopy ...
        #
        self._importObjectFromFile(upload_file, verify=1,
                                   set_owner=set_owner)
        
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, 
                manage_tabs_message='<em>%s</em> sucessfully imported' % id,
                title = 'Object imported',
                update_menu=1)

    def manage_repair(self, REQUEST=None):
        """
        Repair objects in folder ...
        """
        if getattr(aq_base(self), '_repair', None):
            self._repair()
        map(lambda x: x._repair(),
            filter(lambda x: getattr(x, '_repair', None), self.objectValues()))
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Repaired')
            return self.manage_main(self, REQUEST)
    #
    # this is a wrapper to format sizes for both Bastion and standard Zope objects
    # Bastion objects use getSize, and Zope get_size.  Bastion objects return a
    # formatted object as size is much more generic than byte size ...
    #
    def getSize(self, ob=None):
        # shite for QuotaFolder ...
        if ob == None: return 0
        if getattr(aq_base(ob), 'get_size', None):
            size = ob.get_size()
            if isinstance(ob, PortalContent):
                return size
            if size < 1024:
                return "1 Kb"
            elif size > 1048576:
                return "%0.02f Mb" % (size / 1048576)
            else:
                return "%0.02f Kb" % (size / 1024)
        else:
            return ""
            
    def SecurityCheckPermission(self, permission, object=None):
        """Check whether the security context allows the given permission on
        the given object.

        Arguments:
        
        permission -- A permission name
        
        object -- The object being accessed according to the permission
        """
        return (SecurityManagement.getSecurityManager().checkPermission(permission, object or self))

    def X__str__(self):
        """ this is massively useful for debugging ..."""
        return SimpleItem.__repr__(self)

    # screwed getToolByName dependency for non-plone-contained stuff ...
    _verifyObjectPaste = ObjectManager._verifyObjectPaste

    def manage_delObjects(self, ids=[], REQUEST=None):
        """
        Plone doesn't return a form!
        """
        ObjectManager.manage_delObjects(self, ids, REQUEST)
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _verifyObjectPaste(self, obj, validate_src=1):
        if self.expertMode():
            return True
        # stick a folder in there only to allow content to be added, but not pushing this
        # into FTI (and AT stuff doesn't have Product-registered ctors) ...
        if isinstance(obj, ATFolder):
            return True
        return ObjectManager._verifyObjectPaste(self, obj, validate_src)

    getIcon = PortalContent.getIcon

AccessControl.class_init.InitializeClass(PortalFolder)


class LargePortalFolder(BTreeFolder2, PloneFolder, PortalContent):
    """
    Adding future potential to customise behaviour and formatting ...
    """
    portal_type = 'Folder'

    __ac_permissions__ = BTreeFolder2.__ac_permissions__ +  PortalFolder.__ac_permissions__
    icon = 'misc_/BastionLedger/bfolder'

    # we want to drop off Find/Sync ...
    manage_options = (
        { 'label':'Contents', 'action':'manage_main',
          'help':('OFSP', 'ObjectManager_Contents.stx') },
        ) + PortalContent.manage_options

    _properties = PortalContent._properties
    
    def dontAllowCopyAndPaste(self): return 0
    isPrincipiaFolderish = 1
    property_extensible_schema__ = 1
    #
    # the long term ambition is to customise this ...
    #
    manage_dtml = BTreeFolder2.manage_main
    manage_main = PageTemplateFile('zpt/view_main', globals())
    manage_importExportForm = PageTemplateFile('zpt/import_export', globals())

    index_html = None  # This special value informs ZPublisher to use __call__

    def __init__(self, id, title=''):
        title = title
        # f**k Archetype Schemas ...
        BTreeFolder2.__init__(self, id)

    def _checkId(self, id, allow_dups=1):
        """
        allow duplicates (in acquisition context) by default
        """
        return BTreeFolder2._checkId(self, id, allow_dups)

    def manage_exportObject(self, id='', download=None, toxml=None,
                            RESPONSE=None,REQUEST=None):
        """Exports an object to a file and returns that file."""
        download = 1
        return BTreeFolder2.manage_exportObject(self, id, download, toxml, RESPONSE, REQUEST)

    def manage_importObject(self, upload_file='', REQUEST=None, set_owner=1):
        """ import an object from a local file system """
        #
        # total overcopy ...
        #
        self._importObjectFromFile(upload_file, verify=1,
                                   set_owner=set_owner)
        
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, 
                manage_tabs_message='<em>%s</em> sucessfully imported' % id,
                title = 'Object imported',
                update_menu=1)

    def manage_repair(self, REQUEST=None):
        """
        Repair objects in folder ...
        """
        if getattr(aq_base(self), '_repair', None):
            self._repair()
        map( lambda x: x._repair(),
             filter( lambda x: getattr(x, '_repair', None), self.objectValues()) )
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Repaired')
            return self.manage_main(self, REQUEST)

    def getSize(self, ob=None):
        # shite for QuotaFolder ...
        if ob == None: return 0
        if getattr(aq_base(ob), 'get_size', None):
            size = ob.get_size()
            if isinstance(ob, PortalContent):
                return size
            if size < 1024:
                return "1 Kb"
            elif size > 1048576:
                return "%0.02f Mb" % (size / 1048576)
            else:
                return "%0.02f Kb" % (size / 1024)
        else:
            return ""
    
    def SecurityCheckPermission(self, permission, object=None):
        """Check whether the security context allows the given permission on
        the given object.

        Arguments:
        
        permission -- A permission name
        
        object -- The object being accessed according to the permission
        """
        #print "LargePortalFolder::SecurityCheckPermission(%s, %s)" % (permission, object)
        return (SecurityManagement.getSecurityManager().checkPermission(permission, object or self))

    def __str__(self):
        return SimpleItem.__repr__(self)

    def asCSV(self, meta_type, REQUEST=None):
        """
        """
        return '\n'.join(map(lambda x: x.asCSV(),
                             self.objectValues(meta_type)))

    def as_xml(self, REQUEST):
        """
        """
        return '<%s>%s</%s>' % (self.meta_type,
                                self._xmlBody(),
                                self.meta_type)

    def _verifyObjectPaste(self, obj, validate_src=1):
        if self.expertMode():
            return 1
        return BTreeFolder2._verifyObjectPaste(self, obj, validate_src)

    getIcon = PloneFolder.getIcon

AccessControl.class_init.InitializeClass(LargePortalFolder)


class CalendarSupport:
    """
    i18n for local calendar views (as per plone.app.portlets.calendar)
    """
    display_calendar = PageTemplateFile('zpt/calendar_view', globals())

    def getPreviousMonth(self, month, year):
        """
        return the DateTime of the first of the  previous month
        """
        m = int(month)
        if m == 1:
            return DateTime('%i/12/01' % (int(year) - 1))  
        return DateTime('%s/%02i/01' % (year, m - 1))

    def getNextMonth(self, month, year):
        """
        return the DateTime of the first of the next month
        """
        m = int(month)
        if m == 12:
            return DateTime('%i/01/01' % (int(year) + 1))  
        return DateTime('%s/%02i/01' % (year, m + 1))

    def monthName(self, month):
        """
        return translated month name
        """
        ts = getToolByName(self, 'translation_service')
        return PLMF(ts.month_msgid(month), default=ts.month_english(month))

    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""
        weekdays = []
        ts = getToolByName(self, 'translation_service')
        calendar = getToolByName(self, 'portal_calendar')
        # list of ordered weekdays as numbers
        for day in calendar.getDayNumbers():
            weekdays.append(PLMF(ts.day_msgid(day, format='s'),
                                 default=ts.weekday_english(day, format='a')))
        return weekdays


#
# catalog-aware stuff should be able to call these
#
def catalogAdd(ob, event):
    # this may fail if we're copying to a system with different cataloging scheme
    try:
        ob.indexObject()
    except:
        pass

def catalogRemove(ob, event):
    try:
        ob.unindexObject()
    except:
        pass


# deprecated stuff needed for importing old ledgers
BObjectManager = PloneFolder
BObjectManagerTree = LargePortalFolder
