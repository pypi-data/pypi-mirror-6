from zope.component import getUtility

from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
from Products.PortalTransforms.interfaces import IPortalTransformsTool

from redomino.odttransforms.transforms import initialize
from redomino.odttransforms.mimetype import OdtTextTransformed


class SetupVarious:

    def __call__(self, context):

        # Ordinarily, GenericSetup handlers check for the existence of XML files.
        # Here, we are not parsing an XML file, but we use this text file as a 
        # flag to check that we actually meant for this import step to be run.
        # The file is found in profiles/default.

        if context.readDataFile('redomino.odttransforms.txt') is None:
            return

        # Add additional setup code here
        site = context.getSite()

        # setup mimetype registry
        self.setup_mimetype_registry(site)

        # setup transforms
        self.setup_transforms(site)

    def setup_mimetype_registry(self, site):
        mimetypes_registry = getUtility(IMimetypesRegistryTool)
        mimetypes_registry.register(OdtTextTransformed())

    def setup_transforms(self, site):
        portal_transforms = getUtility(IPortalTransformsTool)
        initialize(portal_transforms)

class Uninstall:

    def __call__(self, context):

        # Ordinarily, GenericSetup handlers check for the existence of XML files.
        # Here, we are not parsing an XML file, but we use this text file as a 
        # flag to check that we actually meant for this import step to be run.
        # The file is found in profiles/default.

        if context.readDataFile('redomino.odttransforms_uninstall.txt') is None:
            return

        # Add additional setup code here
        site = context.getSite()

        # uninstall transform
        self.uninstall_transforms(site)

        # uninstall mimetype
        self.uninstall_mimetype(site)

    def uninstall_mimetype(self, site):
        mimetypes_registry = getUtility(IMimetypesRegistryTool)
        mimetype_instance = mimetypes_registry.lookup('application/vnd.oasis.opendocument.text.transformed')
        if mimetype_instance:
            mimetypes_registry.unregister(mimetype_instance[0])

    def uninstall_transforms(self, site):
        portal_transforms = getUtility(IPortalTransformsTool)
        transform = 'odt_transform'
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
