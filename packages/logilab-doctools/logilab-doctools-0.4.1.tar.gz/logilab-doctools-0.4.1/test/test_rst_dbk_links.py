from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class LinksTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_url(self):
        rst = u"""
URL test.

This is a paragraph with an URL: http://www.logilab.fr/\ .
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">URL test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with an URL: <ulink url="http://www.logilab.fr/">http://www.logilab.fr/</ulink>.</para>"""
        self.generic_test(rst, dbk)

    def test_external_link(self):
        rst = u"""
External link test.

This is a paragraph with an external link_\ .

.. _link: http://www.logilab.fr/
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">External link test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with an external <ulink url="http://www.logilab.fr/">link</ulink>.</para>"""
        self.generic_test(rst, dbk)

    def test_external_anonymous_link(self):
        rst = u"""
External anonymous link test.

This is a paragraph with an `external anonymous link`__\ .

.. __: http://www.logilab.fr/
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">External anonymous link test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with an <ulink url="http://www.logilab.fr/">external anonymous link</ulink>.</para>"""
        self.generic_test(rst, dbk)

    def test_internal_link_simple(self):
        rst = u"""
Simple internal link test.

This is a paragraph with an internal link to this target_\ .

.. _target:

This is the target paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple internal link test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with an internal link to this <link linkend="target">target</link>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="target">This is the target paragraph.</para>"""
        self.generic_test(rst, dbk)

    def test_internal_link_complex(self):
        rst = u"""
Complex internal link test.

This is a paragraph with an internal link to this target_\ .

.. _target:
.. _target1:

This is the target paragraph with two target names.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex internal link test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with an internal link to this <link linkend="target">target</link>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="target1"><anchor id="target"/>This is the target paragraph with two target names.</para>"""
        self.generic_test(rst, dbk)

    def test_inline_target(self):
        rst = u"""
Inline target test.

This is a paragraph with an internal link to the following `inline target`_\ .

This is a paragraph with an _`inline target`\ .

"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Inline target test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with an internal link to the following <link linkend="inline-target">inline target</link>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with an <phrase id="inline-target">inline target</phrase>.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()


