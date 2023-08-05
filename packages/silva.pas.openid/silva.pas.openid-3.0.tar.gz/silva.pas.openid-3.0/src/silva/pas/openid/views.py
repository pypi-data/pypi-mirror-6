# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.component import getUtility
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.traversing.browser import absoluteURL

from silva.core.services.interfaces import IMemberService
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IHTTPResponseHeaders
from silva.pas.openid.interfaces import IOpenIDAskUserInformation
from silva.pas.openid.interfaces import ILoginPage, IRegisterPage
from silva.translations import translate as _

from zExceptions import BadRequest

from silva.fanstatic import need


class LoginPage(silvaviews.Page):
    grok.name('silva_login_form_with_openid.html')
    grok.require('zope2.Public')

    message = None
    action = None

    def update(self):
        need(ILoginPage)
        self.url = absoluteURL(self.context, self.request)
        if self.action is None:
            raise BadRequest()
        # Due how PAS monkey patch Zope, we need to do this by hand here.
        headers = queryMultiAdapter(
            (self.request, self),
            IHTTPResponseHeaders)
        if headers is not None:
            headers()


class RegisterPage(silvaviews.Page):
    grok.name('openid_register_new_user.html')
    grok.require('zope2.Public')

    def _process(self, captcha):
        self.feedback = None

        def get_form_value(key, default=None):
            return self.request.form.get(
                '__ac.field.identity.{0}'.format(key),
                default)

        if not get_form_value('do'):
            return
        identity = get_form_value('register', '').strip()
        if not identity:
            self.feedback = _(u"You need to provide an identity.")
            return
        verification = get_form_value('captcha', None)
        if verification is None:
            self.feedback = _(u"You need to fill the captcha.")
            return
        if not captcha.verify(verification):
            self.feedback = _(u"Error while validating the captcha.")
            return

        # Insert the URL under the name used by the PAS plugin in the
        # request to trigger the authentication when validating
        # credentials again.
        self.request.form['__ac.field.identity.url'] = identity

        root = self.context.get_root()
        service = getUtility(IMemberService)
        if not service.is_user(identity):
            # Create a member.
            members = root.Members
            factory = members.manage_addProduct['silva.pas.openid']
            factory.manage_addOpenIDMember(identity)
            # Ask information in order to fill-in member object.
            provider = IOpenIDAskUserInformation(self.request)
            provider.require('email')
            provider.optional('nickname')
            provider.optional('fullname')

        root.acl_users.validate(self.request)
        self.feedback = _(u'This URL is not a OpenID identity.')

    def update(self):
        need(IRegisterPage)
        captcha = getMultiAdapter((self.context, self.request), name='captcha')
        self._process(captcha)
        self.url = absoluteURL(self.context, self.request)
        self.captcha_img = captcha.image_tag()
        self.captcha_audio_url = captcha.audio_url()
