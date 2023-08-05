========================
OpenID Support for Silva
========================

This extension provides full support for OpenID in Silva. It relies on
PluggableAuthService and ``silva.pas.base``.

After installing the extension, visitors will be able to login to Silva
using an OpenID identity. First, visitors will have to register their OpenID
via a form protected by a captcha. This registration step will fetch the
available information about the user from the OpenID provider and add it to
the Silva member object. After registration, site managers can assign roles
to the new users.

This extension requires at least `Silva`_ 3.x or higher. For previous
versions of Silva, please use previous versions of this extension.


Credits
=======

Silva's OpenID integration was sponsored by Marc Petitmermet, who's at the
Department of Materials at ETH Zurich (http://www.mat.ethz.ch/) but the
funding came from another source.


Code repository
===============

You can find the code of this extension in Git:
https://github.com/silvacms/silva.pas.openid


.. _Silva: http://silvacms.org

