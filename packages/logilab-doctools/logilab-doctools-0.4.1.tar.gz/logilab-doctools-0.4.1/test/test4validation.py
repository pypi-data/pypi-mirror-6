# -*- coding: utf-8 -*-
"""Validation tests for doctools

These tests are based on the specification document (see doc/spec_mkdoc.pdf)
"""
MKDOC = '../bin/mkdoc'
DEBUG = 0

from logilab.common.testlib import TestCase, unittest_main, SkipTest
import os, sys, shutil, tempfile


SAMPLEDOC = '''<?xml version="1.0" encoding="iso-8859-15"?>
<!DOCTYPE %(root_elt)s>
%(pi)s
<%(root_elt)s id="test" lang="fr">
<%(root_elt)sinfo>
<title>Test</title>
<subtitle>Gros test</subtitle>
<author><firstname>Alexandre</firstname><surname>FAYOLLE</surname></author>
<copyright><year>2003</year><holder>Logilab</holder></copyright>
</%(root_elt)sinfo>
<section><title>Présentation</title>
<para>Test des utilitaires mkdoc de <orgname>Logilab</orgname>.</para>
</section>
</%(root_elt)s>'''

SAMPLELETTRE = '''<?xml version="1.0" encoding="iso-8859-15"?>
<!DOCTYPE lettre>
%(pi)s
<lettre lang="fr" nos-ref="TEST" date="01 août 2012" lieu="Paris">
  <address role='to'>
    <othername>Destinataire</othername>
  </address>
  <address role="from">
    <firstname>Olivier</firstname>
    <surname>CAYROL</surname>
    <email>Olivier.Cayrol@logilab.fr</email>
    <phone>01.45.32.03.12</phone>
  </address>
  <para role="objet">Test de mkdoc</para>
  <section>
    <para>Ceci est un test.</para>
  </section>
</lettre>'''

SAMPLECONTRAT = '''<?xml version="1.0" encoding="iso-8859-15"?>
<!DOCTYPE contrat>
%(pi)s
<contrat ref="TEST" date="01 août 2012" lieu="Paris" nb-exempl="2" lang="fr">
<titre>Test</titre>
<contractant>
  <intro>
    <para>Première partie</para>
  </intro>
  <signature>
    <signataire>Robert Wald</signataire>
  </signature>
</contractant>
<contractant>
  <intro>
    <para>Deuxième partie</para>
  </intro>
  <signature>
    <signataire>Axel Herre</signataire>
  </signature>
</contractant>
<section role="article"><title>Premier article</title>
<para>Test des utilitaires mkdoc de <orgname>Logilab</orgname>.</para>
</section>
</contrat>'''

SAMPLECATA = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE book>
%(pi)s
<book lang="fr">
<bookinfo>
<title>Catalogue de Formations</title>
</bookinfo>
<preface>
<title>Introduction</title>
<para>Bonjour</para>
</preface>
<part><title>Première partie</title>
<training>
  <trainingcontent lang="fr">
    <traininginfo>
      <title>Formation 1</title>
      <shorttitle>Form 1</shorttitle>
      <reference>FORM-1</reference>
      <duration>
        <days>5 jours</days>
        <hours>35 heures</hours>
      </duration>
      <price>
        <inter>2&#xA0;100,00</inter>
        <onsite>10&#xA0;500,00</onsite>
      </price>
    </traininginfo>
    <objectives>
      <para>Ceci est un test.</para>
    </objectives>
    <audience>
      <para>Ceci est un test.</para>
    </audience>
    <prerequisites>
      <para>Ceci est un test.</para>
    </prerequisites>
    <customization>
      <para>Ceci est un test.</para>
    </customization>
    <terms>
      <para>Ceci est un test.</para>
    </terms>
    <thematic-content>
      <para>Ceci est un test.</para>
    </thematic-content>
    <program>
      <para>Ceci est un test.</para>
    </program>
  </trainingcontent>
</training>
</part>
</book>
'''

SAMPLEREST = '''.. class:: %(root_elt)s

Test ReST
=========

:Author: Sylvain Thénault
:Organization: Logilab
:Version: $Revision: 1.26 $
:Date: $Date: 2005-11-30 15:40:16 $
:Abstract:
    Test de la conversion avec du ReST

Test1
-----

Description
```````````
Des tests et du text à convertir. Convertit des fichiers au format ReST_ (Restructured Text) ou Docbook_ dans divers formats tels que html ou pdf.

.. _ReST: http://docutils.sourceforge.net/rst.html
.. _Docbook: http://www.docbook.org


Les substitutions avec des charactères non latin-1 sont également mises en |oe| uvre.

.. |oe| unicode:: &#x0153;
   :rtrim:

'''

SAMPLEFO = '''<?xml version="1.0" encoding="UTF-8"?>
 <root xmlns="http://www.w3.org/1999/XSL/Format" font-size="16pt">
  <layout-master-set>
    <simple-page-master
         margin-right="15mm" margin-left="15mm"
         margin-bottom="15mm" margin-top="15mm"
         page-width="210mm" page-height="297mm"
         master-name="bookpage">
      <region-body region-name="bookpage-body"
         margin-bottom="5mm" margin-top="5mm" />
    </simple-page-master>
  </layout-master-set>
  <page-sequence master-reference="bookpage">
    <title>Hello world example</title>
    <flow flow-name="bookpage-body">
      <block>Hello XSLFO!</block>
    </flow>
  </page-sequence>
 </root>'''


EXTENSIONS = {
    'pdf': 'pdf',
    'html': 'html',
    'docbook': 'xml',
    }


class TestMkdoc(TestCase):
    """Base class. Defines some helper functions and no tests"""
    EXTENSION = 'xml'
    TARGET = None
    def setUp(self):
        """initialize the name of the file to process and the name of the result"""
        fd, base = tempfile.mkstemp()
        self.filename = base+'.'+self.EXTENSION
        self.targetname = os.path.basename(base)+'.'+EXTENSIONS[self.TARGET]
        os.close(fd)

    def tearDown(self):
        """remove generated files"""
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.targetname):
            os.remove(self.targetname)

    def run_mkdoc(self, doc, style=None, **additional_options):
        f = open(self.filename,'w')
        f.write(doc)
        f.close()
        commandline = [MKDOC, '--target', self.TARGET, '--check', 'no']
        if not DEBUG:
            commandline.append('--quiet')
        if style:
            commandline.append('--stylesheet')
            commandline.append(style)
        for key, val in additional_options.items():
            commandline.append('--%s' % key)
            commandline.append(val)
        commandline.append(self.filename)
        if DEBUG:
            print '*'*80
            print ' '.join(commandline)
            print 'target', self.targetname
            sys.stdout.flush()
        status = os.spawnv(os.P_WAIT,MKDOC,  commandline)
        return status

    def make_doc(self, target, xslt, sample=SAMPLEDOC, root_elt=None):
        """default implementation for XML documents"""
        PI = '<?logidoc-style target="%s" xslt="%s"?>' % (target,xslt)
        doc = sample % {"pi":PI, "root_elt": (root_elt or 'article')}
        return doc


    def default_test(self,target=None,xslt=None, root_elt=None,
                     **additional_options):
        """The average default test.
        Tests that mkdoc runs fine and that a file is generated
        with some contents"""
        doc = self.make_doc(target, xslt, root_elt=root_elt)
        status = self.run_mkdoc(doc, xslt, **additional_options)
        self.failUnlessEqual(status,0)
        self.failUnless(os.path.isfile(self.targetname))
        self.failUnless(os.path.getsize(self.targetname)>0)


class Xml2Pdf(TestMkdoc):
    """Tests the XML to PDF conversions"""
    TARGET = 'pdf'

    def test_pdf_standard(self):
        self.default_test('pdf','standard', 'book')

    def test_pdf_standard(self):
        self.default_test('pdf','standard', 'book')

    def test_pdf_ao(self):
        self.default_test('pdf','reponse-ao', 'book')

    def test_pdf_admin(self):
        self.default_test('pdf','rapport-admin', 'article')

    def test_pdf_pubtech(self):
        self.default_test('pdf','publi-technique', 'book')

    def test_pdf_pubcom(self):
        self.default_test('pdf','publi-commerciale', 'article')

    def test_pdf_lettre(self):
        doc = self.make_doc(self.TARGET, 'lettre', sample=SAMPLELETTRE)
        status = self.run_mkdoc(doc)
        self.failUnlessEqual(status,0)
        self.failUnless(os.path.isfile(self.targetname))

    def test_pdf_contrat(self):
        doc = self.make_doc(self.TARGET, 'contrat', sample=SAMPLECONTRAT)
        status = self.run_mkdoc(doc)
        self.failUnlessEqual(status, 0)
        self.failUnless(os.path.isfile(self.targetname))

    def test_pdf_formation(self):
        doc = self.make_doc(self.TARGET, 'catalogue-formation', sample=SAMPLECATA)
        status = self.run_mkdoc(doc, 'catalogue-formation')
        self.failUnlessEqual(status,0)
        self.failUnless(os.path.isfile(self.targetname))
        self.failUnless(os.path.getsize(self.targetname)>0)


class Xml2Html(TestMkdoc):
    """Tests the XML to HTML conversions"""
    EXTENSION = 'dbk'
    TARGET = 'html'

    def tearDown(self):
        """remove generated files"""
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.targetname):
            os.remove(self.targetname)
        if os.path.exists('html'):
            shutil.rmtree('html')

    def multi_test(self,target=None,xslt=None, root_elt=None,
                     **additional_options):
        """The average default test.
        Tests that mkdoc runs fine and that a file is generated
        with some contents"""
        doc = self.make_doc(target, xslt, root_elt=root_elt)
        status = self.run_mkdoc(doc, xslt, **additional_options)
        self.failUnlessEqual(status,0)
        self.failUnless(os.path.isdir('html'))
        self.failUnless(os.path.isfile('html/index.html'))

    def test_html_standard(self):
        self.default_test('html','standard', 'book')

    def test_html_single(self):
        self.default_test('html','single-file', 'book')

    def test_html_multi(self):
        self.multi_test('html','multi-files', 'book')


class Rest2Html(Xml2Html):
    EXTENSION = 'rst'

    def make_doc(self, target, xslt, sample=None, root_elt=None):
        return SAMPLEREST % {"root_elt": (root_elt or 'article')}

    def test_html_website(self):
        pass


class Rest2Pdf(Xml2Pdf):
    EXTENSION = 'txt'

    def test_pdf_lettre(self):
        pass

    def test_pdf_contrat(self):
        pass

    def test_pdf_formation(self):
        pass

    def make_doc(self, target, xslt, sample=None, root_elt=None):
        return SAMPLEREST % {"root_elt": (root_elt or 'article')}


class Rest2Docbook(TestMkdoc):
    EXTENSION = 'rest'
    TARGET = 'docbook'
    def make_doc(self, target, xslt, sample=None, root_elt=None):
        return SAMPLEREST % {"root_elt": (root_elt or 'article')}

    def test_rest_to_docbook(self):
        self.default_test(root_elt='article')


class Fo2Pdf(TestMkdoc):
    EXTENSION = 'fo'
    TARGET = 'pdf'
    def make_doc(self, target, xslt, sample=None, root_elt=None):
        return SAMPLEFO

    def test_fo_to_pdf(self):
        self.default_test()


class Xml2PdfWithPreprocess(TestMkdoc):
    EXTENSION = 'xml'
    TARGET = 'pdf'
    def make_doc(self, target, xslt, sample=None, root_elt=None):
        """default implementation for XML documents"""
        PI = '<?logidoc-style target="%s" xslt="%s"?>'%(target,xslt)
        PI2 = '<?logidoc-preprocess xslt="session2prg-cours"?>'
        doc = SAMPLEDOC % {"pi": (PI+PI2), "root_elt": (root_elt or 'article')}
        return doc

    def test_pdf_admin(self):
        self.default_test('pdf','rapport-admin')


def ensure_mkdoc_executable():
    import stat
    mask = stat.S_IMODE(os.stat(MKDOC)[stat.ST_MODE])
    if not mask & 0111:
        try:
            os.chmod(MKDOC, mask|0111)
        except OSError:
            sys.exit('%s is not executable')

ensure_mkdoc_executable()


if __name__ == '__main__':
    unittest_main()
