# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import adapts
from zope.interface import implements

from interfaces import IOpenIDAskUserInformation, IOpenIDAskedUserInformation


REQUIRE_KEY = 'openid-require'
OPTIONAL_KEY = 'openid-optional'

class AnnotatedAdapter(object):

    def __init__(self, request):
        self.context = request
        # following is ugly but request is not annotable
        if not hasattr(request, '__annotations__'):
            setattr(request, '__annotations__', dict())
        self.annotations = request.__annotations__

class AskOpenIDOnRequest(AnnotatedAdapter):

    implements(IOpenIDAskUserInformation)
    adapts(IBrowserRequest)

    def require(self, name):
        requires = self.annotations.get(REQUIRE_KEY, [])
        requires.append(name)
        self.annotations[REQUIRE_KEY] = requires

    def optional(self, name):
        optionals = self.annotations.get(OPTIONAL_KEY, [])
        optionals.append(name)
        self.annotations[OPTIONAL_KEY] = optionals


class AskedOpenIDOnRequest(AnnotatedAdapter):

    implements(IOpenIDAskedUserInformation)
    adapts(IBrowserRequest)

    def require(self):
        return self.annotations.get(REQUIRE_KEY, [])

    def optional(self):
        return self.annotations.get(OPTIONAL_KEY, [])


