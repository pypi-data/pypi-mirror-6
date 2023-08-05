from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.OneTimeTokenPAS.config import PROJECTNAME, PLUGIN_ID

def install( portal ):
    out = StringIO()
    print >> out, "Installing %s:" % PROJECTNAME
    pas = getToolByName(portal, 'acl_users')
    registry = pas.plugins

    existing = pas.objectIds()
    if PLUGIN_ID not in existing:
        onetimetokenpas = pas.manage_addProduct[PROJECTNAME]
        onetimetokenpas.manage_addOneTimeTokenPlugin(PLUGIN_ID, 'One Time Token Plugin')
        print >> out, "Adding %s to PAS." % PLUGIN_ID
        activatePluginInterfaces(portal, PLUGIN_ID, out)

    # we want to be fully compatible with old Plone versions
    setuptool = getToolByName(portal, 'portal_setup')
    importcontext = 'profile-Products.%s:default' % PROJECTNAME
    if getattr(setuptool, 'runAllImportStepsFromProfile', None) is not None:
        # Plone 4+, maybe 3
        setuptool.runAllImportStepsFromProfile(importcontext)
    else:
        setuptool.setImportContext(importcontext)
        setuptool.runAllImportSteps()

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall( portal ):
    pas = getToolByName(portal, 'acl_users')
    existing = pas.objectIds()
    if PLUGIN_ID in existing:
        pas.manage_delObjects(PLUGIN_ID)


