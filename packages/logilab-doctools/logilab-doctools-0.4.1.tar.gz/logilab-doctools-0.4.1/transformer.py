# -*- coding: utf-8 -*-

# Copyright (c) 2000-2014 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

""" %prog [options] <input_file>

  Transform ReST / DOCBOOK XML to differents output formats

  In ReST documents, you can specify a DocBook component by adding a
  class on sections. For example:

      .. class:: book

      Section title
      =============
"""

import os
import sys
from os.path import isabs, join, exists, expanduser, splitext, basename
from commands import getstatusoutput
from lxml.etree import parse

from logilab.common.configuration import Configuration
from logilab.common.xmlutils import parse_pi_data

from logilab.doctools.__pkginfo__ import version

import warnings

REST_EXTENSIONS = ('.txt', '.rst', '.rest')
DOCBOOK_EXTENSIONS = ('.xml', '.dbk')
FO_EXTENSIONS = ('.fo',)
PYBILL_ROOTS = ('bill', 'claim-form', 'pro-forma', 'downpayment', 'debit',
             # Version 1.0:
             "{http://www.logilab.org/2010/PyBillDocument}accounting-document",)
TRAINING_SESSION_ROOTS = ('training-session')
STANDARD_XSLT_PATH = "/usr/share/sgml/logilab-xml/stylesheet/"

# XXX use ~/.config/mkdocrc or ~/.config/doctools/mkdocrc instead

if os.environ.has_key('MKDOCRC') and exists(os.environ['MKDOCRC']):
    MKDOCRC = os.environ['MKDOCRC']
else:
    USER_HOME = expanduser('~')
    if USER_HOME == '~':
        MKDOCRC = ".mkdocrc"
    else:
        MKDOCRC = join(USER_HOME, '.mkdocrc')
    if not exists(MKDOCRC):
        if exists('/etc/mkdocrc'):
            MKDOCRC = '/etc/mkdocrc'
        else:
            MKDOCRC = None

ENV_HELP = """
The following environment variables are used :
    * MKDOCRC
    path to the configuration file. If not found, it will use the first
existant file in ~/.mkdocrc, /etc/mkdocrc.
"""
if MKDOCRC:
    ENV_HELP += 'The current configuration file in use is %s.'% MKDOCRC
else:
    ENV_HELP += 'No configuration file has been found for this run.'

# exceptions ##################################################################

class FormattingException(Exception):
    """raised when a transformation failed"""

class GuessException(Exception):
    """raised when we are not able to guess something"""

class InputGuessException(GuessException):
    """raised when we are not able to guess the input file format"""

class OutputGuessException(GuessException):
    """raised when we are not able to guess the output file format"""

# utilities ###################################################################

def exec_cmd(cmd):
    """executed a command, check status and return output"""
    status, output = getstatusoutput(cmd)
    if status != 0:
        raise FormattingException('"%s" returned status %s\n%s' % (
            cmd, status, output))
    return output

def guess_format(filename):
    """guess file format according to its extension"""
    ext = splitext(filename)[1]
    if ext in REST_EXTENSIONS:
        return u'rest'
    if ext in DOCBOOK_EXTENSIONS:
        root_elt = parse(filename).getroot()
        if root_elt.tag in PYBILL_ROOTS:
            return u'pybill'
        if root_elt.tag in TRAINING_SESSION_ROOTS:
            return (u'training_session//%s'
                    % root_elt.findtext(u"reference", u""))
        return u'docbook'
    if ext in FO_EXTENSIONS:
        return u'fo'
    raise InputGuessException("Unable to guess file format from %s" % filename)

def xmlproc_output(output, checked):
    """parse xmlproc output and check for errors"""
    for line in output.strip().split('\n'):
        if line[0:2] == 'E:' or line[0:2] == 'W:' :
            print line
    j = line.find(" error(s)")
    assert j != -1
    i = line.rfind(" ", 0, j)
    err = line[i+1:j]
    if err != "0" :
        raise FormattingException('Not a %s xml file' % checked)


# the transformer #############################################################

class Transformer(Configuration):
    name = 'MAIN'
    options = (
        # main options
        ('target',
         {'type': 'choice',
          'choices': ('docbook', 'html', 'fo', 'pdf'),
          'default' : 'pdf',
          'metavar' : "<format>",
          'help': "output format. Available format are docbook (if input is a \
ReST file), html and pdf."
        }),
        ('source',
         {'type': 'choice',
          'choices': ('rest', 'docbook', 'fo'),
          'metavar' : "<format>",
          'help': "source format. Available format are rest, docbook, fo. If \
not specified, source format will be guessed from the file's extension."
        }),
        ('check',
         {'type' : 'yn',
          'metavar' : '<y_or_n>',
          'default' : 1,
          'help': "tell if we should check that the docbook input file is \
well formed xml."
          }),
        ('validate',
         {'type' : 'yn',
          'metavar' : '<y_or_n>',
          'default' : 0,
          'help': "tell if we should validate the docbook input file."
          }),
        ('preprocess',
         {'type': 'string',
          'action': 'append',
          'default': (),
          'metavar' : '<xslt>',
          'help': "add a pre-processing style sheet. You can set this option \
multiple times. If not specified, preprocessing."
          }),
        ('stylesheet',
         {'type': 'string',
          'metavar' : '<xslt>',
          'help': "set the main style sheet."
          }),
        ('ignore-pi',
         {'action': 'store_true',
          'dest': 'ignore_pi',
          'help': "Do not try to guess main/pre-process stylesheets from \
processing instruction."
          }),
        ('keep',
         {'action': 'store_true',
          'help': "Keep temporary files."
          }),
        ('quiet',
         {'action': 'store_true',
          'help': "Do not display information about what we're doing..."
          }),

        # FOP related options
        ('fop',
         {'type': 'string',
          'default' : 'fop',
          'metavar' : "<binpath>",
          'help': "path of the fop executable."
          }),
        ('fop-options',
         {'type': 'string',
          'dest' : 'fop_opts',
          'default' : '',
          'metavar' : "<options list>",
          'help': "options given to the fop executable."
          }),

        # xsltproc related options
        ('xsltproc',
         {'type': 'string',
          'default' : 'xsltproc',
          'metavar' : "<binpath>",
          'help': "path of the xsltproc executable."
          }),
        ('xsltproc-options',
         {'type': 'string',
          'dest' : 'xsltproc_opts',
          'default' : '--xinclude',
          'metavar' : "<options list>",
          'help': "options given to the xsltproc executable."
          }),
        ('param',
         {'type': 'named',
          'dest': 'parameters',
          'default': {},
          'metavar' : "<name>=<value>",
          'help': "sets the <name> stylesheet parameter to <value>. You may \
set multiple parameters separated by commas. Parameters are given to the xslt processor."
          }),
        # ReST related options
        ('doctype',
         {'type': 'string',
          'default' : None,
          'metavar' : "<doctype>",
          'help': "[DEPRECATED] doctype to use when converting ReST to DOCBOOK. Now, insert a class in the ReST source file."
          }),
        ('inputenc',
         {'type': 'string',
          'default' : None,
          'metavar' : "<encoding>",
          'help': "input encoding to use when converting ReST to DOCBOOK."
          }),
        ('lang',
         {'type': 'string',
          'default' : 'fr',
          'metavar' : "<language_code>",
          'help': "code of the language used in the document (useful for generatting text)."
          }),


        ## FIXME Path to xslt directory has not to be specified.
        ## TODO : Remove all references to xslt root and use id in catalog
        # xslts location
        ('xsltroot',
         {'type': 'string',
          'metavar' : "<xslt directory>",
          'default' : None,
          'help': "directory where logilab's stylesheets are located."
          }),
        )

    def __init__(self):
        Configuration.__init__(self, usage=__doc__, version=version,
                               config_file=MKDOCRC)
        self.add_help_section('Environment variables', ENV_HELP)

    def xslt_transform(self, input_file, output_file, xslt_file):
        """xsltproc based transformation
        """
        if not self.config.quiet:
            print '-' * 80
            print "Transforms %s to %s using %s" % (input_file, output_file,
                                                    xslt_file)
        cmd = [self.config.xsltproc, self.config.xsltproc_opts,
               "--output ", output_file]
        for name, value in self.config.parameters.items():
            cmd.append('--param')
            cmd.append(name)
            cmd.append("\"'" + value + "'\"")
        cmd.append(xslt_file)
        cmd.append(input_file)
        # executes transformation command line
        output = exec_cmd(' '.join(cmd))
        if not self.config.quiet:
            print output
        return output_file

    def fop_transform(self, fo_file, output_file):
        """FOP based transformation
        """
        if not self.config.quiet:
            print '-' * 80
            print "Transforms Formatting Objects to PDF (%s -> %s)" % (
                fo_file, output_file)
        # executes transformation command line
        output = exec_cmd("%s %s %s %s" %(self.config.fop, self.config.fop_opts,
                                 fo_file, output_file))
        if not self.config.quiet:
            print output
        return output_file

    def rest_transform(self, rest_file, output_file):
        """transforms Restructured Text to DOCBOOK XML
        """
        if not self.config.quiet:
            print '-' * 80
            print "Transforms Restructured Text to DOCBOOK XML (%s -> %s)" % (
                rest_file, output_file)
        from docutils import core, io
        from logilab.doctools.rest_docbook import DocbookWriter
        writer = DocbookWriter()
        pub = core.Publisher(writer=writer)
        pub.set_reader(reader_name='standalone',
                       parser_name='restructuredtext', parser=None)
        pub.source = io.FileInput(source_path=rest_file, encoding=self.config.inputenc)
        pub.destination = io.FileOutput(destination_path=output_file,
                                        encoding='UTF-8')
        # FIXME : find the way to specify docutils no parsing args
        # hint: use core.publish_programmatically ?
        sys.argv = [sys.argv[0]]
        try:
            pub.publish(settings_overrides={'output_encoding': 'UTF-8',
                                            'report_level': 2,
                                            'doctype': self.config.doctype,
                                            'traceback': True,
                                            'language_code': self.config.lang,
                                            })
        except Exception, ex:
            raise FormattingException(str(ex))
        return output_file

    def check_xml(self, xml_file):
        """check the given xml file is well formed XML
        """
        if not self.config.quiet:
            print '-' * 80
            print 'Checking %s' % xml_file
        output = exec_cmd("xmlproc_parse " + xml_file)
        xmlproc_output(output, 'well formed')
        return xml_file

    def validate_xml(self, xml_file):
        """check the given xml file is valid XML
        """
        if not self.config.quiet:
            print '-' * 80
            print 'Validating %s' % xml_file
        output = exec_cmd("xmlproc_val " + xml_file)
        xmlproc_output(output, 'valid')
        return xml_file


    def transform(self, filename):
        """run transforms on filename
        """
        # Raises deprecation warnings
        if self.config.doctype:
            warnings.warn("[doctools 0.4] ``--doctype`` option is deprecated, "
                          "rather specify directly in ReST source document "
                          "using ``.. class:: <doctype>`` at top level.")
        # process xsltroot to get a proper configuration
        if self.config.xsltroot and self.config.xsltroot != STANDARD_XSLT_PATH:
            # ~/ in parameters isn't' appreciated
            self.config.xsltroot = expanduser(self.config.xsltroot)
            self.config.parameters.setdefault('logo.dir',
                                              join(self.config.xsltroot, 'logos/'))
        else:
            self.config.xsltroot = STANDARD_XSLT_PATH
        # get transform parameters
        to_remove = []
        source_format = self.config.source
        dest_format = self.config.target
        preprocess = self.config.preprocess
        stylesheet = self.config.stylesheet
        base = splitext(basename(filename))[0]

        if not source_format:
            source_format = guess_format(filename)

        if source_format == 'pybill':
            exec_cmd('pybill %s' % filename)
            return

        if source_format.startswith('training_session'):
            from logilab.doctools.training_docs import produce_docs
            session_ref = source_format.split("//")[1]
            if session_ref == "":
                session_ref = "UNKNOWN"
            produce_docs(filename,
                         "%s-liste-presence.pdf" % session_ref,
                         "%s-fiches-evaluation.pdf" % session_ref)
            return

        # check docbook xml for validity or well formness
        if source_format == 'docbook':
            if not self.config.ignore_pi and (not preprocess or not stylesheet):
                preproc = []
                styles = {}
                tree = parse(filename)
                for pi in tree.xpath(
                            u"//processing-instruction('logidoc-preprocess')"):
                    attrs = parse_pi_data(pi.text)
                    if u"xslt" not in attrs:
                        msg = 'Bad logidoc-preprocess processing instruction.'\
                              ' Missing "xslt" attribute.'
                        raise FormattingException(msg)
                    preproc.append(attrs[u"xslt"])
                for pi in tree.xpath(
                                 u"//processing-instruction('logidoc-style')"):
                    attrs = parse_pi_data(pi.text)
                    if u"target" not in attrs:
                        msg = 'Bad logidoc-style processing instruction.'\
                              ' Missing "target" attribute.'
                        raise FormattingException(msg)
                    if u"xslt" not in attrs:
                        msg = 'Bad logidoc-style processing instruction.'\
                              ' Missing "xslt" attribute.'
                        raise FormattingException(msg)
                    styles[attrs[u"target"]] = attrs[u"xslt"]
                preprocess = preprocess or preproc
                stylesheet = stylesheet or styles.get(dest_format)
        # check we have a main stylesheet
        if not stylesheet and dest_format != 'docbook' and source_format != 'fo':
            raise OutputGuessException('Unable to guess the main style sheet')

        # transform ReST to docbook ?
        if source_format == 'rest':
            filename = self.rest_transform(filename, base + '.xml')
            if dest_format != 'docbook':
                to_remove.append(filename)

        # are we arrived ?
        if dest_format == 'docbook':
            return filename

        # preprocessing
        for preprocess_xslt in preprocess:
            xslt = self.absolute_stylesheet(preprocess_xslt, 'pre-process')
            output = '%s.%s.xml' % (base, preprocess_xslt)
            filename = self.xslt_transform(filename, output, xslt)
            to_remove.append(output)

        # finalization
        if dest_format == 'html':
            # transform DOCBOOK to HTML
            xslt = self.absolute_stylesheet(stylesheet, 'html')
            filename = self.xslt_transform(filename, base + '.html', xslt)
        else:
            if source_format != 'fo':
                # transform DOCBOOK to FO
                xslt = self.absolute_stylesheet(stylesheet, 'fo')
                filename = self.xslt_transform(filename, base + '.fo', xslt)
                to_remove.append(filename)
            # are we arrived ?
            if dest_format == 'fo':
                return filename
            # transform FO to PDF
            filename = self.fop_transform(filename, base + '.pdf')


        self.clean(to_remove)
        return filename


    def absolute_stylesheet(self, stylesheet, type):
        """return the absolute path of the given stylesheet"""
        if isabs(stylesheet):
            return stylesheet
        if stylesheet.endswith('.xsl') and stylesheet.endswith('.xslt'):
            return join(self.config.xsltroot, type, stylesheet)
        return join(self.config.xsltroot, type, stylesheet, 'root.xsl')

    def clean(self, files):
        """remove temporary files, unless configuration tells to keep them"""
        if self.config.keep:
            return
        if not self.config.quiet and files:
            print '-' * 80
            print 'Removing temporary files'
        for file in files:
            os.remove(file)


