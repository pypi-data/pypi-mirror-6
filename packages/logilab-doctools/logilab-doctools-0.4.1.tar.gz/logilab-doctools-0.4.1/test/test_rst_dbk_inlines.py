from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class InlinesTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_emphasis(self):
        rst = u"""
Emphasis test.

This is a paragraph with *emphasis* text.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Emphasis test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with <emphasis>emphasis</emphasis> text.</para>"""
        self.generic_test(rst, dbk)

    def test_strong(self):
        rst = u"""
Strong test.

This is a paragraph with **bold** text.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Strong test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with <emphasis role="bold">bold</emphasis> text.</para>"""
        self.generic_test(rst, dbk)

    def test_abbreviation(self):
        ### FIXME: no test for abbreviation
        pass

    def test_acronym(self):
        rst = u"""
Acronym test.

This is a paragraph containing an acronym: :acronym:`ACR`.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Acronym test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph containing an acronym: <acronym>ACR</acronym>.</para>"""
        self.generic_test(rst, dbk)

    def test_literal(self):
        rst = u"""
Literal test.

This is a paragraph containing a ``literal  value`` that is displayed
differently from plain text.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Literal test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph containing a <literal>literal  value</literal> that is displayed differently from plain text.</para>"""
        self.generic_test(rst, dbk)

    def test_inline(self):
        rst = u"""
Inline test (defines a new role).

.. role:: custom

An example of using :custom:`text with specific role`.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Inline test (defines a new role).</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">An example of using <phrase role="custom">text with specific role</phrase>.</para>"""
        self.generic_test(rst, dbk)

    def test_title_reference(self):
        rst = u"""
Title reference test.

An example of `title reference` inside the text.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Title reference test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">An example of <citetitle>title reference</citetitle> inside the text.</para>"""
        self.generic_test(rst, dbk)

    def test_superscript(self):
        rst = u"""
Superscript test.

An example of :sup:`superscript` like in x\ :sup:`2`.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Superscript test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">An example of <superscript>superscript</superscript> like in x<superscript>2</superscript>.</para>"""
        self.generic_test(rst, dbk)

    def test_subscript(self):
        rst = u"""
Subscript test.

An example of :sub:`subscript` like in H\ :sub:`2`\ O.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Subscript test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">An example of <subscript>subscript</subscript> like in H<subscript>2</subscript>O.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
