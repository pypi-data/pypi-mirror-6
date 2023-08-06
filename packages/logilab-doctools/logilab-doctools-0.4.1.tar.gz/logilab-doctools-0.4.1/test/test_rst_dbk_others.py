from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class OthersTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_comment(self):
        rst = u"""
Comment test.

This is a paragraph.

.. this is a simple comment.

This is another paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Comment test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a paragraph.</para><!-- this is a simple comment. --><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is another paragraph.</para>"""
        self.generic_test(rst, dbk)

    def test_raw_docbook(self):
        rst = u"""
Raw DocBook test.

This is a classical paragraph.

.. raw:: DocBook

   <para>This paragraph is imported from raw data.</para>

   <para>So is this paragraph. This paragraph is much longer than the
   previous one.</para>
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Raw DocBook test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a classical paragraph.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This paragraph is imported from raw data.</para>\n\n<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">So is this paragraph. This paragraph is much longer than the\nprevious one.</para>"""
        self.generic_test(rst, dbk)

    def test_system_message(self):
        rst = u"""
System message test.

This is a classical paragraph. The following list contains an error.

- item 1 contains an error on
 second line.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">System message test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a classical paragraph. The following list contains an error.</para><itemizedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><listitem><para>item 1 contains an error on</para></listitem></itemizedlist><warning xmlns:ldg="http://www.logilab.org/2005/DocGenerator" role="system_message"><title>### WARNING on line 7</title><para>Bullet list ends without a blank line; unexpected unindent.</para></warning><blockquote xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><para>second line.</para></blockquote><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_problematic(self):
        rst = u"""
Problematic test.

This is a classical paragraph. The following paragraph contains an error.

This is a link to an `unknown target`_\ .

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Problematic test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a classical paragraph. The following paragraph contains an error.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a link to an <literal role="problematic" id="id2"><link linkend="id1">`unknown target`_</link></literal>.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para><section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" role="system-messages"><title>Docutils System Messages</title><warning role="system_message" id="id1"><title>### ERROR on line 6</title><para>Unknown target name: "unknown target".</para><para>See <link linkend="id2">this occurrence</link>.</para></warning></section>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
