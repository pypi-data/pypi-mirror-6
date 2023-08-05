import sys

from urllib import quote, unquote
from Acquisition import aq_base
from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile

from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.plugins.CookieAuthHelper \
    import CookieAuthHelper as BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.authservice \
        import IPluggableAuthService
from Products.PluggableAuthService.interfaces.plugins import \
        IExtractionPlugin, IAuthenticationPlugin

from Products.CMFPlone.utils import log
from Products.OneTimeTokenPAS.config import *

# This hacked PlonePAS collection of plugins was mostly ripped
# from other plugins, especially from CookieAuthHelper

def manage_addOneTimeTokenPlugin (self, id, title='',
                                RESPONSE=None, **kw):
    """Create an instance of a one time token cookie helper.
    """

    self = self.this()

    o = OneTimeTokenPlugin(id, title, **kw)
    self._setObject(o.getId(), o)
    o = getattr(aq_base(self), id)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')

manage_addOneTimeTokenForm = DTMLFile("www/OneTimeTokenForm", globals())


class UsernameStorage:
    """Store the username in this object, so it can be stored in the session"""

    def _setUsername(self, username):
        self.__username = username

    def _getUsername(self):
        return self.__username


class OneTimeTokenPlugin(BasePlugin):
    """Multi-plugin which adds ability to override the updating of cookie via
    a setAuthCookie method/script.
    """

    _properties = ( { 'id'    : 'title'
                    , 'label' : 'Title'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    },
                  )

    meta_type = 'One Time Token Plugin'
    security = ClassSecurityInfo()

    session_var = '__ac'

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    security.declarePrivate( 'extractCredentials' )
    def extractCredentials( self, request ):

        """ Extract credentials from cookie or 'request'. """
        #log( 'extractCredentials')

        creds = {}
        session = request.SESSION
        username = None

        tokenTool = getToolByName(self, 'onetimetoken_storage')

        ob = session.get(self.session_var)
        if ob is not None and isinstance(ob, UsernameStorage):
            username = ob._getUsername()
            #log( "session username: %s" % username )
        
        if username is None: 
            loginCode = request.get('logincode')

            if not loginCode:
                return None # not authenticated

            try:
                username = tokenTool.verifyToken(loginCode)
            except:
                log( "Error, token tool refused token: %s" % sys.exc_info()[0] )

            if not username:
                return None # not authenticated

            #log( "token username: %s" % username )

            userstorage = UsernameStorage()
            userstorage._setUsername(username)
            session[self.session_var] = userstorage

        creds['remote_host'] = request.get('REMOTE_HOST', '')
        try:
            creds['remote_address'] = request.getClientAddr()
        except AttributeError:
            creds['remote_address'] = request.get('REMOTE_ADDR', '')


        creds['login'] = username

        # log( "returning username: %s" % username )

        return creds


    def authenticateCredentials(self, credentials):

        if credentials.has_key('extractor') and \
           credentials['extractor'] != self.getId():
            return (None, None)

        login = credentials.get('login')

        #log( "returning credentials: (%s, %s)" % (login, login) )

        return (login, login)


    security.declarePrivate('resetCredentials')
    def resetCredentials(self, request, response):
        """ Clears credentials"""
        session = self.REQUEST.SESSION
        session[self.session_var] = None

    


classImplements(OneTimeTokenPlugin,
                IExtractionPlugin,
                IAuthenticationPlugin,
               )

InitializeClass(OneTimeTokenPlugin)

