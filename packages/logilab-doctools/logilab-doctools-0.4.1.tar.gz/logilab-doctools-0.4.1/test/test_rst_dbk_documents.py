# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class DocumentsTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_simple_section_document(self):
        rst = u"""
Title
=====

This is a paragraph.

Section title
-------------

This is another paragraph.
"""
        dbk = u"""<section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="title"><sectioninfo><title>Title</title></sectioninfo><para>This is a paragraph.</para><section id="section-title"><title>Section title</title><para>This is another paragraph.</para></section></section>"""
        self.generic_test(rst, dbk)

    def test_simple_book_document(self):
        rst = u"""
.. class:: book

Title
=====

Chapter title
-------------

This is a paragraph.

Chapter 2 title
---------------

This is another paragraph.
"""
        dbk = u"""<book xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="title"><bookinfo><title>Title</title></bookinfo><chapter id="chapter-title"><title>Chapter title</title><para>This is a paragraph.</para></chapter><chapter id="chapter-2-title"><title>Chapter 2 title</title><para>This is another paragraph.</para></chapter></book>"""
        self.generic_test(rst, dbk)

    def test_simple_article_document(self):
        rst = u"""
.. class:: article

Title
=====

This is a paragraph.

Section title
-------------

This is another paragraph.
"""
        dbk = u"""<article xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="title"><articleinfo><title>Title</title></articleinfo><para>This is a paragraph.</para><section id="section-title"><title>Section title</title><para>This is another paragraph.</para></section></article>"""
        self.generic_test(rst, dbk)

    def test_complex_document(self):
        rst = u"""
Title
=====

Subtitle
--------

:revision: @hg-1234534

:author: Jean Dupond

:organization: LOGILAB

:address:
    104 boulevard Blanqui
    75013 PARIS
    http://www.logilab.fr/

:contact: contact@logilab.fr

:copyright: ⓒ by Logilab SA 2005-2012

:date: 2012-08-01

:version: Version 1.2

:status: published and sent to the client

:dedication:
    This document is dedicated to my boss that inspires me every day.

    Please don't forget me in the next pay raise.

:abstract:
    This document is just a test.

    It contains all the bibliographic elements one may find in ReST.

This is a paragraph.

Section title
`````````````

This is another paragraph.
"""
        dbk = u"""<section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="title"><sectioninfo><title>Title</title><subtitle id="subtitle">Subtitle</subtitle><edition>Version 1.2, @hg-1234534</edition><author><othername>Jean Dupond</othername></author><orgname>LOGILAB</orgname><address><otheraddress>104 boulevard Blanqui</otheraddress><otheraddress>75013 PARIS</otheraddress><otheraddress>http://www.logilab.fr/</otheraddress><email>contact@logilab.fr</email></address><legalnotice><para>&#9426; by Logilab SA 2005-2012</para></legalnotice><date>2012-08-01</date><releaseinfo>published and sent to the client</releaseinfo><dedication><para>This document is dedicated to my boss that inspires me every day.</para><para>Please don't forget me in the next pay raise.</para></dedication><abstract><para>This document is just a test.</para><para>It contains all the bibliographic elements one may find in ReST.</para></abstract></sectioninfo><para>This is a paragraph.</para><section id="section-title"><title>Section title</title><para>This is another paragraph.</para></section></section>"""
        self.generic_test(rst, dbk)

    def test_document_with_authors_list(self):
        rst = u"""
Title
=====

Subtitle
--------

:authors:
    * Jean Dupond
    * Pierre Durant
    * Robert Vald

This is a paragraph.

Section title
`````````````

This is another paragraph.
"""
        dbk = u"""<section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="title"><sectioninfo><title>Title</title><subtitle id="subtitle">Subtitle</subtitle><authorgroup><author><othername>Jean Dupond</othername></author><author><othername>Pierre Durant</othername></author><author><othername>Robert Vald</othername></author></authorgroup></sectioninfo><para>This is a paragraph.</para><section id="section-title"><title>Section title</title><para>This is another paragraph.</para></section></section>"""
        self.generic_test(rst, dbk)

    def test_document_with_authors_comma_list(self):
        rst = u"""
Title
=====

Subtitle
--------

:authors: Jean Dupond, Pierre Durant, Robert Vald

This is a paragraph.

Section title
`````````````

This is another paragraph.
"""
        dbk = u"""<section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="title"><sectioninfo><title>Title</title><subtitle id="subtitle">Subtitle</subtitle><authorgroup><author><othername>Jean Dupond</othername></author><author><othername>Pierre Durant</othername></author><author><othername>Robert Vald</othername></author></authorgroup></sectioninfo><para>This is a paragraph.</para><section id="section-title"><title>Section title</title><para>This is another paragraph.</para></section></section>"""
        self.generic_test(rst, dbk)

    def test_document_with_authors_semi_colon_list(self):
        rst = u"""
Title
=====

Subtitle
--------

:authors: Jean, Jacques Dupond; Pierre Durant; Robert Vald;

This is a paragraph.

Section title
`````````````

This is another paragraph.
"""
        dbk = u"""<section xmlns:ldg="http://www.logilab.org/2005/DocGenerator" id="title"><sectioninfo><title>Title</title><subtitle id="subtitle">Subtitle</subtitle><authorgroup><author><othername>Jean, Jacques Dupond</othername></author><author><othername>Pierre Durant</othername></author><author><othername>Robert Vald</othername></author></authorgroup></sectioninfo><para>This is a paragraph.</para><section id="section-title"><title>Section title</title><para>This is another paragraph.</para></section></section>"""
        self.generic_test(rst, dbk)

if __name__ == '__main__':
    unittest_main()
