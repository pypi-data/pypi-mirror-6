# coding=utf-8
import unittest2 as unittest

from redomino.appytransforms.testing import REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING


class TestOdsTemplateTransform(unittest.TestCase):
    """ Quick and dirty tests about ods transforms """
    layer = REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING

    def test_input_file(self):
        """ We have an input file with a variable named plone_version """
        from zipfile import ZipFile
        import os
        with ZipFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input.ods'), 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertFalse('davide' in input_contents)
            self.assertFalse('coccorino' in input_contents)
            self.assertFalse('<text:p>32</text:p>' in input_contents)
            self.assertFalse('<text:p>unknown</text:p>' in input_contents)
            self.assertFalse('<text:p>Pippo</text:p>' in input_contents)


    def test_transform(self):
        """ We have an input file with a variable named plone_version """
        portal = self.layer['portal']
        import os
        file_contents = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input.ods')).read()
        pt = portal.portal_transforms
        persons = [{'name':'davide', 'age':32},
                   {'name':'coccorino', 'age':'unknown'},
                  ]
        converter = pt.convertTo(target_mimetype='application/vnd.oasis.opendocument.spreadsheet.transformed',
                                 orig=file_contents,
                                 mimetype='application/vnd.oasis.opendocument.spreadsheet',
                                 mapper=dict(persons=persons),
                                )
        data = converter.getData()
        from zipfile import ZipFile
        from StringIO import StringIO
        output_file = StringIO(data)
        with ZipFile(output_file, 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertTrue('davide' in input_contents)
            self.assertTrue('<text:p>32</text:p>' in input_contents)
            self.assertTrue('coccorino' in input_contents)
            self.assertTrue('<text:p>unknown</text:p>' in input_contents)

class TestOdsTemplateTransform2(unittest.TestCase):
    """ Quick and dirty tests about ods transforms """
    layer = REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING

    def test_input_file(self):
        """ We have an input file with a variable named plone_version """
        from zipfile import ZipFile
        import os
        with ZipFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input1.ods'), 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertFalse('<text:p>Pippo</text:p>' in input_contents)


    def test_transform(self):
        """ We have an input file with a variable named plone_version """
        portal = self.layer['portal']
        import os
        file_contents = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input1.ods')).read()
        pt = portal.portal_transforms
        name = 'Pippo'
        converter = pt.convertTo(target_mimetype='application/vnd.oasis.opendocument.spreadsheet.transformed',
                                 orig=file_contents,
                                 mimetype='application/vnd.oasis.opendocument.spreadsheet',
                                 mapper=dict(name=name),
                                )
        data = converter.getData()
        from zipfile import ZipFile
        from StringIO import StringIO
        output_file = StringIO(data)
        with ZipFile(output_file, 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertTrue('<text:p>Pippo</text:p>' in input_contents)

