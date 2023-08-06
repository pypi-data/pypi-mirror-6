#!/usr/bin/python
'''%(PROG)s: format xml source code to xml docbook using roles

USAGE: %(PROG)s [OPTIONS] <input.xml>...

OPTIONS:
  -h / --help
       display this help message and exit

  -o / --output <OUTPUT_FILE>
       write results in file <OUTPUT_FILE>.
  -s / --stdout
       write results to standard output.
  -e / --encoding iso-8859-1
       specify encoding to use in outputs.

  -n / --no-head
       do not insert output headers.

  -f / --format <OUTPUT_FORMAT>
       set output format. Default to %(DEFAULT_FORMAT)s.
       Available formats are %(FORMATS)s.
'''

import sys
from os.path import basename
from xml.dom.ext import SplitQName
from xml.sax.handler import ContentHandler

PROG = basename(sys.argv[0])
FORMATS = ('docbook', 'extended-docbook', 'html')
DEFAULT_FORMAT = 'docbook'

_ROOT, _STRING, _COMMENT, _NAME, _KEYWORD, _TEXT, _HEAD = 0, 1, 2, 3, 4, 5, 6

LOGILAB = {
    _HEAD: ('''<?xml version="1.0" encoding="%s"?>
<article>''', '</article>'),
    _ROOT: ('<programlisting role="python">','</programlisting>'),
    _STRING: ('<emphasis role="string">', '</emphasis>'),
    _COMMENT:('<emphasis role="comment">', '</emphasis>'),
    _NAME:   ('<emphasis role="name">', '</emphasis>'),
    _KEYWORD:('<emphasis role="keyword">', '</emphasis>'),
    _TEXT:   ('', '')
    }
DOCBOOK = {
    _HEAD: ('''<?xml version="1.0" encoding="%s"?>
<article>''', '</article>'),
    _ROOT: ('<programlisting>','</programlisting>'),
    _STRING: ('<emphasis>', '</emphasis>'),
    _COMMENT:('<emphasis>', '</emphasis>'),
    _NAME:   ('', ''),
    _KEYWORD:('<emphasis role="bold">', '</emphasis>'),
    _TEXT:   ('', '')
    }
HTML = {
    _HEAD: ('''<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=%s">
  <link rel="stylesheet" type="text/css" href="/intranet.css">
</head>
<body>''','</body>\n</html>'),
    _ROOT: ('<div>', '</div>'),
    _STRING: ('<font color="#004080">', '</font>'),
    _COMMENT:('<font color="#008000">', '</font>'),
    _NAME:   ('', ''),
    _KEYWORD:('<font color="#C00000">', '</font>'),
    _TEXT:   ('', '')
    }

## full sax handler, print each event to output ###############################

class XmlFormatSaxHandler(ContentHandler):
    """
    Format an xmlfile to docbook or html
    """

    def __init__(self, head=1, output=sys.stdout, encoding='UTF-8'):
        self._out = output
        self._cod = encoding
        self._head = head
        self._o_d = LOGILAB
        self._ind = 0

    def set_format(self, format):
        if format == 'docbook':
            self._o_d = DOCBOOK
        elif format == 'extended-docbook':
            self._o_d = LOGILAB
        if format == 'html':
            self._o_d = HTML

    ## content handler ########################################################
    def startDocument(self):
        if self._head:
            self._out.write(self._o_d[_HEAD][0] % self._cod)
        self._out.write(self._o_d[_ROOT][0])

    def endDocument(self):
        self._out.write(self._o_d[_ROOT][1])
        if self._head:
            self._out.write(self._o_d[_HEAD][1])

    def startElement(self, name, attrs):
        prefix, local = SplitQName(name)
        if prefix:
            self._out.write('&lt;%s%s%s:%s%s%s'.encode(self._cod) % (
                self._o_d[_KEYWORD][0], prefix, self._o_d[_KEYWORD][1],
                self._o_d[_NAME][0], local, self._o_d[_NAME][1]))
        else:
            self._out.write('&lt;%s%s%s'.encode(self._cod) % (
                self._o_d[_KEYWORD][0], local, self._o_d[_KEYWORD][1]))
        for key, val in attrs.items():
            prefix, local = SplitQName(key)
            if prefix:
                self._out.write(' %s%s%s:%s%s%s=%s"%s"%s'.encode(self._cod) % (
                    self._o_d[_KEYWORD][0], prefix, self._o_d[_KEYWORD][1],
                    self._o_d[_NAME][0], local, self._o_d[_NAME][1],
                    self._o_d[_STRING][0], val, self._o_d[_STRING][1]))
            else:
                self._out.write(' %s%s%s=%s"%s"%s'.encode(self._cod) % (
                    self._o_d[_NAME][0], local, self._o_d[_NAME][1],
                    self._o_d[_STRING][0], val, self._o_d[_STRING][1]))
        self._out.write('>')

    def endElement(self, name):
        prefix, local = SplitQName(name)
        if prefix:
            self._out.write('&lt;/%s%s%s:%s%s%s>'.encode(self._cod) % (
                self._o_d[_KEYWORD][0], prefix, self._o_d[_KEYWORD][1],
                self._o_d[_NAME][0], local, self._o_d[_NAME][1]))
        else:
            self._out.write('&lt;/%s%s%s>'.encode(self._cod) % (
                self._o_d[_KEYWORD][0], local, self._o_d[_KEYWORD][1]))

    def processingInstruction(self, target, data):
        self._out.write('&lt;?%s%s%s %s%s%s>'.encode(self._cod) % (
            self._o_d[_NAME][0], target, self._o_d[_NAME][1],
            self._o_d[_STRING][0], data, self._o_d[_STRING][1]))

    def characters(self, ch):
        self._out.write('%s%s%s' % (
            self._o_d[_TEXT][0], ch.replace('<', '&lt;').encode(self._cod),
            self._o_d[_TEXT][1]))

    ## lexical handler ########################################################
    def comment(self, comment):
        self._out.write('%s&lt;!--%s-->%s' % (
            self._o_d[_COMMENT][0],
            comment.replace('<', '&lt;').encode(self._cod),
            self._o_d[_COMMENT][1]))

    def startCDATA(self):
        self.cdata = 0
        self._out.write('&lt;%s[CDATA[%s' % (
            self._o_d[_KEYWORD][0], self._o_d[_KEYWORD][1]))

    def endCDATA(self):
        self._out.write('%s]]%s>' % (
            self._o_d[_KEYWORD][0], self._o_d[_KEYWORD][1]))

    def startDTD(self, name, public_id, system_id):
        self._out.write('&lt;%s!DOCTYPE%s %s'.encode(self._cod) % (
            self._o_d[_KEYWORD][0], self._o_d[_KEYWORD][1], name))
        if public_id:
            self._out.write(' PUBLIC %s"%s"%s %s"%s"%s [\n'.encode(self._cod) % (
                self._o_d[_STRING][0], public_id, self._o_d[_STRING][1],
                self._o_d[_STRING][0], system_id, self._o_d[_STRING][1]))
        else:
            self._out.write(' SYSTEM %s"%s"%s [\n'.encode(self._cod) % (
                self._o_d[_STRING][0], system_id, self._o_d[_STRING][1]))

    def endDTD(self):
        self._out.write(']>\n')

    def startEntity(self, name):
        pass

    def endEntity(self, name):
        pass

    ## decl handler ###########################################################
    def internalEntityDecl(self, name, value):
        self._out.write('&lt;%s!ENTITY%s %s %s>\n'.encode(self._cod) % (
            self._o_d[_KEYWORD][0], self._o_d[_KEYWORD][1], name, value))

    def externalEntityDecl(self, name, public_id, system_id):
        self._out.write('&lt;%s!ENTITY%s %s'.encode(self._cod) % (
            self._o_d[_KEYWORD][0], self._o_d[_KEYWORD][1], name))
        if public_id:
            self._out.write(' PUBLIC %s"%s"%s %s"%s"%s>\n'.encode(self._cod) % (
                self._o_d[_STRING][0], public_id, self._o_d[_STRING][1],
                self._o_d[_STRING][0], system_id, self._o_d[_STRING][1]))
        else:
            self._out.write(' SYSTEM %s"%s"%s>\n'.encode(self._cod) % (
                self._o_d[_STRING][0], system_id, self._o_d[_STRING][1]))

    def elementDecl(self, elem_name, content_model):
        c_m = _decode_content_model(content_model)
        self._out.write('&lt;%s!ELEMENT%s %s %s>\n'.encode(self._cod) % (
             self._o_d[_KEYWORD][0], self._o_d[_KEYWORD][1], elem_name,
            c_m))

    def attributeDecl(self, elem_name, attr_name, type_d, value_def, value):
        import types
        if type(type_d) is types.ListType:
            s = ''
            for pos in type_d:
                if not s:
                    s = '(%s' % pos
                else:
                    s = '%s|%s' % (s, pos)
            s = '%s)' % s
            self._out.write('&lt;%s!ATTLIST%s %s %s %s %s>\n'.encode(self._cod) % (
                self._o_d[_KEYWORD][0], self._o_d[_KEYWORD][1], elem_name,
                attr_name, s , value_def))
        else:
            self._out.write('&lt;%s!ATTLIST%s %s %s %s>\n'.encode(self._cod) % (
                self._o_d[_KEYWORD][0], self._o_d[_KEYWORD][1], elem_name,
                attr_name, type))

C_OP, C_VAL, C_NUM = 0, 1, 2
def _decode_content_model(content_m):
    s = ''
    if content_m[C_OP] == ',':
        for c_m in content_m[C_VAL]:
            if not s:
                s = '(%s' % _decode_content_model(c_m)
            else:
                s = '%s, %s' % (s, _decode_content_model(c_m))
        s = '%s)%s' % (s, content_m[C_NUM] )
    elif content_m[C_OP] == '|':
        for c_m in content_m[C_VAL]:
            if not s:
                s = '(%s' % _decode_content_model(c_m)
            else:
                s = '%s|%s' % (s, _decode_content_model(c_m))
        s = '%s)%s' % (s, content_m[C_NUM] )
    else:
        s = '%s%s' % (s, content_m[C_OP])
        s = '%s%s' % (s, content_m[-1])
    return s


def run(args):
    """
    main
    """
    import getopt, os
    from xml.sax import make_parser
    from xml.sax.handler import property_lexical_handler
    from xml.sax.handler import property_declaration_handler
    ## get options
    (options, args) = getopt.getopt(args,
                                'he:o:sf:n',
                                ['help', 'encoding=', 'output=', 'stdout',
                                 'format=', 'no-head'])
    encod, output, dest, head, format = 'UTF-8', None, None, 1, DEFAULT_FORMAT
    for opt in options:
        if opt[0] == '-h' or opt[0] == '--help':
            print __doc__ % globals()
            return
        elif opt[0] == '-o' or opt[0] == '--output':
            output = opt[1]
            dest = open(output, 'w')
        elif opt[0] == '-s' or opt[0] == '--stdout':
            dest = sys.stdout
        elif opt[0] == '-o' or opt[0] == '--format':
            val = opt[1].lower()
            if not val in FORMATS:
                raise 'Unknown format %s' % val
            format = val
        elif opt[0] == '-e' or opt[0] == '--encoding':
            encod = opt[1]
        elif opt[0] == '-n' or opt[0] == '--no-head':
            head = 0
    if len(args) == 0:
        print __doc__ % globals()
        return
    ## transforms source files (xmlproc support property_lexical_handler while
    ##      pyexpat doen't)
    #p = make_parser(['xml.sax.drivers2.drv_xmlproc'])
    p = make_parser()
    for filename in args:
        source = open(filename, 'r')
        ## prepare handler
        if not dest:
            if filename[-4:] not in ('.xml', '.dtd'):
                sys.stderr.write('Unknown extension %s, ignored file %s\n' % \
                                 (filename[-4:], filename))
                continue
            dest = open('%s_dcbk.xml' % os.path.basename(filename)[:-4], 'w+')
        h = XmlFormatSaxHandler(head, dest, encod)
        h.set_format(format)
        p.setContentHandler(h)
        try:
            p.setProperty(property_lexical_handler, h)
        except Exception, exc:
            print exc
        try:
            p.setProperty(property_declaration_handler, h)
        except Exception, exc:
            print exc
        sys.stderr.write("Formatting %s ...\n" % filename)

        ## parse and write colorized version to output file
        p.parse(source)

        source.close()
        if not output and not dest is sys.stdout:
            dest.close()
            dest = None


if __name__ == "__main__":
    run(sys.argv[1:])
