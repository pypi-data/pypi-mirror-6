from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class ListsTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_bullet_list_simple(self):
        rst = u"""
Simple bullet list test.

This is a bullet list:

- first item,

- second item,

- third item that extends on several lines. That's to say,
  the item will be written not on one single line but on
  two or three, depending on the width of the support where
  the list is written on.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple bullet list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a bullet list:</para><itemizedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item that extends on several lines. That's to say, the item will be written not on one single line but on two or three, depending on the width of the support where the list is written on.</para></listitem></itemizedlist>"""
        self.generic_test(rst, dbk)

    def test_bullet_list_complex(self):
        rst = u"""
Complex bullet list test.

This is a bullet list:

- first item,

- second item,

- third item with one paragraph.

  And a second paragraph!

  And a third!

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex bullet list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a bullet list:</para><itemizedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item with one paragraph.</para><para>And a second paragraph!</para><para>And a third!</para></listitem></itemizedlist><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_enumerated_list_auto(self):
        rst = u"""
Enumerated auto-numbered list test.

This is an enumerated list:

#. first item,

#. second item,

#. third item.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Enumerated auto-numbered list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is an enumerated list:</para><orderedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator" numeration="arabic"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item.</para></listitem></orderedlist>"""
        self.generic_test(rst, dbk)

    def test_enumerated_list_arabic(self):
        rst = u"""
Enumerated arabic-numbered list test.

This is an enumerated list:

1. first item,

2. second item,

3. third item.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Enumerated arabic-numbered list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is an enumerated list:</para><orderedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator" numeration="arabic"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item.</para></listitem></orderedlist>"""
        self.generic_test(rst, dbk)

    def test_enumerated_list_arabic_starting_at_given_number(self):
        rst = u"""
Enumerated arabic-numbered list test.

This is an enumerated list starting at 5:

5. first item,

6. second item,

7. third item.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Enumerated arabic-numbered list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is an enumerated list starting at 5:</para><orderedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator" numeration="arabic" ldg:first-number="5"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item.</para></listitem></orderedlist>"""
        self.generic_test(rst, dbk)

    def test_enumerated_list_loweralpha(self):
        rst = u"""
Enumerated lower-alpha-numbered list test.

This is an enumerated list:

a) first item,

b) second item,

c) third item.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Enumerated lower-alpha-numbered list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is an enumerated list:</para><orderedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator" numeration="loweralpha"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item.</para></listitem></orderedlist>"""
        self.generic_test(rst, dbk)

    def test_enumerated_list_upperalpha(self):
        rst = u"""
Enumerated upper-alpha-numbered list test.

This is an enumerated list:

A. first item,

B. second item,

C. third item.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Enumerated upper-alpha-numbered list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is an enumerated list:</para><orderedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator" numeration="upperalpha"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item.</para></listitem></orderedlist>"""
        self.generic_test(rst, dbk)

    def test_enumerated_list_lowerroman(self):
        rst = u"""
Enumerated lower-roman-numbered list test.

This is an enumerated list:

i) first item,

ii) second item,

iii) third item.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Enumerated lower-roman-numbered list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is an enumerated list:</para><orderedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator" numeration="lowerroman"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item.</para></listitem></orderedlist>"""
        self.generic_test(rst, dbk)

    def test_enumerated_list_upperroman(self):
        rst = u"""
Enumerated upper-roman-numbered list test.

This is an enumerated list:

(IV) first item,

(V) second item,

(VI) third item.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Enumerated upper-roman-numbered list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is an enumerated list:</para><orderedlist xmlns:ldg="http://www.logilab.org/2005/DocGenerator" numeration="upperroman" ldg:first-number="4"><listitem><para>first item,</para></listitem><listitem><para>second item,</para></listitem><listitem><para>third item.</para></listitem></orderedlist>"""
        self.generic_test(rst, dbk)

    def test_definition_list_simple(self):
        rst = u"""
Simple definition list test.

This is a definition list:

term 1
  This is the definition,

term 2
  This is the definition,

term 3
  This is the definition.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple definition list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a definition list:</para><variablelist xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><varlistentry><term>term 1</term><listitem><para>This is the definition,</para></listitem></varlistentry><varlistentry><term>term 2</term><listitem><para>This is the definition,</para></listitem></varlistentry><varlistentry><term>term 3</term><listitem><para>This is the definition.</para></listitem></varlistentry></variablelist>"""
        self.generic_test(rst, dbk)

    def test_definition_list_complex(self):
        rst = u"""
Complex definition list test.

This is a definition list:

term 1
  This is the definition,

term 2
  This is a definition that uses several paragraphs.

  This is the second paragraph of the definition. This
  paragraph uses several lines, that is to say it is
  written not on a single line but on two or more lines,
  depending on the width of the support where the
  definition is written on.

term 3 : classif 1
  This is a term with a classifier.

term 4 : classif 1 : classif 2 : classif 3
  This is a term with several classifiers.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex definition list test.</para><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">This is a definition list:</para><variablelist xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><varlistentry><term>term 1</term><listitem><para>This is the definition,</para></listitem></varlistentry><varlistentry><term>term 2</term><listitem><para>This is a definition that uses several paragraphs.</para><para>This is the second paragraph of the definition. This paragraph uses several lines, that is to say it is written not on a single line but on two or more lines, depending on the width of the support where the definition is written on.</para></listitem></varlistentry><varlistentry><term>term 3 (<type>classif 1</type>)</term><listitem><para>This is a term with a classifier.</para></listitem></varlistentry><varlistentry><term>term 4 (<type>classif 1</type>, <type>classif 2</type>, <type>classif 3</type>)</term><listitem><para>This is a term with several classifiers.</para></listitem></varlistentry></variablelist>"""
        self.generic_test(rst, dbk)

    def test_option_list_simple(self):
        rst = u"""
Simple option list test.

-o    Option description 1.

--opt2    Option description 2.

/opt_three    Option description 3.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple option list test.</para><variablelist xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><varlistentry><term><option>-o</option></term><listitem><para>Option description 1.</para></listitem></varlistentry><varlistentry><term><option>--opt2</option></term><listitem><para>Option description 2.</para></listitem></varlistentry><varlistentry><term><option>/opt_three</option></term><listitem><para>Option description 3.</para></listitem></varlistentry></variablelist>"""
        self.generic_test(rst, dbk)

    def test_option_list_complex(self):
        rst = u"""
Complex option list test.

-o
   Option description 1, this is the first paragraph.

   This is the second paragraph that extends on multiple
   lines, that's to say it will be displayed not one single
   line but on several lines. The number of lines depends on
   the width of the support where the options list is written
   on.

--opt2, -2    Two options with the same description.

--opt3 VALUE    Option with an argument.

--opt4=VAL2    Option with another argument.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex option list test.</para><variablelist xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><varlistentry><term><option>-o</option></term><listitem><para>Option description 1, this is the first paragraph.</para><para>This is the second paragraph that extends on multiple lines, that's to say it will be displayed not one single line but on several lines. The number of lines depends on the width of the support where the options list is written on.</para></listitem></varlistentry><varlistentry><term><option>--opt2</option></term><term><option>-2</option></term><listitem><para>Two options with the same description.</para></listitem></varlistentry><varlistentry><term><option>--opt3</option><replaceable> VALUE</replaceable></term><listitem><para>Option with an argument.</para></listitem></varlistentry><varlistentry><term><option>--opt4</option><replaceable>=VAL2</replaceable></term><listitem><para>Option with another argument.</para></listitem></varlistentry></variablelist><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_field_list(self):
        rst = u"""
Field list test.

:Field1: This is the field description.

:Field2: This is the field description
    that continues on several lines, that's
    to say it will be displayed not one single
    line but on several lines. The exact number
    of lines depends on the width of the
    support where the field list is written.

:Field3: This a field description with several paragraphs.

         This is the second paragraph of the description.

         This is the third.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Field list test.</para><variablelist xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><varlistentry><term>Field1</term><listitem><para>This is the field description.</para></listitem></varlistentry><varlistentry><term>Field2</term><listitem><para>This is the field description that continues on several lines, that's to say it will be displayed not one single line but on several lines. The exact number of lines depends on the width of the support where the field list is written.</para></listitem></varlistentry><varlistentry><term>Field3</term><listitem><para>This a field description with several paragraphs.</para><para>This is the second paragraph of the description.</para><para>This is the third.</para></listitem></varlistentry></variablelist><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)


if __name__ == '__main__' :
    unittest_main()



