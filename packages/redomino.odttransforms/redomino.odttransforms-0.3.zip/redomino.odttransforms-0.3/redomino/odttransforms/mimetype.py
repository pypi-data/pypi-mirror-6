from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem


class OdtTextTransformed(MimeTypeItem):

    __name__ = "Odt text transformed"
    mimetypes = ('application/vnd.oasis.opendocument.text.transformed',)
    binary = 1
