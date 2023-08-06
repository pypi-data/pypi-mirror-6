from logilab.common.testlib import TestCase, unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class AdmonitionsTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_admonition(self):
        rst = u"""
Admonition test.

.. admonition:: Admonition title

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Admonition test.</para><note xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Admonition title</title><para>This is an admonition paragraph.</para></note><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_attention(self):
        rst = u"""
Attention test.

.. attention::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Attention test.</para><important xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Attention!</title><para>This is an admonition paragraph.</para></important><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_caution(self):
        rst = u"""
Caution test.

.. caution::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Caution test.</para><caution xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Caution!</title><para>This is an admonition paragraph.</para></caution><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_danger(self):
        rst = u"""
Danger test.

.. danger::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Danger test.</para><warning xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>!DANGER!</title><para>This is an admonition paragraph.</para></warning><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_error(self):
        rst = u"""
Error test.

.. error::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Error test.</para><caution xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Error</title><para>This is an admonition paragraph.</para></caution><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_hint(self):
        rst = u"""
Hint test.

.. hint::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Hint test.</para><tip xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Hint</title><para>This is an admonition paragraph.</para></tip><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_important(self):
        rst = u"""
Important test.

.. important::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Important test.</para><important xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Important</title><para>This is an admonition paragraph.</para></important><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_note(self):
        rst = u"""
Note test.

.. note::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Note test.</para><note xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Note</title><para>This is an admonition paragraph.</para></note><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_tip(self):
        rst = u"""
Tip test.

.. tip::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Tip test.</para><tip xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Tip</title><para>This is an admonition paragraph.</para></tip><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_warning(self):
        rst = u"""
Warning test.

.. warning::

   This is an admonition paragraph.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Warning test.</para><warning xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>Warning</title><para>This is an admonition paragraph.</para></warning><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
