# -*- coding: utf-8 -*-
from . import unittest
from libcomxml.core import XmlField, XmlModel


class TestFields(unittest.TestCase):
    def setUp(self):
        self.field = XmlField('Quantity', '10000', attributes={'uom': 'euro'})

    def test_attributes(self):
        self.assertEqual(self.field.attributes, {'uom': 'euro'})
        self.assertEqual(self.field.element().items(), [('uom', 'euro')])

    def test_str(self):
        self.assertEqual(str(self.field),
                         '<Quantity uom="euro">10000</Quantity>')

    def test_value(self):
        self.assertEqual(self.field.element().text, '10000')