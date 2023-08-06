#
#    Copyright (C) 2002-2013  Corporation of Balclutha. All rights Reserved.
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
import AccessControl, types

from utils import _mime_str

from Acquisition import aq_base
from DateTime import DateTime
from OFS.Image import File
from AccessControl.Permissions import view, view_management_screens, use_mailhost_services
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.standard import newline_to_br, html_quote
from bs4 import BeautifulSoup
from Permissions import *
from BLBase import *
from BLAccount import BLAccount

from interfaces.report import IReport
from zope.interface import implements

manage_addBLReportForm = PageTemplateFile('zpt/add_report', globals())
def manage_addBLReport(self, id, title='', effective=None, content='', REQUEST=None):
    """
    allow setting of a report 
    """
    # ZPT-based reports are Unicode, and we can't store these in Images ...
    if type(content) == types.UnicodeType:
        content = content.encode('ascii', 'ignore')
    self._setObject(id, BLReport(id, title, effective or DateTime(), content))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
                    
#class BLReport(PortalContent, File):
class BLReport(File, PortalContent):
    """
    An effective-dated report which is emailable and downloadable
    """
    implements(IReport)

    meta_type = portal_type = 'BLReport'

    charset_coding = 'iso-8859-1'
    tags = ()
    icon = 'misc_/BastionLedger/blreport'

    __ac_permissions__ = PortalContent.__ac_permissions__ + (
        (view, ('text','download')),
        (view_management_screens, ('manage_mail', 'manage_edit')),
        (use_mailhost_services, ('manage_sendmail',)),
        ) + File.__ac_permissions__

    _properties = File._properties + (
        {'id':'effective_date', 'type':'date',   'mode':'w'}, # Dublin Core attr
        {'id':'tags',           'type':'tokens', 'mode':'w'},
        )

    manage_options = (
        {'label':'Rendered',   'action':'manage_main' },
        {'label':'Distribute', 'action':'manage_mail' },
        {'label':'Edit',       'action':'manage_editForm' },
        ) + File.manage_options[1:] + (
        {'label':'Dublin Core', 'action':'manage_metadata'},
        )

    manage_main = PageTemplateFile('zpt/view_report', globals())
    manage_mail = PageTemplateFile('zpt/mail.zpt', globals())
    manage_editForm = File.manage_main

    def __init__(self, id, title, effective, content='', content_type='text/html', tags=[]):
        PortalContent.__init__(self, id, title)
        File.__init__(self, id, title, '', content_type)
        self.effective_date = effective
        if content:
            self.update_data(content, content_type, len(content))
        self.tags = tuple(tags)

    def text(self):
        """
        the function to extract the report once we fully Plonify the thing ...
        """
        # hmmm - this f**ks response headers
        #return File.index_html(self, self.REQUEST, self.REQUEST.RESPONSE)
        # let's hope it's not chunked ...
        return self.data
    
    def __cmp__(self, other):
        """
        sort entries on id within effective date (descending)
        """
        other_dt = other.effective()
        self_dt = self.effective()
        if self_dt < other_dt: return 1
        if self_dt > other_dt: return -1

        self_id = self.getId()
        other_id = other.getId()
        if self_id < other_id: return 1
        if self_id > other_id: return -1
        
        return 0

    def manage_sendmail(self, mfrom, mto, subject='', cc='',bcc='', message='',
                        format='plain', REQUEST=None):
        """
        send this report as an email attachment
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise

	recipients = []
	for field in (mto, bcc, cc):
	    if field:
		recipients.extend(map(str.strip, field.split(',')))

        mailhost.send(_mime_str({'Subject':subject,'From':mfrom, 'To':mto}, message,
                                [('%s.html' % self.getId(), self.content_type, self.data)],
                                format, self.charset_coding),
                      recipients, mfrom, subject)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Message Sent')
            return self.manage_main(self, REQUEST)

    def download(self, REQUEST, RESPONSE):
        """
        download report to local machine
        """
        RESPONSE.setHeader('Content-Type', 'text/html')
        RESPONSE.setHeader('Content-Disposition',
                           'inline; filename=%s.html' % self.getId())
        RESPONSE.write(self.text())

    def update_data(self, data, content_type=None, size=None):
        """
        prettily format any SGML befor saving
        """
        if content_type in ('text/html', 'text/xml'):
            # TODO - cannot store Unicode in File - bummer!!
            data = BeautifulSoup(data).prettify().encode('ascii', 'ignore')
        File.update_data(self, data, content_type, size)

    def asPDF(self, REQUEST, RESPONSE):
        """
        """
        format = self.content_type
        if format.find('html') != -1:
            data = self.text()
        elif format.find('structured') != -1:
            data = self.CookedBody(stx_level=2)
        elif format.find('plain'):
            data = newline_to_br(html_quote(self.text()))
        else:
            raise TypeError, 'unsupported content type: %s' % format

        RESPONSE.setHeader('Content-Type', 'application/pdf')
        RESPONSE.setHeader('Content-Disposition',
                           'inline; filename=%s.pdf' % self.getId())
        RESPONSE.write(self.aq_parent.html2pdf(data, encode=False))

    def accountId(self):
        if isinstance(self.aq_parent, BLAccount):
            return self.aq_parent.getId()
        return None

    def indexObject(self, idxs=[]):
        self.bastionLedger().catalog_object(self, '/'.join(self.getPhysicalPath()), idxs=idxs)

    def unindexObject(self):
        self.bastionLedger().catalog_object('/'.join(self.getPhysicalPath()))

AccessControl.class_init.InitializeClass(BLReport)


class BLReportFolder(LargePortalFolder):
    """
    A Report Folder - to retain end-user reports ...

    This maybe should grow to manage syndication etc
    """
    meta_type = portal_type = 'BLReportFolder'

    manage_options = (
        {'label':'contents', 'action':'manage_main',
         'help':('BastionLedger', 'reports.stx') },
        {'label':'view',     'action':''},
        ) + LargePortalFolder.manage_options[1:]
    
    dontAllowCopyAndPaste = 1

    def displayContentsTab(self): return False

    def all_meta_types(self):
        """ What can be put inside me? """
        return ( ProductsDictionary('BLReport'), )

    def objectValues(self, meta_types=None):
        """
        return descending date-sorted reports
        """
        objs = list(LargePortalFolder.objectValues(self, meta_types))
        objs.sort()
        return objs

    def manage_sendmail(self, ids, mfrom, mto, subject='', cc='',bcc='', message='',
                        format='plain', REQUEST=None):

        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise

	recipients = []
	for field in (mto, bcc, cc):
	    if field:
		recipients.extend(map(str.strip, field.split(',')))

        mailhost.send(_mime_str({'Subject':subject or '%s reports' % self.aq_parent.Title(),
                                 'From':mfrom, 
                                 'To':mto}, 
                                message,
                                map(lambda x: ('%s.html' % x.getId(), x.content_type, x.data),
                                    map(lambda x: self._getOb(x), ids)),
                                format, 'utf-8'),
                      recipients, mfrom, subject)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Report(s) sent to recipient(s)')
            return self.manage_main(self, REQUEST)
        
AccessControl.class_init.InitializeClass(BLReportFolder)
