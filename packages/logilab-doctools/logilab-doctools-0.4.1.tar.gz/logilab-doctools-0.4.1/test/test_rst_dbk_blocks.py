from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class BlocksTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_block_quote_simple(self):
        rst = u"""
Simple block quote test.

  This is a simple block quote.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple block quote test.</para><blockquote xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><para>This is a simple block quote.</para></blockquote>"""
        self.generic_test(rst, dbk)

    def test_block_quote_complex(self):
        rst = u"""
Complex block quote test.

  This is a block quote with a first paragraph.

  And then a second one!
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex block quote test.</para><blockquote xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><para>This is a block quote with a first paragraph.</para><para>And then a second one!</para></blockquote>"""
        self.generic_test(rst, dbk)

    def test_block_quote_attribution(self):
        rst = u"""
Block quote with attribution test.

  This is a block quote with an attribution.

  -- This is the attribution.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Block quote with attribution test.</para><blockquote xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><para>This is a block quote with an attribution.</para><attribution>This is the attribution.</attribution></blockquote>"""
        self.generic_test(rst, dbk)

    def test_doctest_block(self):
        rst = u"""
Doctest block test.

>>> print "This is a Doctest block."
>>> print "This is the same doctest block."
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Doctest block test.</para><programlisting xmlns:ldg="http://www.logilab.org/2005/DocGenerator">&gt;&gt;&gt; print "This is a Doctest block."\n&gt;&gt;&gt; print "This is the same doctest block."</programlisting>"""
        self.generic_test(rst, dbk)

    def test_literal_block(self):
        rst = u"""
Literal block test.

::

  first line   with   words
  second     line

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Literal block test.</para><programlisting xmlns:ldg="http://www.logilab.org/2005/DocGenerator">first line   with   words\nsecond     line</programlisting><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_sidebar_simple(self):
        rst = u"""
Simple sidebar test.

.. sidebar:: The title.

   This is the sidebar paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple sidebar test.</para><sidebar xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>The title.</title><para>This is the sidebar paragraph.</para></sidebar><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)


    def test_sidebar_complex(self):
        rst = u"""
Complex sidebar test.

.. sidebar:: The title.
   :subtitle: and its subtitle.

   This is the sidebar paragraph.

   This is a second paragraph in the sidebar.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex sidebar test.</para><sidebar xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><sidebarinfo><title>The title.</title><subtitle>and its subtitle.</subtitle></sidebarinfo><para>This is the sidebar paragraph.</para><para>This is a second paragraph in the sidebar.</para></sidebar><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_topic(self):
        rst = u"""
Topic test.

.. topic:: Topic title.

   This is the topic content (first paragraph).

   This is the topic content (second paragraph).

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Topic test.</para><sidebar xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Topic title.</title><para>This is the topic content (first paragraph).</para><para>This is the topic content (second paragraph).</para></sidebar><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_line_block_simple(self):
        rst = u"""
Simple line block test.

| This is a line block.
| This is a second     line in the same    line block.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple line block test.</para><literallayout xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a line block.\nThis is a second line in the same line block.\n</literallayout><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_line_block_complex(self):
        rst = u"""
Complex line block test.

| This is a **line block**\ .
| This is a second line in the same line block.
  This line is quite long and continues on several
  lines.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex line block test.</para><literallayout xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a <emphasis role="bold">line block</emphasis>.\nThis is a second line in the same line block. This line is quite long and continues on several lines.\n</literallayout><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_line_block_nested(self):
        rst = u"""
Nested line block test.

| This is a line block.
| This is a second line.
|     This is a third line.
|     This is a fourth line.
| This is a fifth line.
|     This is a sixth line.
|       This is a seventh line.
|     This is an eighth line.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Nested line block test.</para><literallayout xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a line block.\nThis is a second line.\n  This is a third line.\n  This is a fourth line.\nThis is a fifth line.\n  This is a sixth line.\n    This is a seventh line.\n  This is an eighth line.\n</literallayout><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_epigraph(self):
        rst = u"""
Epigraph test.

Section 1
---------

.. epigraph::

   This is an epigraph.

   This is a second paragraph in the epigraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Epigraph test.</para><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="section-1"><title>Section 1</title><epigraph><para>This is an epigraph.</para><para>This is a second paragraph in the epigraph.</para></epigraph><para>End of test.</para></section>"""
        self.generic_test(rst, dbk)

    def test_highlights(self):
        rst = u"""
Highlights test.

Section 1
---------

.. highlights::

   - this is the first point.

   - this is the second point.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Highlights test.</para><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="section-1"><title>Section 1</title><highlights><itemizedlist><listitem><para>this is the first point.</para></listitem><listitem><para>this is the second point.</para></listitem></itemizedlist></highlights><para>End of test.</para></section>"""
        self.generic_test(rst, dbk)

    def test_pull_quote(self):
        rst = u"""
Pull-quote test.

.. pull-quote::

   This is an important quote.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Pull-quote test.</para><blockquote xmlns:ldg="http://www.logilab.org/2005/DocGenerator" role="pull-quote"><para>This is an important quote.</para></blockquote><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)



if __name__ == '__main__':
    unittest_main()


