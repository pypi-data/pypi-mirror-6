# -*- coding: utf-8 -*-
import re
import os

from Acquisition import aq_inner
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.permissions import ManagePortal
from AccessControl import Unauthorized

class LoginAs(BrowserView):
    """ Login as another user """

    template = ViewPageTemplateFile('login_as.pt')

    def __call__(self):
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

        # Hide the editable-object border
        self.request.set('disable_border', True)
        self.actions()
        return self.template()

    def actions(self):
        """Login the user"""
        context = aq_inner(self.context)
        # explicitly check permission on portal root. This browserview is registered for *
        portal = self.portal_state.portal()
        mtool = getToolByName(portal, 'portal_membership')
        if mtool.checkPermission(ManagePortal, portal):
            response = self.request.response
            if 'user' in self.request.keys():
                user = self.request['user']
                acl = getToolByName(context, 'acl_users')
                token_tool = getToolByName(context, 'onetimetoken_storage')
                token = token_tool.setToken(user)
                acl.resetCredentials(self.request, response)
                return response.redirect(self.portal_state.portal_url()+'?logincode='+token)
        else:
            raise Unauthorized()

