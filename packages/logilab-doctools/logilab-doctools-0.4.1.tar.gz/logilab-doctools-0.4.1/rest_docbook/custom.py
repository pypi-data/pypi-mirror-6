"""
This module defines several customized directives or roles for the
documents written and processed at Logilab.
"""

from docutils.parsers.rst.directives import register_directive
from docutils.parsers.rst import Directive


class PassDirective(Directive):
    """
    Directive that does nothing.
    """
    required_arguments = 0
    optional_arguments = 0
    has_content= True
    def run(self):
        return []


class BreakPara(Directive):
    """
    New directive describing a paragraph preceded by a page break.

    This directive builds a regular paragraph node but adds a ``pagebreak``
    attribute whose value is set to ``True``.
    """
    required_arguments = 0
    optional_arguments = 0
    has_content= True
    def run(self):
        self.assert_has_content()
        # Builds a paragraph node and inserts the content of the node
        para = nodes.paragraph(rawsource=self.content, pagebreak="true",
                               **self.options)
        # Keeps on processing
        self.state.nested_parse(self.content, self.content_offset, para)
        return[para]

# Registers the new directive class in the analyzer
register_directive('break-para', BreakPara)


# Registers the Sphinx-specific directive "toctree" in the analyzer
# As we don't use it, just does nothing when finding it.

register_directive('toctree', PassDirective)

