#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages
import hmac
from datetime import date
from hashlib import sha1
from persistent import Persistent

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.authentication.interfaces import IAuthentication
from zope.container.contained import Contained
from zope.interface import implements, Interface
from zope.pluggableauth.factories import PrincipalInfo
from zope.pluggableauth.interfaces import ICredentialsPlugin, IAuthenticatorPlugin
from zope.pluggableauth.plugins.principalfolder import IInternalPrincipalContainer
from zope.publisher.interfaces.http import IHTTPRequest
from zope.schema import TextLine
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.utils.traversing import getParent

from ztfy.security import _


class TokenCredentialsUtility(Persistent, Contained):
    """Token credentials extraction utility"""

    implements(ICredentialsPlugin)

    loginfield = 'login'
    tokenfield = 'token'

    def extractCredentials(self, request):
        if not IHTTPRequest.providedBy(request):
            return None
        if not (request.get(self.loginfield) and request.get(self.tokenfield)):
            return None
        return {'login': request.get(self.loginfield),
                'token': request.get(self.tokenfield)}

    def challenge(self, request):
        return False

    def logout(self, request):
        return False


class ITokenAuthenticationUtility(Interface):
    """Token authentication utility interface"""

    encryption_key = TextLine(title=_("Encryption key"),
                              description=_("This key is used to encrypt login:password string "
                                            "with HMAC+SHA1 protocol"),
                              required=True)


class TokenAuthenticationUtility(Persistent, Contained):
    """Token authentication checker utility

    Be warned that authentication mechanism can only be checked against an
    InternalPrincipal using plain text password manager...
    """

    implements(ITokenAuthenticationUtility, IAuthenticatorPlugin)

    encryption_key = FieldProperty(ITokenAuthenticationUtility['encryption_key'])

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'token' in credentials):
            return None
        login = credentials['login']
        token = credentials['token']
        if not (login and token):
            return None
        utility = getParent(self, IAuthentication)
        if utility is None:
            return None
        for name, plugin in utility.getAuthenticatorPlugins():
            if not IInternalPrincipalContainer.providedBy(plugin):
                continue
            try:
                id = plugin.getIdByLogin(login)
                principal = plugin[login]
            except KeyError:
                continue
            else:
                source = '%s:%s:%s' % (principal.login,
                                       principal.password,
                                       date.today().strftime('%Y%m%d'))
                encoded = hmac.new(self.encryption_key.encode('utf-8'), source, sha1)
                if encoded.hexdigest() == token:
                    return PrincipalInfo(id, principal.login, principal.title, principal.description)

    def principalInfo(self, id):
        return None
