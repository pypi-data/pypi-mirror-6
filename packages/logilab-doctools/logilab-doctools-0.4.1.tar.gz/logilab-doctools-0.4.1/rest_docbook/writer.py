"""
Module containing the writer that does the transformation of a ReST document
into an XML Docbook tree.
"""
from docutils.writers import Writer
from logilab.doctools.rest_docbook.visitor import DocbookConverter
from lxml.etree import tostring, Element

class DocbookWriter(Writer):
    """
    Writer that produces a list of :class:`~lxml.etree.Element` objects
    containing the DocBook elements corresponding to the transformed ReST
    document.

    Please note that the standard attribute ``output`` contains a string
    representation of the result. The actual list of XML elements (in memory
    objects) can be found in the ``result`` attribute.
    """
    output = None
    """In the standard API, this attribute contains the string representation
    of the transformed form of the ReST document (``self.document``)."""
    result = None
    """Attribute containing a list of lxml :class:`~lxml.etree.Element` objects
    containing the XML Docbook elements built by the transformer."""

    def translate(self):
        # Backward compatibility with old version of doctools.
        if getattr(self.document.settings, "doctype", None):
            self.document.setdefault("classes", []).append(
                self.document.settings.doctype)
        # Starts conversion of document.
        visitor = DocbookConverter(self.document)
        self.document.walkabout(visitor)
        self.result = visitor.out_tree.getroot().getchildren()
        encoding = self.document.settings.output_encoding
        self.output = '<?xml version="1.0" encoding="%s"?>' % encoding.upper()
        if len(self.result) == 1:
            self.output += tostring(visitor.out_tree.getroot()[0],
                                    encoding=encoding,
                                    xml_declaration=False)
        else:
            self.output += tostring(visitor.out_tree.getroot(),
                                    encoding=encoding,
                                    xml_declaration=False)
