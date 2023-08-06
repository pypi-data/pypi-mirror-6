from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class ParasTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_para_simple(self):
        rst = u"""
Simple paragraph test.

This is a paragraph that extends on several lines.
That's to say, the paragraph will be written not on
one single line but on two or three, depending on
the width of the support where the paragraph is
written on.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple paragraph test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph that extends on several lines. That's to say, the paragraph will be written not on one single line but on two or three, depending on the width of the support where the paragraph is written on.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
