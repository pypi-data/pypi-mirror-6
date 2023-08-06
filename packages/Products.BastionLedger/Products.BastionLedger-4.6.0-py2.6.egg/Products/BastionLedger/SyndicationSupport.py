#
# Copyright 2008-2013 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
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
from DateTime import DateTime
from Permissions import ManageBastionLedgers
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

#
# NOTE - this has *all* changed in Plone4.3!!
#
# We need to figure out custom queries - and the fact that portal_catalog
# is used for content search ...
#
from zope.interface import implements
from Products.CMFPlone.interfaces.syndication import ISyndicatable


class SyndicationSupport:
    """
    coordinates with portal_syndication to create RSS xml metadata

    this needs to find a catalog in the acquisition path with a searchObjects
    method, and it expects the catalog to have a meta_type (Field) and
    modified (Date) indexes

    Zope syndication is based upon View (anonymous) permission - we're however
    only syndicating to people with download permissions - this is enforced
    sneakily by only returning cataloged info if they're permitted ...

    It is also up to you to set an appropriate max objects in portal_syndication
    """
    implements(ISyndicatable)

    def isSyndicated(self):
        """
        """
        return self.site_settings.search_rss_enabled

    def synContentValues(self):
        """
        return all active Packages modified with the last day
        """
        return self.searchObjects(**self.syndicationQuery())

    def syndicationQuery(self):
        """
        overridable catalog query - should return a dict
        """
        raise NotImplementedError
