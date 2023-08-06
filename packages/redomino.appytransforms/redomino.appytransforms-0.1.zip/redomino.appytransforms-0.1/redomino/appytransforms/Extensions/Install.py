from Products.CMFCore.utils import getToolByName

def uninstall(portal, reinstall=False):
    if not reinstall:
        portal_setup = getToolByName(portal, 'portal_setup')
        portal_setup.runAllImportStepsFromProfile('profile-redomino.appytransforms:uninstall')

