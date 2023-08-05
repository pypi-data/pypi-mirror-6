from Products.PluggableAuthService import registerMultiPlugin
from plugins import onetimetoken_handler
from permissions import *

from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION
from Products.CMFPlone.interfaces import IPloneSiteRoot

registerMultiPlugin(onetimetoken_handler.OneTimeTokenPlugin.meta_type)

def initialize(context):
    """
    """

    context.registerClass(onetimetoken_handler.OneTimeTokenPlugin,
              permission = ManageUsers,
              constructors = (onetimetoken_handler.manage_addOneTimeTokenForm,
              onetimetoken_handler.manage_addOneTimeTokenPlugin),
              visibility = None)



