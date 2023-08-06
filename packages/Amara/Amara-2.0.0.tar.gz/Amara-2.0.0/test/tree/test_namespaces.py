# -*- encoding: utf-8 -*-
# Testing new amara.tree API

# Testing namespaces
#See "Working with namespaces" section in http://wiki.xml3k.org/Amara2/Whatsnew

import cStringIO
import unittest

import amara
from amara.namespaces import *
from amara import tree, xml_print

TEST1 = '''<a:top xmlns:a="urn:bogus:a" xmlns:b="urn:bogus:b"><a:monty/></a:top>'''

NS_A = u"urn:bogus:a"
NS_B = u"urn:bogus:b"

class test_namespaces(unittest.TestCase):

    def test_namespace_fixup_from_scratch(self):
        '''Basic ns fixup upon mutation'''
        doc = tree.entity()
        elem = doc.xml_element_factory(NS_A, u'top')
        doc.xml_append(elem)
        self.assertEqual(doc.xml_first_child.xml_namespace, NS_A)
        return

    def test_namespace_fixup1(self):
        '''Basic ns fixup upon mutation by xml_namespace'''
        doc = amara.parse(TEST1)
        doc.xml_first_child.xml_namespace = NS_B
        #Side-effect is doc.monty.xml_prefix = u"b"
        self.assertEqual(doc.xml_first_child.xml_namespace, NS_B)
        self.assertEqual(doc.xml_first_child.xml_prefix, u'b')
        doc.xml_first_child.xml_first_child.xml_namespace = NS_B
        #Side-effect is doc.monty.xml_prefix = u"b"
        self.assertEqual(doc.xml_first_child.xml_first_child.xml_namespace, NS_B)
        self.assertEqual(doc.xml_first_child.xml_first_child.xml_prefix, u'b')
        #Make sure it didn't affect the top elem
        self.assertEqual(doc.xml_first_child.xml_namespace, NS_B)
        self.assertEqual(doc.xml_first_child.xml_prefix, u'b')
        return

    def test_namespace_fixup2(self):
        '''Basic ns fixup upon mutation by xml_prefix'''
        doc = amara.parse(TEST1)
        doc.xml_first_child.xml_prefix = u'b'
        #Side-effect is doc.monty.xml_namespace = NS_B
        self.assertEqual(doc.xml_first_child.xml_namespace, NS_B)
        self.assertEqual(doc.xml_first_child.xml_prefix, u'b')

        doc.xml_first_child.xml_first_child.xml_prefix = u'b'
        #Side-effect is doc.monty.xml_namespace = NS_B
        self.assertEqual(doc.xml_first_child.xml_first_child.xml_namespace, NS_B)
        self.assertEqual(doc.xml_first_child.xml_first_child.xml_prefix, u'b')
        #Make sure it didn't affect the top elem
        self.assertEqual(doc.xml_first_child.xml_namespace, NS_B)
        self.assertEqual(doc.xml_first_child.xml_prefix, u'b')
        return

    def test_auto_xml_namespace(self):
        '''Automatic recognition of XML namespace'''
        doc = amara.parse('<a/>')
        self.assertEqual(doc.xml_first_child.xml_namespaces[u'xml'], XML_NAMESPACE)
        doc.xml_first_child.xml_attributes[XML_NAMESPACE, u'xml:base'] = u'urn:bogus'
        self.assertEqual(doc.xml_first_child.xml_attributes[XML_NAMESPACE, u'xml:base'], u'urn:bogus')
        return


if __name__ == '__main__':
    raise SystemExit("use nosetests")
