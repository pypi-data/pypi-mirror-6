# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import urlparse

# Zope 2
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zExceptions import Redirect
import transaction
from zope.component import getUtility
from zope.component.event import objectEventNotify

# PAS
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin


# Silva
from silva.pas.openid.interfaces import *
from silva.pas.base.interfaces import IUserConverter
from silva.pas.openid.store import ZopeStore
from silva.pas.openid.events import *
from silva.core.views.interfaces import IVirtualSite

# OpenID
from openid.yadis.discover import DiscoveryFailure
from openid.consumer.consumer import Consumer, SUCCESS

# Python
import logging

manage_addOpenIDPluginForm = PageTemplateFile("../www/openIDAddForm",
                globals(), __name__="manage_addOpenIDPluginForm")

logger = logging.getLogger("PluggableAuthService")

def manage_addOpenIDPlugin(self, id, title='', REQUEST=None):
    """Add a OpenID plugin to a Pluggable Authentication Service.
    """
    plugin = OpenIdPlugin(id, title)
    self._setObject(plugin.getId(), plugin)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=OpenID+plugin+added." %
                self.absolute_url())


class OpenIdPlugin(BasePlugin):
    """OpenID authentication plugin.
    """

    meta_type = "OpenID plugin"
    security = ClassSecurityInfo()

    _properties = BasePlugin._properties + ({'id': 'policy_url',
                                             'type': 'string',
                                             'mode': 'w',
                                             'label': 'Policy URL',
                                             },)

    policy_url = ''

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title
        self.store = ZopeStore()

    def getConsumer(self):
        session=self.REQUEST["SESSION"]
        return Consumer(session, self.store)

    def extractOpenIdServerResponse(self, request, creds):
        """Process incoming redirect from an OpenId server.

        The redirect is detected by looking for the openid.mode
        form parameters. If it is found the creds parameter is
        cleared and filled with the found credentials.
        """

        mode = request.form.get("openid.mode", None)
        if mode == "id_res":
            # id_res means 'positive assertion' in OpenID, more commonly
            # describes as 'positive authentication'
            creds["openid.creds"] = request.form.copy()
        elif mode == "cancel":
            # cancel is a negative assertion in the OpenID protocol,
            # which means the user did not authorize correctly.
            objectEventNotify(OpenIDResultCancel(self, None, None))

    # IOpenIdExtractionPlugin implementation
    def initiateChallenge(self, request, identity_url, return_to=None):
        consumer = self.getConsumer()
        try:
            result = consumer.begin(identity_url)
        except DiscoveryFailure, e:
            logger.info("openid consumer discovery error for identity %s: %s",
                    identity_url, e[0])
            return
        except KeyError, e:
            logger.info("openid consumer error for identity %s: %s",
                    identity_url, e.why)
            pass

        site_url = IVirtualSite(request).get_top_level_url()
        site_parts = urlparse.urlparse(site_url)

        if return_to is None:
            return_to = request.form.get("__ac.field.origin", None)
            if return_to:
                # Complicated smash-up to build a full-url
                return_parts = urlparse.urlparse(return_to)
                result_parts = ()
                if not (return_parts[0] and return_parts[1]):
                    result_parts = result_parts + (
                        site_parts[0], site_parts[1])
                else:
                    result_parts = result_parts + (
                        return_parts[0], return_parts[1])
                result_parts = result_parts + (
                    return_parts[2], '', '', return_parts[5])
                return_to = urlparse.urlunparse(result_parts)
        if not return_to:
            return_to = site_url

        request["SESSION"]['return_to'] = return_to

        if self.policy_url:
            result.addExtensionArg('sreg', 'policy_url', self.policy_url)

        extra = IOpenIDAskedUserInformation(request)
        if extra.require():
            result.addExtensionArg('sreg',
                                   'required',
                                   ','.join(extra.require()))
        if extra.optional():
            result.addExtensionArg('sreg',
                                   'optional',
                                   ','.join(extra.optional()))

        url = result.redirectURL(site_url, return_to)

        # There is evilness here: we can not use a normal RESPONSE.redirect
        # since further processing of the request will happily overwrite
        # our redirect. So instead we raise a Redirect exception, However
        # raising an exception aborts all transactions, which means are
        # session changes are not stored. So we do a commit ourselves to
        # get things working.
        # XXX this also f**ks up ZopeTestCase
        transaction.commit()
        raise Redirect, url

    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        """This method performs the PAS credential extraction.

        It takes either the zope cookie and extracts openid credentials
        from it, or a redirect from a OpenID server.
        """
        creds = {}
        identity = request.form.get("__ac.field.identity.url", '').strip()
        if identity:
            self.initiateChallenge(request, identity)
            return creds

        self.extractOpenIdServerResponse(request, creds)
        return creds


    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        if not credentials.has_key("openid.creds"):
            return None
        real_creds = credentials["openid.creds"]
        if real_creds:
            consumer = self.getConsumer()
            result = consumer.complete(real_creds,
                                       self.REQUEST["SESSION"]['return_to'])
            userid = self._identityToId(result.identity_url)

            if result.status == SUCCESS:
                pas = self._getPAS()
                pas.updateCredentials(self.REQUEST,
                                      self.REQUEST.RESPONSE,
                                      userid,
                                      "")

                objectEventNotify(OpenIDResultSuccess(self, result, userid))
                return (userid, result.identity_url)
            else:
                logger.info("OpenId Authentication for %s failed: %s",
                            result.identity_url, result.message)
                objectEventNotify(OpenIDResultCancel(self, result, userid))

        return None

    def _identityToId(self, identity):
        utility = getUtility(IUserConverter, name="openid")
        converter = utility()
        return converter.convert(identity)


classImplements(OpenIdPlugin, IOpenIdExtractionPlugin, IAuthenticationPlugin)
registerMultiPlugin(OpenIdPlugin.meta_type)
