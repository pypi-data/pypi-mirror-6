# coding=utf-8
import unittest2 as unittest

from redomino.appytransforms.testing import REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING


class TestOdtTemplateTransform(unittest.TestCase):
    """ Quick and dirty tests about odt transforms """
    layer = REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING

    def test_input_file(self):
        """ We have an input file with a variable named plone_version """
        from zipfile import ZipFile
        import os
        with ZipFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input.odt'), 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertTrue('plone_version' in input_contents)
            self.assertFalse('4.3.2-sunny-day-beta' in input_contents)

    def test_transform(self):
        """ We have an input file with a variable named plone_version """
        portal = self.layer['portal']
        import os
        file_contents = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input.odt')).read()
        pt = portal.portal_transforms
        converter = pt.convertTo(target_mimetype='application/vnd.oasis.opendocument.text.transformed',
                                 orig=file_contents,
                                 mimetype='application/vnd.oasis.opendocument.text',
                                 mapper=dict(plone_version='4.3.2-sunny-day-beta'),
                                )
        data = converter.getData()
        from zipfile import ZipFile
        from StringIO import StringIO
        output_file = StringIO(data)
        with ZipFile(output_file, 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertTrue('plone_version' in input_contents)
            self.assertTrue('4.3.2-sunny-day-beta' in input_contents)

    def test_transform_list(self):
        """ We have an input file with a list """
        portal = self.layer['portal']
        import os
        file_contents = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input1.odt')).read()
        pt = portal.portal_transforms
        converter = pt.convertTo(target_mimetype='application/vnd.oasis.opendocument.text.transformed',
                                 orig=file_contents,
                                 mimetype='application/vnd.oasis.opendocument.text',
                                 mapper=dict(elements=['pippo', 'pluto', 'paperino']),
                                )
        data = converter.getData()
        from zipfile import ZipFile
        from StringIO import StringIO
        output_file = StringIO(data)
        with ZipFile(output_file, 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertTrue('pippo' in input_contents)
            self.assertTrue('pluto' in input_contents)
            self.assertTrue('paperino' in input_contents)

    def test_transform_conditional(self):
        """ We have an input file with a conditional text (with comments) """
        portal = self.layer['portal']
        import os
        file_contents = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input2.odt')).read()
        pt = portal.portal_transforms
        converter = pt.convertTo(target_mimetype='application/vnd.oasis.opendocument.text.transformed',
                                 orig=file_contents,
                                 mimetype='application/vnd.oasis.opendocument.text',
                                 mapper=dict(R35=5),
                                )
        data = converter.getData()
        from zipfile import ZipFile
        from StringIO import StringIO
        output_file = StringIO(data)
        with ZipFile(output_file, 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertTrue('Should appear' in input_contents)
            self.assertFalse('Should not appear' in input_contents)

    def test_transform_conditional2(self):
        """ We have an input file with a conditional field """
        portal = self.layer['portal']
        import os
        file_contents = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input3.odt')).read()
        pt = portal.portal_transforms
        converter = pt.convertTo(target_mimetype='application/vnd.oasis.opendocument.text.transformed',
                                 orig=file_contents,
                                 mimetype='application/vnd.oasis.opendocument.text',
                                 mapper=dict(name='davide'),
                                )
        data = converter.getData()
        from zipfile import ZipFile
        from StringIO import StringIO
        output_file = StringIO(data)
        with ZipFile(output_file, 'r') as myzip:
            input_contents = myzip.read('content.xml')
            self.assertTrue('I am davide' in input_contents)
            self.assertTrue('I am not coccorino, I am davide' in input_contents)
            self.assertFalse('I am not davide, I am coccoino' in input_contents)
            self.assertFalse('I am coccorino' in input_contents)
