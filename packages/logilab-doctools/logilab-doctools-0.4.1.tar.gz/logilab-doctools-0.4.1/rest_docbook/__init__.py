"""
ReStructured Text to XML DocBook Converter.

This converter relies on Docutils module to read the ReST date. It provides
a Docutils Visitor and a Docutils Writer for the conversion into an XML tree
containing DocBook elements. The XML tree is built thanks to the lxml library.

Here are defined the high-level functions that can transform ReST data into 
XML DocBook data.
"""

import custom

from docutils.core import publish_string
from logilab.doctools.rest_docbook.writer import DocbookWriter


def rest_dbk_transform(rest):
    """
    Transforms a ``rest`` unicode string into a lxml tree containing the XML
    DocBook document.

    :param rest:
        ReStructured Text unicode string to be turned into XML DocBook.
    :returns:
        list of lxml :class:`~lxml.etree.Element` objects containing the XML
        DocBook elements built by the transformation.
    """
    writer = DocbookWriter()
    publish_string(writer=writer, source=rest,
                   settings_overrides={'traceback':True,
                                       'input_encoding': 'unicode',
                                       'output_encoding': 'utf-8',})
    return writer.result


def rest_file2dbk_tree(filename, encoding='utf-8'):
    """
    Reads a file in ReST format, and transforms it in a lxml tree
    containing the XML DocBook document.

    :param filename:
        Name of the file containing the ReST document.
    :returns:
        list of lxml :class:`~lxml.etree.Element` objects containing the XML
        DocBook elements built by the transformation.
    """
    restfile = open(filename)
    dbk_elts = rest_dbk_transform(unicode(restfile.read(), encoding=encoding))
    restfile.close()
    return dbk_elts
