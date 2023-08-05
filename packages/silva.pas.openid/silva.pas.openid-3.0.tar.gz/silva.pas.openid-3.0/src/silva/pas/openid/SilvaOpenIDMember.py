# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.component import getUtility

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import DateTime

from Products.Silva.SimpleMembership import SimpleMember
from Products.Silva.helpers import add_and_edit
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.pas.base.interfaces import IUserConverter
from interfaces import IOpenIDMember


class SilvaOpenIDMember(SimpleMember):
    grok.implements(IOpenIDMember)

    meta_type = 'Silva OpenID Member'
    security = ClassSecurityInfo()
    silvaconf.icon('www/member.png')
    silvaconf.factory('manage_addOpenIDMemberForm')
    silvaconf.factory('manage_addOpenIDMember')

    manage_options = ({'label': 'Details',
                       'action': 'manage_details',
                       },) + SimpleMember.manage_options

    def __init__(self, identity_url, id):
        super(SilvaOpenIDMember, self).__init__(id)
        self.identity_url = identity_url
        self.application_date = DateTime.DateTime()
        self.fully_registered = False
        self.last_login_date = None

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_details')
    manage_details = PageTemplateFile(
        "www/openIDMemberDetails", globals(),
        __name__='manage_details')

    manage_main = manage_details


InitializeClass(SilvaOpenIDMember)


manage_addOpenIDMemberForm = PageTemplateFile(
    "www/openIDMemberAdd", globals(),
    __name__='manage_addOpenIDMemberForm')


def manage_addOpenIDMember(self, identity_url, REQUEST=None):
    """Add a OpenID Member.
    """
    utility = getUtility(IUserConverter, name="openid")
    converter = utility()
    userid = converter.convert(identity_url)

    user = SilvaOpenIDMember(identity_url, userid)
    self._setObject(userid, user)
    user = getattr(self, userid)
    user.manage_addLocalRoles(id, ['ChiefEditor'])
    add_and_edit(self, userid, REQUEST)
    return ''
