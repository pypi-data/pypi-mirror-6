#!/usr/bin/python
# -*- coding: utf-8 -*-
"""%(PROG)s: format Python source code to xml docbook using roles

USAGE: %(PROG)s [OPTIONS] <input.py>...

OPTIONS:
  -h / --help
       display this help message and exit

  -r / --root "rootstring"
       insert "rootstring" as root

  -f / --format <OUTPUT_FORMAT>
       set output format. Default to %(DEFAULT_FORMAT)s.
       Available formats are %(FORMATS)s.

  -s / --stdout
       write results to standard output
"""
## Original code from active state recipe
##         'Colorize Python source using the built-in tokenizer'
## posted by Jürgen Hermann and modified to obtain docbook instead of colored
## html

## ----------------------------------------------------------------------------
##      MoinMoin - Python Source Parser

##  This code is part of MoinMoin (http://moin.sourceforge.net/) and converts
##  Python source code to HTML markup, rendering comments, keywords, operators,
##  numeric and string literals in different colors.

##  It shows how to use the built-in keyword, token and tokenize modules
##  to scan Python source code and re-emit it with no changes to its
##  original formatting (which is the hard part).

import sys, cStringIO
import keyword, token, tokenize
from xml.sax.saxutils import escape
from os.path import basename


## Python Source Parser #####################################################

_KEYWORD = token.NT_OFFSET + 1
_TEXT    = token.NT_OFFSET + 2

class Parser:
    """
    Send colored python source.
    """

    def __init__(self, raw, tags, out = sys.stdout):
        """
        Store the source text.
        """
        self.raw = raw.expandtabs().strip()
        self.out = out
        self.tags = tags

    def format(self, root=''):
        """
        Parse and send the colored source.
        """
        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = self.raw.find('\n', pos) + 1
            if not pos: break
            self.lines.append(pos)
        self.lines.append(len(self.raw))

        # parse the source and write it
        self.pos = 0
        text = cStringIO.StringIO(self.raw)
        if root:
            self.out.write('<%s>\n'%root)
        self.out.write('  <programlisting role="python">\n')
        try:
            tokenize.tokenize(text.readline, self)
        except tokenize.TokenError, ex:
            msg = ex[0]
            line = ex[1][0]
            print "ERROR: %s%s\n" % (msg, self.raw[self.lines[line]:])
        self.out.write('\n  </programlisting>\n')
        if root:
            self.out.write('</%s>\n'%root)

    def __call__(self, toktype, toktext, (srow, scol), (erow, ecol), line):
        """
        Token handler.
        """
        #print "type", toktype, token.tok_name[toktype], "text", toktext,
        #print "start", srow,scol, "end", erow,ecol, "<br>"

        ## calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)

        ## handle newlines
        if toktype in [token.NEWLINE, tokenize.NL]:
            self.out.write('\n')
            return

        ## send the original whitespace, if needed
        if newpos > oldpos:
            self.out.write(self.raw[oldpos:newpos])

        ## skip indenting tokens
        if toktype in [token.INDENT, token.DEDENT]:
            self.pos = newpos
            return

        ## map token type to a group
        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = _KEYWORD

        t_tags = self.tags.get(toktype, self.tags[_TEXT])

        ## send text
        self.out.write(t_tags[0])
        self.out.write(escape(toktext))
        self.out.write(t_tags[1])


## Command line ###############################################################
_TAGS = {
    token.NUMBER:       ('<emphasis role="number">', '</emphasis>'),
    token.OP:           ('<emphasis role="op">', '</emphasis>'),
    token.STRING:       ('<emphasis role="string">', '</emphasis>'),
    tokenize.COMMENT:   ('<emphasis role="comment">', '</emphasis>'),
    token.NAME:         ('<emphasis role="name">', '</emphasis>'),
    token.ERRORTOKEN:   ('<emphasis role="error">', '</emphasis>'), # ?
    _KEYWORD:           ('<emphasis role="keyword">', '</emphasis>'),
    _TEXT:              ('', '')
    }
_STANDARDS_TAGS = {
    token.NUMBER:       ('', ''),
    token.OP:           ('', ''),
    token.STRING:       ('<emphasis>', '</emphasis>'),
    tokenize.COMMENT:   ('<emphasis>', '</emphasis>'),
    token.NAME:         ('', ''),
    token.ERRORTOKEN:   ('', ''), # ?
    _KEYWORD:           ('<emphasis role="bold">', '</emphasis>'),
    _TEXT:              ('', '')
    }

PROG = basename(sys.argv[0])
FORMATS = ('docbook', 'extended-docbook')
DEFAULT_FORMAT = 'docbook'

def run(args):
    import getopt

    ## get options
    (opt, args) = getopt.getopt(args,
                                'hr:f:s',
                                ['help', 'root=', 'format=', 'stdout'])
    root, ext, stdout = '', 0, 0
    for o in opt:
        if o[0] == '-h' or o[0] == '--help':
            print __doc__ % globals()
            return
        elif o[0] == '-r' or o[0] == '--root':
            root = o[1]
        elif o[0] == '-f' or o[0] == '--format':
            val = o[1].lower()
            if not val in FORMATS:
                raise 'Unknown format %s' % val
            if val == 'extended-docbook':
                ext = 1
        elif o[0] == '-s' or o[0] == '--stdout':
            stdout = 1

    ## transforms source files
    for file in args:
        if file[-3:] != '.py':
            sys.stderr.write('Unknown extension, ignored file %s\n' % file)
            continue
        source = open(file, 'r')
        if not stdout:
            output = '%s.xml' % file[:-3]
            dest = open(output, 'w+')
        else:
            dest = sys.stdout
        sys.stderr.write("Formatting...\n")
        ## write colorized version to "python.html"
        if not ext:
            Parser(source.read(), _STANDARDS_TAGS, dest).format(root)
        else:
            Parser(source.read(), _TAGS, dest).format(root)
        source.close()
        dest.close()


if __name__ == "__main__":
    run(sys.argv[1:])

