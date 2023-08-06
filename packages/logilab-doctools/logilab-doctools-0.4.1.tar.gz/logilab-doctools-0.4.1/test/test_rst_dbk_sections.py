from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class SectionsTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_one_section_simple(self):
        rst = u"""
Simple one section test.

Section 1 title
===============

This is a paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple one section test.</para><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="section-1-title"><title>Section 1 title</title><para>This is a paragraph.</para></section>"""
        self.generic_test(rst, dbk)

    def test_one_section_complex(self):
        rst = u"""
Complex one section test.

Section 1 title
===============

This is a paragraph.

This is another paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex one section test.</para><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="section-1-title"><title>Section 1 title</title><para>This is a paragraph.</para><para>This is another paragraph.</para></section>"""
        self.generic_test(rst, dbk)

    def test_two_sections(self):
        rst = u"""
Two sections test.

Section 1 title
===============

This is a paragraph.

This is another paragraph.

Section 1 title 2
=================

This is again a paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Two sections test.</para><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="section-1-title"><title>Section 1 title</title><para>This is a paragraph.</para><para>This is another paragraph.</para></section><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="section-1-title-2"><title>Section 1 title 2</title><para>This is again a paragraph.</para></section>"""
        self.generic_test(rst, dbk)

    def test_nested_sections(self):
        rst = u"""
Nested sections test.

Section 1 title
===============

This is a paragraph.

Section 2 title
---------------

This is a paragraph in the sub-section.

Section 2 title
---------------

This is a paragraph in the second sub-section.

Section 1 title 2
=================

This is again a paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Nested sections test.</para><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="section-1-title"><title>Section 1 title</title><para>This is a paragraph.</para><section id="section-2-title"><title>Section 2 title</title><para>This is a paragraph in the sub-section.</para></section><section id="id1"><title>Section 2 title</title><para>This is a paragraph in the second sub-section.</para></section></section><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="section-1-title-2"><title>Section 1 title 2</title><para>This is again a paragraph.</para></section>"""
        self.generic_test(rst, dbk)

    def test_rubric(self):
        rst = u"""
Rubric test.

.. rubric:: Rubric title

This is a paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Rubric test.</para><bridgehead xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Rubric title</bridgehead><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
