# coding=utf-8
import unittest2 as unittest

from redomino.odttransforms.testing import REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING


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
