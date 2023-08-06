from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem

from redomino.appytransforms.config import TRANSFORMED_TEXT_MIME
from redomino.appytransforms.config import TRANSFORMED_SPREADSHEET_MIME


class OdtTextTransformed(MimeTypeItem):

    __name__ = "Odt text transformed"
    mimetypes = (TRANSFORMED_TEXT_MIME,)
    binary = 1


class OdsTextTransformed(MimeTypeItem):

    __name__ = "Ods text transformed"
    mimetypes = (TRANSFORMED_SPREADSHEET_MIME,)
    binary = 1
