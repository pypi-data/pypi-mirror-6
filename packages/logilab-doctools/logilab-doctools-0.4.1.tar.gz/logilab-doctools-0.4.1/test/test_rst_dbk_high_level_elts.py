from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from logilab.doctools.rest_docbook.errors import DbkConversionError
from lxml.etree import tostring


class HighLevelElementsTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_one_chapter(self):
        rst = u"""
One chapter test.

.. class:: chapter

Chapter title
=============

This is a paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">One chapter test.</para><chapter xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="chapter-title"><title>Chapter title</title><para>This is a paragraph.</para></chapter>"""
        self.generic_test(rst, dbk)

    def test_two_chapters(self):
        rst = u"""
Two chapters test.

.. class:: chapter

Chapter title
=============

This is a paragraph.

.. class:: chapter

Another chapter title
=====================

This is a paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Two chapters test.</para><chapter xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="chapter-title"><title>Chapter title</title><para>This is a paragraph.</para></chapter><chapter xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="another-chapter-title"><title>Another chapter title</title><para>This is a paragraph.</para></chapter>"""
        self.generic_test(rst, dbk)

    def test_chapter_subsections(self):
        rst = u"""
Chapter with sub-sections test.

.. class:: chapter

Chapter title
=============

This is a paragraph.

Section 1 title
---------------

And another paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Chapter with sub-sections test.</para><chapter xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="chapter-title"><title>Chapter title</title><para>This is a paragraph.</para><section id="section-1-title"><title>Section 1 title</title><para>And another paragraph.</para></section></chapter>"""
        self.generic_test(rst, dbk)

    def test_appendix(self):
        rst = u"""
Appendix test.

.. class:: appendix

Appendix title
==============

This is a paragraph.

Section title
-------------

And another paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Appendix test.</para><appendix xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="appendix-title"><title>Appendix title</title><para>This is a paragraph.</para><section id="section-title"><title>Section title</title><para>And another paragraph.</para></section></appendix>"""
        self.generic_test(rst, dbk)

    def test_part(self):
        rst = u"""
Part test.

.. class:: part

Part title
==========

This is a paragraph.

Chapter title
-------------

A paragraph.

Section title
`````````````

And another paragraph.

.. class:: appendix

Appendix title
--------------

A paragraph.

Other section title
```````````````````

And another paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Part test.</para><part xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="part-title"><title>Part title</title><para>This is a paragraph.</para><chapter id="chapter-title"><title>Chapter title</title><para>A paragraph.</para><section id="section-title"><title>Section title</title><para>And another paragraph.</para></section></chapter><appendix id="appendix-title"><title>Appendix title</title><para>A paragraph.</para><section id="other-section-title"><title>Other section title</title><para>And another paragraph.</para></section></appendix></part>"""
        self.generic_test(rst, dbk)

    def test_article(self):
        rst = u"""
Article test.

.. class:: article

Article title
=============

This is a paragraph.

Section title
-------------

A paragraph.

.. class:: appendix

Appendix title
--------------

A paragraph.

Other section title
```````````````````

And another paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Article test.</para><article xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="article-title"><title>Article title</title><para>This is a paragraph.</para><section id="section-title"><title>Section title</title><para>A paragraph.</para></section><appendix id="appendix-title"><title>Appendix title</title><para>A paragraph.</para><section id="other-section-title"><title>Other section title</title><para>And another paragraph.</para></section></appendix></article>"""
        self.generic_test(rst, dbk)

    def test_book(self):
        rst = u"""
Book test.

.. class:: book

Book title
==========

This is a paragraph.

Chapter title
-------------

A paragraph.

Section title
`````````````

And another paragraph.

.. class:: appendix

Appendix title
--------------

A paragraph.

Other section title
```````````````````

And another paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Book test.</para><book xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="book-title"><title>Book title</title><para>This is a paragraph.</para><chapter id="chapter-title"><title>Chapter title</title><para>A paragraph.</para><section id="section-title"><title>Section title</title><para>And another paragraph.</para></section></chapter><appendix id="appendix-title"><title>Appendix title</title><para>A paragraph.</para><section id="other-section-title"><title>Other section title</title><para>And another paragraph.</para></section></appendix></book>"""
        self.generic_test(rst, dbk)

    def test_book_with_part(self):
        rst = u"""
Book with part test.

.. class:: book

Book title
==========

This is a paragraph.

Chapter title
-------------

A paragraph.

Section title
`````````````

And another paragraph.

.. class:: part

Part title
----------

A paragraph.

Other chapter title
```````````````````

A second paragraph.

Another section title
.....................

And another paragraph.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Book with part test.</para><book xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="book-title"><title>Book title</title><para>This is a paragraph.</para><chapter id="chapter-title"><title>Chapter title</title><para>A paragraph.</para><section id="section-title"><title>Section title</title><para>And another paragraph.</para></section></chapter><part id="part-title"><title>Part title</title><para>A paragraph.</para><chapter id="other-chapter-title"><title>Other chapter title</title><para>A second paragraph.</para><section id="another-section-title"><title>Another section title</title><para>And another paragraph.</para></section></chapter></part></book>"""
        self.generic_test(rst, dbk)

    def test_invalid_chapter_1(self):
        rst = u"""
Invalid chapter in section.

Section title
=============

.. class:: chapter

Chapter title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_chapter_2(self):
        rst = u"""
Invalid chapter in chapter.

.. class:: chapter

Chapter title
=============

.. class:: chapter

Chapter title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_chapter_3(self):
        rst = u"""
Invalid chapter in appendix.

.. class:: appendix

Appendix title
==============

.. class:: chapter

Chapter title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_chapter_4(self):
        rst = u"""
Invalid chapter in article.

.. class:: article

Article title
=============

.. class:: chapter

Chapter title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_appendix_1(self):
        rst = u"""
Invalid appendix in section.

Section title
=============

.. class:: appendix

Appendix title
--------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_appendix_2(self):
        rst = u"""
Invalid appendix in chapter.

.. class:: chapter

Chapter title
=============

.. class:: appendix

Appendix title
--------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_appendix_3(self):
        rst = u"""
Invalid appendix in appendix.

.. class:: appendix

Appendix title
==============

.. class:: appendix

Appendix title
--------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_part_1(self):
        rst = u"""
Invalid part in section.

Section title
=============

.. class:: part

Part title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_part_2(self):
        rst = u"""
Invalid part in chapter.

.. class:: chapter

Chapter title
=============

.. class:: part

Part title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_part_3(self):
        rst = u"""
Invalid part in appendix.

.. class:: appendix

Appendix title
==============

.. class:: part

Part title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_part_4(self):
        rst = u"""
Invalid part in part.

.. class:: part

part title
==========

.. class:: part

Part title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_part_5(self):
        rst = u"""
Invalid part in article.

.. class:: article

Article title
=============

.. class:: part

Part title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_article_1(self):
        rst = u"""
Invalid article in section.

Section title
=============

.. class:: article

Article title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_article_2(self):
        rst = u"""
Invalid article in chapter.

.. class:: chapter

Chapter title
=============

.. class:: article

Article title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_article_3(self):
        rst = u"""
Invalid article in appendix.

.. class:: appendix

Appendix title
==============

.. class:: article

Article title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_article_4(self):
        rst = u"""
Invalid article in part.

.. class:: part

part title
==========

.. class:: article

Article title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_article_5(self):
        rst = u"""
Invalid article in book.

.. class:: book

Book title
==========

.. class:: article

Article title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_article_6(self):
        rst = u"""
Invalid article in article.

.. class:: article

Article title
=============

.. class:: article

Article title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_book_1(self):
        rst = u"""
Invalid book in section.

Section title
=============

.. class:: book

Book title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_book_2(self):
        rst = u"""
Invalid book in chapter.

.. class:: chapter

Chapter title
=============

.. class:: book

Book title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_book_3(self):
        rst = u"""
Invalid book in appendix.

.. class:: appendix

Appendix title
==============

.. class:: book

Book title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_book_4(self):
        rst = u"""
Invalid book in part.

.. class:: part

part title
==========

.. class:: book

Book title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_book_5(self):
        rst = u"""
Invalid book in book.

.. class:: book

Book title
==========

.. class:: book

Book title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_book_6(self):
        rst = u"""
Invalid book in article.

.. class:: article

Article title
=============

.. class:: book

Book title
----------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_section_1(self):
        rst = u"""
Invalid section in part.

.. class:: part

part title
==========

.. class:: section

Section title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)

    def test_invalid_section_2(self):
        rst = u"""
Invalid section in book.

.. class:: book

Book title
==========

.. class:: section

Section title
-------------

This is a paragraph.
"""
        self.assertRaises(DbkConversionError, rest_dbk_transform, rst)


if __name__ == '__main__':
    unittest_main()
