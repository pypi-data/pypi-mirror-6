# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import alsoProvides, noLongerProvides

from Products.PluggableAuthService.interfaces import plugins
from silva.pas.base.interfaces import IPASService
from silva.pas.openid.interfaces import IOpenIDAware


def install(root, extension):
    """Installation method for OpenID support
    """
    assert IPASService.providedBy(root.service_members), \
        u"This extension requires silva.pas.base"

    # Register PAS plugins
    registerPASPlugins(root.acl_users)

    alsoProvides(root.service_members, IOpenIDAware)


def uninstall(root, extension):
    """Uninstall OpenID support
    """
    assert IPASService.providedBy(root.service_members), \
        u"This extension requires silva.pas.base"
    unregisterPASPlugins(root.acl_users)
    noLongerProvides(root.service_members, IOpenIDAware)


def is_installed(root, extension):
    return IOpenIDAware.providedBy(root.service_members)


def registerPASPlugins(pas):
    """Register new PAS plugins.
    """
    plugin_ids = pas.objectIds()
    assert 'cookie_auth' in plugin_ids, \
        'Acl user have not been created by silva.pas.base'
    if 'openid' not in plugin_ids:
        factory = pas.manage_addProduct['silva.pas.openid']
        factory.manage_addOpenIDPlugin('openid')
    if 'members' not in plugin_ids:
        factory = pas.manage_addProduct['silva.pas.membership']
        factory.manage_addMembershipPlugin('members')

    def registerPluginIfNew(ptype, pid):
        if pid not in pas.plugins.listPluginIds(ptype):
            pas.plugins.activatePlugin(ptype, pid)

    registerPluginIfNew(plugins.IExtractionPlugin, 'openid')
    registerPluginIfNew(plugins.IAuthenticationPlugin, 'openid')
    registerPluginIfNew(plugins.IUserEnumerationPlugin, 'members')
    registerPluginIfNew(plugins.ICredentialsUpdatePlugin, 'cookie_auth')
    # Change login form
    pas.cookie_auth.login_path = 'silva_login_form_with_openid.html'


def unregisterPASPlugins(pas):
    """Remove PAS plugins.
    """
    plugin_ids = pas.objectIds()
    assert 'cookie_auth' in plugin_ids, \
        'Acl user have not been created by silva.pas.base'
    if 'openid' not in plugin_ids:
        pas.manage_delObjects(['openid'])
    if 'members' not in plugin_ids:
        pas.manage_delObjects(['members'])

    pas.manage_delObjects(['openid', 'members',])
    # Restore login form to default one
    pas.cookie_auth.login_path = 'silva_login_form.html'


if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
