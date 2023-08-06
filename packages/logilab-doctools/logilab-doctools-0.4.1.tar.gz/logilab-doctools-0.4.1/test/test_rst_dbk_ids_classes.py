from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class IdsClassesTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_id(self):
        rst = u"""
Identifier test.

.. _id1:

This is a paragraph with an identifier.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Identifier test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="id1">This is a paragraph with an identifier.</para>"""
        self.generic_test(rst, dbk)

    def test_multiple_ids(self):
        rst = u"""
Multiple identifiers test.

.. _id1:
.. _id5:
.. _another-id:

This is a paragraph with several identifiers.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Multiple identifiers test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="another-id"><anchor id="id5"/><anchor id="id1"/>This is a paragraph with several identifiers.</para>"""
        self.generic_test(rst, dbk)

    def test_class(self):
        rst = u"""
Class test.

.. class:: class1

This is a paragraph with a class.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Class test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" role="class1">This is a paragraph with a class.</para>"""
        self.generic_test(rst, dbk)

    def test_multiple_classes(self):
        rst = u"""
Multiple classes test.

.. class:: class1 class2 another-class

This is a paragraph with several classes.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Multiple classes test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" role="class1" condition="class2 another-class">This is a paragraph with several classes.</para>"""
        self.generic_test(rst, dbk)

    def test_text_class(self):
        rst = u"""
Class on text test.

.. role:: class1

This is a paragraph with a :class1:`classified text`.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Class on text test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a <phrase role="class1">classified text</phrase>.</para>"""
        self.generic_test(rst, dbk)

    def test_strong_class(self):
        rst = u"""
Class on strong text test.

.. role:: class1(strong)

This is a paragraph with a :class1:`classified text in strong`.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Class on strong text test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a <emphasis role="bold" condition="class1">classified text in strong</emphasis>.</para>"""
        self.generic_test(rst, dbk)

    def test_pull_quote_class(self):
        rst = u"""
Class on pull-quote test.

.. class:: class1

.. pull-quote::

   This is an important classified quote.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Class on pull-quote test.</para><blockquote xmlns:ldg="http://www.logilab.org/2005/DocGenerator" role="pull-quote" condition="class1"><para>This is an important classified quote.</para></blockquote>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
