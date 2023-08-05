from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

from Products.OneTimeTokenPAS.config import *


ptc.installProduct('OneTimeTokenPAS')
ptc.default_extensions_profiles = ('Products.OneTimeTokenPAS:default',)
ptc.setupPloneSite(products=['OneTimeTokenPAS'])


class TokenStorageTestCase(ptc.PloneTestCase):
    
    def afterSetUp(self):
        super(TokenStorageTestCase, self).afterSetUp()
        self.m_tool = getToolByName(self.portal, 'portal_membership')
        self.ott = getToolByName(self.portal, 'onetimetoken_storage')

    def get_generated_user(self):
        users = self.m_tool.acl_users.getUserIds()
        self.assertEqual(len(users), 2)
        return users[0]

    def test_temporary_user(self):
        # generate token
        token = self.ott.setToken()
        userid = self.get_generated_user()

        # verify token
        userid2 = self.ott.verifyToken(token)
        self.assertEqual(userid, userid2)

        # delete user
        self.ott.deleteTemporaryUser(userid)
        self.assertFalse(userid in self.m_tool.acl_users.getUserIds())

    def test_temporary_user_expire(self):
        # generate token
        token = self.ott.setToken()
        userid = self.get_generated_user()

        # expire tokens
        self.ott.clearExpired(-40)
        self.assertFalse(userid in self.m_tool.acl_users.getUserIds())
        
        # verify token
        self.assertRaises(TokenError, self.ott.verifyToken, token)

    def test_custom_username_function(self):
        username = '123456'
        # generate token
        token = self.ott.setToken(generate_username_callback=lambda: username)

        # verify token
        userid = self.ott.verifyToken(token)
        self.assertEqual(userid, username)

        # delete user
        self.ott.deleteTemporaryUser(username)
        self.assertFalse(username in self.m_tool.acl_users.getUserIds())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TokenStorageTestCase))
    return suite
