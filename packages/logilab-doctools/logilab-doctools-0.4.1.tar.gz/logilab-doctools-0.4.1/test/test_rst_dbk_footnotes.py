from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class FootnotesTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_citation_simple(self):
        rst = u"""
Simple citation test.

This is a paragraph with a citation reference [CIT450]_

.. [CIT450] This is the citation content.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple citation test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a citation reference <footnote id="cit450" label="CIT450"><para>This is the citation content.</para></footnote></para>"""
        self.generic_test(rst, dbk)

    def test_citation_complex(self):
        rst = u"""
Complex citation test.

This is a paragraph with a citation reference\ [CIT78]_ at the heart of the
paragraph.

.. [CIT78] This is the citation content.

       This is another paragraph in the citation.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex citation test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a citation reference<footnote id="cit78" label="CIT78"><para>This is the citation content.</para><para>This is another paragraph in the citation.</para></footnote> at the heart of the paragraph.</para>"""
        self.generic_test(rst, dbk)

    def test_citation_multiple(self):
        rst = u"""
Multiple citation test.

This is a paragraph with a citation reference\ [CIT56]_\ .

This is another paragraph with another citation reference\ [CIT90]_\ .

.. [CIT90] This is the second citation content.

.. [CIT56] This is the first citation content.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Multiple citation test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a citation reference<footnote id="cit56" label="CIT56"><para>This is the first citation content.</para></footnote>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is another paragraph with another citation reference<footnote id="cit90" label="CIT90"><para>This is the second citation content.</para></footnote>.</para>"""
        self.generic_test(rst, dbk)

    def test_citation_multiref(self):
        rst = u"""
Multiple references citation test.

This is a paragraph with a citation reference\ [CIT450]_\ .

This is another paragraph with a reference\ [CIT450]_ to the same citation.

.. [CIT450] This is the citation content.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Multiple references citation test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a citation reference<footnote id="cit450" label="CIT450"><para>This is the citation content.</para></footnote>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is another paragraph with a reference<footnoteref id="id2" linkend="cit450" label="CIT450"/> to the same citation.</para>"""
        self.generic_test(rst, dbk)

    def test_footnote_simple(self):
        rst = u"""
Simple footnote test.

This is a paragraph with a footnote reference [#]_

.. [#] This is the footnote content.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple footnote test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a footnote reference <footnote id="id2"><para>This is the footnote content.</para></footnote></para>"""
        self.generic_test(rst, dbk)

    def test_footnote_symbolic(self):
        rst = u"""
Symbolic footnote test.

This is a paragraph with a footnote symbolic reference\ [*]_\ .

.. [*] This is the footnote content.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Symbolic footnote test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a footnote symbolic reference<footnote id="id2" label="*"><para>This is the footnote content.</para></footnote>.</para>"""
        self.generic_test(rst, dbk)

    def test_footnote_complex(self):
        rst = u"""
Complex footnote test.

This is a paragraph with a footnote reference\ [#]_ at the heart of the paragraph.

.. [#] This is the footnote content.

       This is another paragraph in the footnote.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex footnote test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a footnote reference<footnote id="id2"><para>This is the footnote content.</para><para>This is another paragraph in the footnote.</para></footnote> at the heart of the paragraph.</para>"""
        self.generic_test(rst, dbk)

    def test_footnote_multiple(self):
        rst = u"""
Multiple footnote test.

This is a paragraph with a footnote reference\ [#fn1]_\ .

This is another paragraph with another footnote reference\ [#fn2]_\ .

.. [#fn1] This is the first footnote content.

.. [#fn2] This is the second footnote content.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Multiple footnote test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a footnote reference<footnote id="fn1"><para>This is the first footnote content.</para></footnote>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is another paragraph with another footnote reference<footnote id="fn2"><para>This is the second footnote content.</para></footnote>.</para>"""
        self.generic_test(rst, dbk)

    def test_footnote_multiref(self):
        rst = u"""
Multiple references footnote test.

This is a paragraph with a footnote reference\ [#fn1]_\ .

This is another paragraph with a reference\ [#fn1]_ to the same footnote.

.. [#fn1] This is the footnote content.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Multiple references footnote test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a footnote reference<footnote id="fn1"><para>This is the footnote content.</para></footnote>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is another paragraph with a reference<footnoteref id="id2" linkend="fn1"/> to the same footnote.</para>"""
        self.generic_test(rst, dbk)

    def test_footnote_manual(self):
        rst = u"""
Manually numbered footnote test.

This is a paragraph with a footnote reference\ [6]_\ .

This is a paragraph with another footnote reference\ [5]_\ .

.. [5] This is the second footnote content.

.. [6] This is the first footnote content.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Manually numbered footnote test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a footnote reference<footnote id="id4" label="6"><para>This is the first footnote content.</para></footnote>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with another footnote reference<footnote id="id3" label="5"><para>This is the second footnote content.</para></footnote>.</para>"""
        self.generic_test(rst, dbk)

    def test_footnote_multiref_manual(self):
        rst = u"""
.. [5] This is the second footnote content.

.. [6] This is the first footnote content.

Multiple referenced manually numbered footnote test.

This is a paragraph with a footnote reference\ [6]_\ .

This is a paragraph with another footnote reference\ [5]_\ .

This is a paragraph with a reference\ [6]_ to the first footnote.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Multiple referenced manually numbered footnote test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a footnote reference<footnote id="id2" label="6"><para>This is the first footnote content.</para></footnote>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with another footnote reference<footnote id="id1" label="5"><para>This is the second footnote content.</para></footnote>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph with a reference<footnoteref id="id5" linkend="id2" label="6"/> to the first footnote.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
