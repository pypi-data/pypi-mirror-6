#
#    Copyright (C) 2006-2012  Corporation of Balclutha. All rights Reserved.
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
import AccessControl, base64, random, re
from StringIO import StringIO
from Acquisition import aq_base
from AccessControl.Permissions import view_management_screens, delete_objects, \
     use_mailhost_services, access_contents_information
from OFS.Image import Image, File
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from BLBase import PortalContent, PortalFolder
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from utils import _mime_str, Message
from collective.quickupload.interfaces import IQuickUploadCapable
from zope.interface import implements

# this folder we stuff attachments in - needs to be *public* so the JS can traverse it ...
ATTACHMENTFOLDER_ID = 'attachments'

def rawData(blob):
    """
    get raw data out of a ZODB blob
    """
    data = blob.data
    if isinstance(data, str):
        return data

    p = StringIO()
    while data is not None:
        p.write(data.data)
        data = data.next
    return p.getvalue()

class AttachmentsFolder(PortalFolder):
    implements(IQuickUploadCapable)

class BLAttachmentSupport(PortalContent):
    """
    allow other extraneous supporting documentation to be attached to an object
    """
    implements(IQuickUploadCapable)

    __ac_permissions__ = PortalContent.__ac_permissions__ + (
        (access_contents_information, ('hasAttachments', 'attachmentValues', 'attachmentPayload',
                                       'attachmentsAsAttachments', 'attachmentJS', 'attachmentAsPdf',
                                       'attachmentUploaderId',)),
        (view_management_screens, ('manage_attachments',)),
        (delete_objects, ('manage_delAttachments',)),
        (ManageBastionLedgers, ('manage_repairAttachments',)),
        (OperateBastionLedgers, ('manage_addAttachment', 'manage_deleteAttachments',)),
        (use_mailhost_services, ('manage_emailAttachments',)),
        )

    manage_options = (
        {'label':'Attachments', 'action':'manage_attachments'},
        ) + PortalContent.manage_options

    manage_attachments = PageTemplateFile('zpt/attachments', globals())

    def manage_addAttachment(self, file, REQUEST=None):
        """
        """
        if not getattr(aq_base(self), ATTACHMENTFOLDER_ID, None):
            self.attachments = AttachmentsFolder(ATTACHMENTFOLDER_ID)

        filename = file.filename
        id = filename[max(filename.rfind('/'), filename.rfind('\\'), filename.rfind(':'),)+1:]

        # go figure out if it's an Image or a File ...
        obj = File(id, id, file)
        if obj.content_type.startswith('image'):
            obj = Image(id, id, file)

        getattr(self, ATTACHMENTFOLDER_ID)._setObject(id, obj)

        if REQUEST:
            REQUEST.set('management_view', 'Attachments')
            return self.manage_attachments(self, REQUEST)

    def manage_delAttachments(self, ids=[], REQUEST=None):
        """
        """
        try:
            getattr(self, ATTACHMENTFOLDER_ID).manage_delObjects(ids)
        except:
            pass
        if REQUEST:
            REQUEST.set('management_view', 'Attachments')
            return self.manage_attachments(self, REQUEST)

    def manage_emailAttachments(self, ids, email, REQUEST=None):
        """
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise

        subject = self.title_or_id()

        mailhost.send(_mime_str({'Subject':subject, 'From':self.email, 'To':email}, '',
                                map(lambda x: (x.getId(),x.getContentType(), x.data),
                                    filter(lambda x,ids=ids: x.getId() in ids,
                                           self.attachmentValues()))),
                      [email], self.email, subject)

        if REQUEST:
            REQUEST.set('management_view', 'Attachments')
            REQUEST.set('manage_tabs_message', 'Attachment(s) sent')
            return self.manage_attachments(self, REQUEST)
            
    def hasAttachments(self):
        """
        return whether or not attachments are present
        """
        return getattr(aq_base(self), ATTACHMENTFOLDER_ID, None) is not None and len(getattr(self, ATTACHMENTFOLDER_ID)) > 0

    def attachmentValues(self):
        """
        """
        if getattr(aq_base(self), ATTACHMENTFOLDER_ID, None):
            return getattr(self, ATTACHMENTFOLDER_ID).objectValues()
        return []

    def attachmentsAsAttachments(self):
        """
        return text-based attachment formatted with email headers and base64-encoded
        """
        results = []
        for attachment in self.attachmentValues():
            a = Message()
            content_type = attachment.getContentType()
            data = attachment.data

            if content_type.startswith('text') and isinstance(data, str):
                a.set_payload(data, charset='iso-8859-1')
            else:
                encoded = base64.b64encode(rawData(attachment))
                # break encoded data into 80 char chunks
                a.set_payload('\n'.join(map(lambda x: encoded[x*80:(x+1)*80],
                                            xrange((len(encoded)/80)+1))))
                a.add_header('Content-Transfer-Encoding', 'base64')

            # only assign content-type if it looks like a valid main-type/sub-type
            if content_type and content_type.find('/') != -1:
                a.set_type(content_type)

            a.add_header('Content-Disposition', 'attachment', filename="%s" % attachment.getId())
            results.append(a.as_string())

        return results

    def attachmentValue(self, id):
        """
        retrieve the attachment file (or None)
        """
        return getattr(self, ATTACHMENTFOLDER_ID)._getOb(id, None)

    def attachmentPayload(self, id):
        """
        the raw content of the attachment
        """
        a = self.attachmentValue(id)
        if a:
            return rawData(a)

    def attachmentAsPdf(self, id):
        """
        """
        a = self.attachmentValue(id)
        if a:
            ct = a.get_content_type()
            if ct.startswith('application/pdf'):
                return a
            elif ct.find('html') != -1:
                return self.html2pdf(self.attachmentPayload(id))
            else:
                raise TypeError, ct

        return None

    def attachmentJS(self, uploader_id):
        """
        the ajax widget 
        """
        if not getattr(aq_base(self), ATTACHMENTFOLDER_ID, None):
            setattr(self, ATTACHMENTFOLDER_ID, AttachmentsFolder(ATTACHMENTFOLDER_ID))
        raw = getattr(self, ATTACHMENTFOLDER_ID).unrestrictedTraverse('@@quick_upload_init')(for_id=uploader_id)
        return raw.replace('Browse', '<div class="context">Attach</div>')  # change button text TODO - i18n may f**k this ...

    def attachmentUploaderId(self):
        """
        a unique id for an attachment quick-upload
        """
        return 'uploader%s' %str(random.random()).replace('.','')

    def manage_repairAttachments(self, REQUEST=None):
        """
        migrate attachments to new format
        """
        attachments = getattr(aq_base(self), ATTACHMENTFOLDER_ID, None)
        if attachments:
            if not isinstance(attachments, AttachmentsFolder):
                content = self.attachmentValues()
                delattr(self, ATTACHMENTFOLDER_ID)
                setattr(self, ATTACHMENTFOLDER_ID, AttachmentsFolder(ATTACHMENTFOLDER_ID))
                attchments = getattr(self, ATTACHMENTFOLDER_ID)
                for k,v in content:
                    attachments._setObject(k,v)
                if REQUEST:
                    REQUEST.set('manage_tabs_message', 'Reset attachments')
                    return self.manage_main(self, REQUEST)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Nothing to do for attachments')
            return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(BLAttachmentSupport)
