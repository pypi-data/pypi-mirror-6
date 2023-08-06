from zope.component import getUtility

from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
from Products.PortalTransforms.interfaces import IPortalTransformsTool

from redomino.appytransforms.transforms import initialize
from redomino.appytransforms.mimetype import OdtTextTransformed
from redomino.appytransforms.mimetype import OdsTextTransformed
from redomino.appytransforms.config import TRANSFORMED_MIMETYPES
from redomino.appytransforms.config import TRANSFORM_IDS


class SetupVarious:

    def __call__(self, context):

        # Ordinarily, GenericSetup handlers check for the existence of XML files.
        # Here, we are not parsing an XML file, but we use this text file as a 
        # flag to check that we actually meant for this import step to be run.
        # The file is found in profiles/default.

        if context.readDataFile('redomino.appytransforms.txt') is None:
            return

        # Add additional setup code here
        site = context.getSite()

        # setup mimetype registry
        self.setup_mimetype_registry(site)

        # setup transforms
        self.setup_transforms(site)

    def setup_mimetype_registry(self, site):
        mimetypes_registry = getUtility(IMimetypesRegistryTool)
        mimetypes = (OdtTextTransformed(), OdsTextTransformed())
        for mimetype in mimetypes:
            mimetypes_registry.register(mimetype)

    def setup_transforms(self, site):
        portal_transforms = getUtility(IPortalTransformsTool)
        initialize(portal_transforms)

class Uninstall:

    def __call__(self, context):

        # Ordinarily, GenericSetup handlers check for the existence of XML files.
        # Here, we are not parsing an XML file, but we use this text file as a 
        # flag to check that we actually meant for this import step to be run.
        # The file is found in profiles/default.

        if context.readDataFile('redomino.appytransforms_uninstall.txt') is None:
            return

        # Add additional setup code here
        site = context.getSite()

        # uninstall transform
        self.uninstall_transforms(site)

        # uninstall mimetype
        self.uninstall_mimetype(site)

    def uninstall_mimetype(self, site):
        mimetypes_registry = getUtility(IMimetypesRegistryTool)
        for mime in TRANSFORMED_MIMETYPES:
            mimetype_instance = mimetypes_registry.lookup(mime)
            if mimetype_instance:
                mimetypes_registry.unregister(mimetype_instance[0])

    def uninstall_transforms(self, site):
        portal_transforms = getUtility(IPortalTransformsTool)
        for transform in TRANSFORM_IDS:
            if hasattr(portal_transforms, transform):
                portal_transforms.unregisterTransform(transform)


def setupVarious(context):
    """ setup various step. Handles for steps not handled by a gs profile """
    handler = SetupVarious()
    handler(context)

def uninstall(context):
    """ Uninstall step """
    handler = Uninstall()
    handler(context)
