from tempfile import TemporaryFile
from tempfile import NamedTemporaryFile

from zope.interface import implements

from appy.pod.renderer import Renderer

from Products.PortalTransforms.interfaces import ITransform

from redomino.appytransforms.config import ODS_TRANSFORM_ID
from redomino.appytransforms.config import TRANSFORMED_SPREADSHEET_MIME


class OdsTransform:
    """
    Ods templating transform.

    Input: ods model
    Output: rendered ods
    """

    implements(ITransform)

    __name__ = ODS_TRANSFORM_ID
    inputs = ('application/vnd.oasis.opendocument.spreadsheet', )
    output = TRANSFORMED_SPREADSHEET_MIME

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
            # appy requires a result path file with .ods extension...
            # the result path should not exists and the overwriteExisting 
            # does not works as (I) expected, so here it is this horrible
            # workaround to get a valid file name temporary path
            # See how things should work: 
            # https://github.com/redomino/redomino.odttransforms/blob/master/redomino/odttransforms/transforms/odt_transforms.py
            with NamedTemporaryFile(suffix='.ods') as temp_output_data:
                output_path = temp_output_data.name
            renderer = Renderer(temp_orig_data, kwargs.get('mapper', {}), output_path)
            renderer.run()
            with open(output_path, 'rb') as temp_output_data:
                transformed_value = temp_output_data.read()

                data.setData(transformed_value)
        return data


def register():
    return OdsTransform()
