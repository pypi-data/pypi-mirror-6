# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl.Permissions import manage_users as ManageUsers
from silva.core import conf as silvaconf

import install

silvaconf.extension_name("silva.pas.openid")
silvaconf.extension_title("Silva OpenID Support")
silvaconf.extension_depends(["Silva", 'silva.pas.base'])


def initialize(context):
    from .plugins import oid
    context.registerClass(oid.OpenIdPlugin,
                          permission=ManageUsers,
                          constructors=
                          (oid.manage_addOpenIDPluginForm,
                           oid.manage_addOpenIDPlugin),
                          visibility=None,
                          icon="www/openid.png")
