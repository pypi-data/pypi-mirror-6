from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class TablesTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_table_simple(self):
        rst = u"""
Simple table test.

+-------+-------+-------+
| A1    | A2    | A3    |
+-------+-------+-------+
| B1    | B2    | B3    |
+-------+-------+-------+

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple table test.</para><informaltable xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><tgroup cols="3"><colspec colwidth="7*" colname="col0"/><colspec colwidth="7*" colname="col1"/><colspec colwidth="7*" colname="col2"/><tbody><row><entry>A1</entry><entry>A2</entry><entry>A3</entry></row><row><entry>B1</entry><entry>B2</entry><entry>B3</entry></row></tbody></tgroup></informaltable><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_table_complex(self):
        rst = u"""
Complex table test.

.. table:: This is the table title

   +-------+-------+---------------------+
   | A1    | A2    | A3                  |
   |       |       |                     |
   |       |       | This is the second  |
   |       |       | paragraph in the    |
   |       |       | table cell.         |
   +-------+-------+---------------------+
   | B1    | B2    | - this is a list    |
   |       |       |                     |
   |       |       | - with two items.   |
   +-------+-------+---------------------+

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex table test.</para><table xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>This is the table title</title><tgroup cols="3"><colspec colwidth="7*" colname="col0"/><colspec colwidth="7*" colname="col1"/><colspec colwidth="21*" colname="col2"/><tbody><row><entry>A1</entry><entry>A2</entry><entry><para>A3</para><para>This is the second paragraph in the table cell.</para></entry></row><row><entry>B1</entry><entry>B2</entry><entry><itemizedlist><listitem><para>this is a list</para></listitem><listitem><para>with two items.</para></listitem></itemizedlist></entry></row></tbody></tgroup></table><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_table_header(self):
        rst = u"""
Table with header test.

+-------+-------+-------+
| Ha1   | Ha2   | Ha3   |
+-------+-------+-------+
| Hb1   | Hb2   | Hb3   |
+=======+=======+=======+
| A1    | A2    | A3    |
+-------+-------+-------+
| B1    | B2    | B3    |
+-------+-------+-------+

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Table with header test.</para><informaltable xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><tgroup cols="3"><colspec colwidth="7*" colname="col0"/><colspec colwidth="7*" colname="col1"/><colspec colwidth="7*" colname="col2"/><thead><row><entry>Ha1</entry><entry>Ha2</entry><entry>Ha3</entry></row><row><entry>Hb1</entry><entry>Hb2</entry><entry>Hb3</entry></row></thead><tbody><row><entry>A1</entry><entry>A2</entry><entry>A3</entry></row><row><entry>B1</entry><entry>B2</entry><entry>B3</entry></row></tbody></tgroup></informaltable><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_table_simple_span(self):
        rst = u"""
Table with simple spans test.

+-------+-------+-------+
| A1    | A2/3          |
+-------+-------+-------+
| B1    | B/C2  | B3    |
+-------+       +-------+
| C1    |       | C3    |
+-------+-------+-------+

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Table with simple spans test.</para><informaltable xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><tgroup cols="3"><colspec colwidth="7*" colname="col0"/><colspec colwidth="7*" colname="col1"/><colspec colwidth="7*" colname="col2"/><tbody><row><entry>A1</entry><entry namest="col1" nameend="col2">A2/3</entry></row><row><entry>B1</entry><entry morerows="1">B/C2</entry><entry>B3</entry></row><row><entry>C1</entry><entry>C3</entry></row></tbody></tgroup></informaltable><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_table_complex_span(self):
        rst = u"""
Table with complex spans test.

+--------+--------+--------+--------+--------+--------+--------+
| A1     | A2/3/4                   | A/B5   | A6/7            |
+--------+--------+--------+--------+        +--------+--------+
| B/C1/2          | B3     | B4     |        | B6     | BCDE7  |
+                 +--------+--------+--------+--------+        +
|                 | C3     | C/D/E4/5        | C6     |        |
+--------+--------+--------+                 +--------+        +
| D1     | D2     | D3     |                 | D6     |        |
+--------+--------+--------+                 +--------+        +
| E1     | E2     | E3     |                 | E6     |        |
+--------+--------+--------+--------+--------+--------+--------+

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Table with complex spans test.</para><informaltable xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><tgroup cols="7"><colspec colwidth="8*" colname="col0"/><colspec colwidth="8*" colname="col1"/><colspec colwidth="8*" colname="col2"/><colspec colwidth="8*" colname="col3"/><colspec colwidth="8*" colname="col4"/><colspec colwidth="8*" colname="col5"/><colspec colwidth="8*" colname="col6"/><tbody><row><entry>A1</entry><entry namest="col1" nameend="col3">A2/3/4</entry><entry morerows="1">A/B5</entry><entry namest="col5" nameend="col6">A6/7</entry></row><row><entry morerows="1" namest="col0" nameend="col1">B/C1/2</entry><entry>B3</entry><entry>B4</entry><entry>B6</entry><entry morerows="3">BCDE7</entry></row><row><entry>C3</entry><entry morerows="2" namest="col3" nameend="col4">C/D/E4/5</entry><entry>C6</entry></row><row><entry>D1</entry><entry>D2</entry><entry>D3</entry><entry>D6</entry></row><row><entry>E1</entry><entry>E2</entry><entry>E3</entry><entry>E6</entry></row></tbody></tgroup></informaltable><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_table_light(self):
        rst = u"""
Light table test.

====== ====== ======
A1     A2     A3
====== ====== ======
B1     B2     B3
------ ------ ------
C1     C2     C3
====== ====== ======

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Light table test.</para><informaltable xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><tgroup cols="3"><colspec colwidth="6*" colname="col0"/><colspec colwidth="6*" colname="col1"/><colspec colwidth="6*" colname="col2"/><thead><row><entry>A1</entry><entry>A2</entry><entry>A3</entry></row></thead><tbody><row><entry>B1</entry><entry>B2</entry><entry>B3</entry></row><row><entry>C1</entry><entry>C2</entry><entry>C3</entry></row></tbody></tgroup></informaltable><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_table_csv(self):
        rst = u"""
CSV table test.

.. csv-table::
   :header: "Title", "A1", "A2", "A3"
   :stub-columns: 1

   "row1", "B1", "B2", "B3"
   "row2", "C1", "C2", "C3"

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">CSV table test.</para><informaltable xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><tgroup cols="4"><colspec colwidth="25*" ldg:bold="true" colname="col0"/><colspec colwidth="25*" colname="col1"/><colspec colwidth="25*" colname="col2"/><colspec colwidth="25*" colname="col3"/><thead><row><entry>Title</entry><entry>A1</entry><entry>A2</entry><entry>A3</entry></row></thead><tbody><row><entry>row1</entry><entry>B1</entry><entry>B2</entry><entry>B3</entry></row><row><entry>row2</entry><entry>C1</entry><entry>C2</entry><entry>C3</entry></row></tbody></tgroup></informaltable><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_table_list(self):
        rst = u"""
List table test.

.. list-table::
   :header-rows: 1

   * - A1
     - A2
     - A3
   * - B1
     - B2
     - B3
   * - C1
     - C2
     - C3

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">List table test.</para><informaltable xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><tgroup cols="3"><colspec colwidth="33*" colname="col0"/><colspec colwidth="33*" colname="col1"/><colspec colwidth="33*" colname="col2"/><thead><row><entry>A1</entry><entry>A2</entry><entry>A3</entry></row></thead><tbody><row><entry>B1</entry><entry>B2</entry><entry>B3</entry></row><row><entry>C1</entry><entry>C2</entry><entry>C3</entry></row></tbody></tgroup></informaltable><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__':
    unittest_main()
