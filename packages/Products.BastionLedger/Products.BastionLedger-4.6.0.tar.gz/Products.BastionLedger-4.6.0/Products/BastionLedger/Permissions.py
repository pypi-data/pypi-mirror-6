#
#    Copyright (C) 2002-2008  Corporation of Balclutha. All rights Reserved.
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

###############################################################################
#
# Permissions.py Permissions defined for use with the BastionLedger Product
#
###############################################################################
__doc__     = """ BastionLedger Permission definitions """
__version__ = '$Revision: 514 $'[11:-2]

#
# Note that *all* permissionable functions on these permissions *REQUIRE* authenticated
# login - this is both a Plone requirement and eminently sensible in that an audit
# trail is provided.
#
import AccessControl

# strongest permission to setup/close accounts etc etc
ManageBastionLedgers = 'BastionLedger: Manage'

# perform cancel/reject stuff
OverseeBastionLedgers = 'BastionLedger: Oversee'

# create invoices/accounts/transactions/orders
OperateBastionLedgers = 'BastionLedger: Operate'

AddBastionLedgers = 'BastionLedger: Add'

GodAccess = AccessControl.Permissions.change_configuration


def setDefaultRoles(permission, roles, object,acquire=1):
    registered = AccessControl.Permission._registeredPermissions
    if not registered.has_key(permission):
        registered[permission] = 1
        Products.__ac_permissions__=(
            Products.__ac_permissions__+((permission,(),roles),))
        mangled = AccessControl.Permission.pname(permission)
        setattr(Globals.ApplicationDefaultPermissions, mangled, roles)

    # Get the current roles with the given permission, so
    # that we don't overwrite them. We basically need to
    # merge the current roles with the new roles to be
    # assigned the given permission.
    current = object.rolesOfPermission(permission)
    roles = list(roles)
    for dict in current:
        if dict.get('selected'):
            roles.append(dict['name'])
    object.manage_permission(permission, roles, acquire)



