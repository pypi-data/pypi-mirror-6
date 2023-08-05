import socket
import time
import md5
import random
from base64 import urlsafe_b64encode as encodestring
from base64 import urlsafe_b64decode as decodestring

import persistent
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ManageUsers
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject

from Products.OneTimeTokenPAS.config import *


class TokenStorage(UniqueObject, SimpleItem, persistent.Persistent):
    isPrincipiaFolderish = True # Show up in the ZMI
    security = ClassSecurityInfo()
    meta_type = 'TokenStorage'
    id = 'onetimetoken_storage'

    _timedelta = 504 # three weeks

    def __init__(self):
        self._tokens = OOBTree()

    def getTokens(self):
        """ Return all usernames and dates without tokens, read only
        """
        return self._tokens.values()

    security.declareProtected(ManageUsers, 'setToken')
    def setToken(self, userId=None, generate_username_callback=None, generate_username_kwargs=None):
        """ Generate token for user or create one-time-user + token
        """
        token = ''
        m_tool = getToolByName(self, 'portal_membership')

        if not userId:
            if generate_username_callback:
                userId = generate_username_callback(**(generate_username_kwargs or {}))
            else:
                userId = self.uniqueString()
            done = m_tool.acl_users.source_users.doAddUser(userId, self.uniqueString())
            assert done, "User could not be created for OneTimeToken!"

        expiry = str(self.expirationDate())
        token = self.uniqueString()

        self._tokens[token] = (userId, expiry)
        login = "%s:%s" % (userId, token)

        # encode the login string to make it url safe
        token = encodestring(login)

        return token

    security.declarePublic('verifyToken')
    def verifyToken(self, loginCode):
        """
        """
        try:
            userId, token = decodestring(loginCode).split(':')
        except:
            raise TokenError('InvalidLoginCodeError')

        try:
            u, expiry = self._tokens[token]
        except KeyError:
            raise TokenError('InvalidTokenError')

        if self.expired(expiry):
            raise TokenError('ExpiredExpiryError')

        if not u == userId:
            raise TokenError('InvalidUserError')

        del self._tokens[token]

        return u

    security.declarePublic('deleteTemporaryUser')
    def deleteTemporaryUser(self, userId):
        """
        """
        m_tool = getToolByName(self, 'portal_membership')
        return m_tool.acl_users.source_users.doDeleteUser(userId)

    security.declarePrivate('uniqueString')
    def uniqueString(self):
        """Returns a string that is random and unguessable, or at
        least as close as possible."""
        # this is the informal UUID algorithm of
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/213761
        # by Carl Free Jr
        t = long( time.time() * 1000 )
        r = long( random.random()*100000000000000000L )
        try:
            a = socket.gethostbyname( socket.gethostname() )
        except:
            # if we can't get a network address, just imagine one
            a = random.random()*100000000000000000L
        data = str(t)+' '+str(r)+' '+str(a)#+' '+str(args)
        data = md5.md5(data).hexdigest()
        return str(data)

    security.declarePrivate('expirationDate')
    def expirationDate(self):
        """Returns a DateTime for exipiry of a request from the
        current time.

        This is used by housekeeping methods (like clearEpired)
        and stored in reset request records."""
        if not hasattr(self, '_timedelta'):
            self._timedelta = 168
        try:
            if isinstance(self._timedelta,datetime.timedelta):
                expire = datetime.datetime.utcnow() + self._timedelta
                return DateTime(expire.year,
                                expire.month,
                                expire.day,
                                expire.hour,
                                expire.minute,
                                expire.second,
                                'UTC')
        except NameError:
            pass  # that's okay, it must be a number of hours...
        expire = time.time() + self._timedelta*3600  # 60 min/hr * 60 sec/min
        return DateTime(expire)

    security.declarePrivate('expired')
    def expired(self, datetime, now=None):
        """Tells whether a DateTime or timestamp 'datetime' is expired
        with regards to either 'now', if provided, or the current
        time."""
        if not now:
            now = DateTime()
        return now.greaterThanEqualTo(datetime)

    security.declarePrivate('clearExpired')
    def clearExpired(self, days=0):
        """Destroys all expired reset request records.
        Parameter 'days' controls how many days past expired it must be to clear token.
        """
        for token, record in self._tokens.items():
            stored_user, expiry = record
            if self.expired(DateTime(expiry), DateTime()-days):
                del self._tokens[token]
                self.deleteTemporaryUser(stored_user)

InitializeClass(TokenStorage)
