# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.tests import SilvaTestCase
from Products.Five import zcml

from Testing import ZopeTestCase as ztc


class OpenIDDependencyTestCase(SilvaTestCase.SilvaTestCase):
    """Test that if you try to use OpenID without the dependency
    installed in service extensions, you get an error.
    """

    def test_install(self):

        def install():
            root = self.getRoot()
            root.service_extensions.install('silva.pas.openid')

        self.assertRaises(AssertionError, install)


class OpenIDTestCase(SilvaTestCase.SilvaTestCase):
    """Test case for OpenID implementation.
    """

    def afterSetUp(self):
        """After set up, install the extension.
        """
        root = self.getRoot()
        root.service_extensions.install('silva.pas.base')
        root.service_extensions.install('silva.pas.openid')


    def test_00install(self):
        """Test install.
        """
        root = self.getRoot()

        # First the extension should be installed
        service_extensions = root.service_extensions
        self.failUnless(service_extensions.is_installed('silva.pas.base'))
        self.failUnless(service_extensions.is_installed('silva.pas.openid'))


    def test_99uninstall(self):
        """Test uninstall.
        """

        root = self.getRoot()
        root.service_extensions.uninstall('silva.pas.openid')

        # Should be uninstalled now
        service_extensions = root.service_extensions
        self.failIf(service_extensions.is_installed('silva.pas.openid'))

        # But we can reinstall it
        root.service_extensions.install('silva.pas.openid')
        self.failUnless(service_extensions.is_installed('silva.pas.openid'))


import unittest
def test_suite():

    # Load Five ZCML
    from Products import Five
    zcml.load_config('meta.zcml', Five)
    zcml.load_config('configure.zcml', Five)

    # Load our ZCML, which add the extension as a Product
    from silva.pas import openid
    zcml.load_config('configure.zcml', openid)

    # Load the Zope Product
    ztc.installProduct('GenericSetup')
    ztc.installProduct('PluginRegistry')
    ztc.installProduct('PluggableAuthService')
    ztc.installPackage('plone.session')
    ztc.installPackage('silva.pas.base')
    ztc.installPackage('silva.pas.membership')
    ztc.installPackage('silva.pas.openid')

    # Run tests
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OpenIDDependencyTestCase))
    suite.addTest(unittest.makeSuite(OpenIDTestCase))
    return suite
