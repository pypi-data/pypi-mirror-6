# -*- coding: utf-8 -*-

from zope.interface import Invalid

from seantis.plonetools import tests
from seantis.plonetools import schemafields


class TestSchemafields(tests.IntegrationTestCase):

    def test_validate_email(self):
        schemafields.validate_email(u'test@example.org')
        schemafields.validate_email(u' test@example.org ')
        self.assertRaises(Invalid, schemafields.validate_email, u'asdf')
