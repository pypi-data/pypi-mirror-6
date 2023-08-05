# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from silva.pas.base.interfaces import IUserConverter

import urlparse

class OpenIDUserConverter(object):
    """ This let OpenID work, since getUserName and getUserId are
     called indifferently in Silva, but doesn't refere to the
     same data.
     """

    implements(IUserConverter)

    def match(self, userid):
        if not userid:
            return False
        ids = urlparse.urlparse(userid)
        if ids[1]:
            return True
        return False

    def convert(self, userid):
        if not userid:
            return userid
        ids = urlparse.urlparse(userid)
        real = ids[1]
        if len(ids[2]) > 1:
            real += '_' + str(ids[2][1:]).replace('/', '-')
        return real

