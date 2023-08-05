from tempfile import TemporaryFile

from ooopy.Transformer import Transformer
from ooopy import Transforms
from ooopy.OOoPy import OOoPy

from zope.interface import implements

from Products.PortalTransforms.interfaces import ITransform


class OdtTransform:
    """
    Odt templating transform.

    Input: odt model
    Output: rendered odt
    """

    implements(ITransform)

    __name__ = "odt_transform"
    inputs = ('application/vnd.oasis.opendocument.text', )
    output = "application/vnd.oasis.opendocument.text.transformed"

    def __init__(self, name=None, **kwargs):
        self.conf = kwargs

        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        with TemporaryFile() as temp_orig_data:
            temp_orig_data.write(orig)
            temp_orig_data.seek(0)
            with TemporaryFile() as temp_output_data:
                ooo = OOoPy(infile=temp_orig_data, outfile=temp_output_data)
                ooo_mimetype = ooo.mimetype
        
                ttt = Transformer(ooo_mimetype,
                                  Transforms.Field_Replace(replace=kwargs.get('mapper', {})),
                                 )
                ttt.transform(ooo)
                ooo.close()
                temp_output_data.seek(0)
                transformed_value = temp_output_data.read()

                data.setData(transformed_value)
        return data


def register():
    return OdtTransform()
