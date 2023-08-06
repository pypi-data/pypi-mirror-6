"""
Module defining the visitor that will transform a ReST tree read by the
docutils machinery into a DocBook XML tree built thanks to the lxml
library.
"""

from lxml.etree import (ElementTree, Element, SubElement, Comment, fromstring,
                        tostring)
from docutils.nodes import (NodeVisitor, SkipNode, caption, citation, title,
                            document, sidebar, Text, reference, topic)
from docutils.languages import get_language
from logilab.doctools.rest_docbook.errors import DbkConversionError


LDG_NS = u"http://www.logilab.org/2005/DocGenerator"
"""
Namespace of Logilab extension (specific properties for customized rendering
of DocBook).
"""

NS_MAP = {u"ldg": LDG_NS,
          }
"""
Mapping between XML prefixes and namespaces.
"""

DBK_ENUM_STYLE = {"arabic"    : u"arabic",
                  "loweralpha": u"loweralpha",
                  "upperalpha": u"upperalpha",
                  "lowerroman": u"lowerroman",
                  "upperroman": u"upperroman",
                  }
"""
Dictionary for converting the enumeration styles specified in ReST into
the enumaration styles specified in the <orderedlist> element of DocBook.
"""

SECTION_DEFAULT_MAPPING = {u"book": u"chapter",
                           u"part": u"chapter",
                           u"article": u"section",
                           u"chapter": u"section",
                           u"appendix": u"section",
                           u"section": u"section",
                           }
"""
Name of the DocBook element a section might be converted in if no specific
class is specified, when it occurs inside another DocBook element (dictionary
key).
"""

DBK_LICIT_PARENTS = {u"book": tuple(),
                     u"part": (u"book",),
                     u"article": tuple(),
                     u"chapter": (u"book", u"part",),
                     u"appendix": (u"book", "part", u"article",),
                     u"section": (u"chapter", u"appendix", u"article",
                                  u"section",),
                     }
"""
For some DocBook elements, list of the possible parents when respecting the
DocBook structure.
"""


def append_text(xml_elt, text):
    """
    Utilitary function that insert text at the end of an XML element.

    The end of the XML element is the tail of its last children element or
    the text of the XML element itself.

    :param xml_elt:
        XML element where the text must be added
    :param text:
        Text that must be added inside the XML element
    """
    children = xml_elt.getchildren()
    if len(children) > 0:
        last_child = children[-1]
        if last_child.tail is None:
            last_child.tail = u""
        last_child.tail += text
    else:
        if xml_elt.text is None:
            xml_elt.text = u""
        xml_elt.text += text


class DocbookConverter(NodeVisitor):
    """
    Docutils visitor that builds a DocBook XML tree from the ReST tree.

    There are multiple ways to translate a ReST section node in a
    DocBook element : <book>, <part>, <chapter>, <appendix>, <article>, or
    <section>. Therefore, it is possible to use a class to specify
    which DocBook element a section node might be converted in:
    ``book``, ``part``, ``chapter``, ``appendix``, ``article``,
    ``section``.

    By default, if no class is specified, the ReST section nodes are
    converted in <section> DocBook elements. If a class is specified,
    the section node is converted to the corresponding DocBook element.
    For instance,

    .. sourcecode:: rest

       .. class:: book

       My title
       ========

    will be converted to

    .. sourcecode:: xml

       <book>
         <title>My title</title>
       </book>

    A default behaviour is implemented to ease the writing of ReST
    documents:

    * Inside a section converted to a <book> element, the sub-sections are
      converted to <chapter> elements unless specified differently with
      a class.

    * Inside a section converted to a <part> element, the sub-sections are
      converted to <chapter> elements unless specified differently with
      a class.

    * Inside a section converted to an <article> element, the sub-sections are
      converted to <section> elements unless specified differently with
      a class.

    * Inside a section converted to a <chapter> element, the sub-sections are
      converted to <section> elements.

    * Inside a section converted to an <appendix> element, the sub-sections are
      converted to <section> elements.

    * Inside a section converted to a <section> element, the sub-sections are
      converted to <section> elements.

    Of course, you can't arbitrarily specify the classes of the sections: you
    have to respect the structure of the DocBook document. The following
    structures are possible:

    * inside a book, you can find parts, chapters or appendices,
    * inside an article, you can find sections or appendices,
    * inside a part, you can find chapters or appendices,
    * inside a chapter, you can find sections,
    * inside an appendix, you can find sections,
    * inside a section, you can find sections.
    """
    def __init__(self, document):
        """
        Initializes the visitor converting ReST tree to XML DocBook tree.

        :param document:
            root of the ReST tree (document node).
        """
        NodeVisitor.__init__(self, document)
        # Stores the Docutils language object that gives i18n phrases
        self.lang = get_language(document.settings.language_code)
        # Initializes the XML tree that will be filled by this visitor
        self.out_tree = ElementTree(Element(u"docbook-excerpt", nsmap=NS_MAP))
        # Initializes the list containing all the parent elements of the
        # current output element
        self.parents_stack = [self.out_tree.getroot()]
        # Dictionary keeping temporary values (counters, pointers on footnotes
        # whose content will be filled later, etc.)
        self.temp_vals = {}
        # Flag set to ``True`` when the whitespaces must be kept in the Text
        # nodes (program listing, etc.)
        self.keep_whitespaces = False

    def insert_ids(self, node, elt):
        """
        Inserts the ids from the ReST node into the DocBook element.

        This method is called in almost every visit method.

        ReST allows multiple ids for a node. The first id is set into
        the ``id`` attribute of ``elt``. The following ids are stored inside
        ``anchor`` child elements of ``elt``.

        :param node:
           Docutils node currently transformed.

        :param elt:
           XML element that is currently filled with data from ``node``.
        """
        if node.has_key('ids') and len(node['ids']) > 0:
            if not elt.attrib.has_key(u"id") or elt.get(u"id").strip() == u"":
                elt.set(u"id", unicode(node['ids'][0]))
                start = 1
            else:
                start = 0
            for id_name in node['ids'][start:]:
                SubElement(elt, u"anchor", id=unicode(id_name))

    def insert_classes(self,node,elt,ignore=None):
        """
        Inserts the classes from the ReST node into the DocBook element.

        This method is called in almost every visit method.

        ReST allows multiple classes for a node. The first class is stored
        inside the ``role`` attribute of ``elt``. The following classes are
        stored in the ``condition`` attribute of ``elt``.

        :param node:
           Docutils node currently transformed.

        :param elt:
           XML element that is currently filled with data from ``node``.
        :param ignore:
           list of classes that must be ignored because they were already
           processed elsewhere.
        """
        if ignore is None:
            ignore = []
        if node.has_key('classes'):
            classes = [cls for cls in node['classes'] if cls not in ignore]
            if len (classes) > 0:
                if not elt.attrib.has_key(u"role") \
                        or elt.get(u"role").strip() == u"":
                    elt.set(u"role", unicode(classes[0]))
                    start = 1
                else:
                    start = 0
                if len(classes[start:]) > 0:
                    elt.set(u"condition", u" ".join(classes[start:]))


    def visit_document(self, node):
        # In the temporary structure, we initialize a dictionnary that will
        # contain the footnote definitions indexed with the footnote ids.
        self.temp_vals['footnotes'] = {}
        # If the document has an id, it comes from a unique top-level section
        # that has been promoted as the document itself. Thus, we process it
        # as a regular section.
        if node.has_key("ids") and len(node["ids"]) > 0:
            self.visit_section(node)
            # Sets the language attribute onto the high-level element
            self.parents_stack[-1].set("lang",
                                       node.settings.language_code)
            # Adds a metadata element that will be filled later with the
            # subtitle node and the docinfo node.
            name = u"%sinfo" % self.parents_stack[-1].tag
            self.temp_vals['metadata'] = SubElement(self.parents_stack[-1],
                                                    name)

    def depart_document(self, node):
        # If the document comes from a top-level section, process it as a
        # regular section.
        if node.has_key("ids") and len(node["ids"]) > 0:
            self.temp_vals.pop('metadata')
            self.depart_section(node)
        # In order to finish the processing, we must put each footnote
        # definition within the first reference of the footnote.
        for f_id, f_elt in self.temp_vals['footnotes'].items():
            if self.temp_vals.has_key('footnoteref_%s' %f_id):
                # We change the first <footnoteref> element in the DocBook tree
                # for the <footnote> element containing the definition of the
                # footnote.
                fref_elt = self.temp_vals['footnoteref_%s' %f_id][0]
                if fref_elt.tail is not None:
                    f_elt.tail = fref_elt.tail
                fref_elt.getparent().replace(fref_elt, f_elt)
                # The others <footnoteref> elements are kept as if in the
                # DocBook tree. They now point towards the footnote definition.
            else:
                raise DbkConversionError("No footnote reference in text "
                                         "matching the footnote %s:\n%s"
                                         % (f_id, tostring(f_elt)))
        self.temp_vals.pop('footnotes')


    def visit_docinfo(self, node):
        # The docinfo node contains several metadata pieces of
        # information that must be inserted in the <*info> element
        # stored inside the 'metadata' key in the temporary structure.
        # This key shall exist in the temporary structure if a docinfo
        # node is encountered.
        self.parents_stack.append(self.temp_vals['metadata'])

    def depart_docinfo(self, node):
        if self.temp_vals.has_key('metadata-address'):
            self.temp_vals.pop('metadata-address')
        if self.temp_vals.has_key('metadata-edition'):
            self.temp_vals.pop('metadata-edition')
        self.parents_stack.pop()


    def visit_header(self, node):
        # The header node is not processed as header static data is not
        # defined in the DocBook tree (it only contains the actual content).
        raise SkipNode

    def depart_header(self, node):
        pass


    def visit_footer(self, node):
        # The footer node is not processed as footer static data is not
        # defined in the DocBook tree (it only contains the actual content).
        raise SkipNode

    def depart_footer(self, node):
        pass


    def visit_Text(self, node):
        text = node.astext()
        # Changes whitespaces for a single space character except if
        # self.keep_whitespaces is set to ``True``
        if not self.keep_whitespaces and text:
            corr_text = u""
            if text[0].isspace():
                corr_text = u" "
            corr_text += u" ".join(text.split())
            if text[-1].isspace() and corr_text != u" ":
                corr_text += u" "
            text = corr_text
        # The text is added inside the last XML element of the stack
        # (``self.parents_stack``): either on the the tail attribute
        # of the last of its children, or on the text attribute of
        # this element itself.
        append_text(self.parents_stack[-1], text)

    def depart_Text(self, node):
        pass


    def visit_abbreviation(self, node):
        elt = SubElement(self.parents_stack[-1], u"abbrev")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_abbreviation(self, node):
        self.parents_stack.pop()


    def visit_acronym(self, node):
        elt = SubElement(self.parents_stack[-1], u"acronym")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_acronym(self, node):
        self.parents_stack.pop()


    def visit_address(self, node):
        # Only appears in the docinfo node.
        # The <address> element in the metadata element is used for the
        # address node and for the contact node.
        # If it has not been yet created, creates it and keeps it in
        # the temporary structure.
        if not self.temp_vals.has_key('metadata-address'):
            self.temp_vals['metadata-address'] = \
                SubElement(self.parents_stack[-1], u"address")
        addr_elt = self.temp_vals['metadata-address']
        self.insert_ids(node, addr_elt)
        self.insert_classes(node, addr_elt)
        # The address node contains a text child with different address lines
        # separated with "\n" characters. It can also contain reference nodes
        # (email or web addresses).
        for child in node.children:
            if isinstance(child, Text):
                for subtxt in child.astext().split("\n"):
                    if subtxt == u"":
                        continue
                    line_elt = SubElement(addr_elt, u"otheraddress")
                    line_elt.text = subtxt
            elif isinstance(child, reference):
                if child.get('refuri', u"").startswith("mailto:"):
                    line_elt = SubElement(addr_elt, u"email")
                    line_elt.text = child.astext()
                else:
                    line_elt = SubElement(addr_elt, u"otheraddress")
                    line_elt.text = child.astext()
        # The node has been processed.
        raise SkipNode

    def depart_address(self, node):
        pass


    def visit_admonition(self, node):
        elt = SubElement(self.parents_stack[-1], u"note")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt, ignore=("admonition-admonition-title",))
        self.parents_stack.append(elt)

    def depart_admonition(self, node):
        self.parents_stack.pop()


    def visit_attention(self, node):
        elt = SubElement(self.parents_stack[-1], u"important")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_attention(self, node):
        self.parents_stack.pop()


    def visit_attribution(self, node):
        elt = SubElement(self.parents_stack[-1], u"attribution")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_attribution(self, node):
        self.parents_stack.pop()


    def visit_author(self, node):
        # Only appears in the docinfo node.
        aut_elt = SubElement(self.parents_stack[-1], u"author")
        self.insert_ids(node, aut_elt)
        self.insert_classes(node, aut_elt)
        # The author node contains a text child with the author name. It can
        # also contain reference nodes (email or web addresses).
        for child in node.children:
            if isinstance(child, Text):
                name_elt = SubElement(aut_elt, u"othername")
                name_elt.text = child.astext()
            elif isinstance(child, reference):
                if child.get('refuri', u"").startswith("mailto:"):
                    line_elt = SubElement(aut_elt, u"email")
                    line_elt.text = child.astext()
                else:
                    line_elt = SubElement(aut_elt, u"othername")
                    line_elt.text = child.astext()
        # The node has been processed.
        raise SkipNode

    def depart_author(self, node):
        pass


    def visit_authors(self, node):
        # Only appears in the docinfo node.
        elt = SubElement(self.parents_stack[-1], u"authorgroup")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        # The authorgroup node contains author nodes describing each author.
        self.parents_stack.append(elt)

    def depart_authors(self, node):
        self.parents_stack.pop()


    def visit_block_quote(self, node):
        # Block quotes are also used for epigraphs and highlights and
        # pull-quotes.
        elt_name = u"blockquote"
        class_name = u""
        if node.has_key("classes"):
            if "epigraph" in node["classes"]:
                elt_name = u"epigraph"
                class_name = u""
            elif "highlights" in node["classes"]:
                elt_name = u"highlights"
                class_name = u""
            elif "pull-quote" in node["classes"]:
                elt_name = u"blockquote"
                class_name = u"pull-quote"
        elt = SubElement(self.parents_stack[-1], elt_name)
        self.insert_ids(node, elt)
        if class_name != "":
            elt.set(u"role", class_name)
        self.insert_classes(node, elt, ignore=("epigraph", "highlights",
                                               "pull-quote",))
        self.parents_stack.append(elt)

    def depart_block_quote(self, node):
        self.parents_stack.pop()


    def visit_bullet_list(self, node):
        elt = SubElement(self.parents_stack[-1], u"itemizedlist")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_bullet_list(self, node):
        self.parents_stack.pop()


    def visit_caption(self, node):
        # The caption of a ReST figure is used as the title of the
        # DocBook figure.
        elt = SubElement(self.parents_stack[-1], u"title")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_caption(self, node):
        self.parents_stack.pop()


    def visit_caution(self, node):
        elt = SubElement(self.parents_stack[-1], u"caution")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_caution(self, node):
        self.parents_stack.pop()


    def visit_citation(self, node):
        # ReST citations are like footnotes, except they have a label
        # instead of a number. In DocBook, there is no equivalent structure
        # so we will use a footnote and try to keep the citation label
        # in the DocBook footnote label.
        self.visit_footnote(node)

    def depart_citation(self, node):
        self.depart_footnote(node)


    def visit_citation_reference(self, node):
        # In ReST, citations are like footnotes, except they have a label
        # instead of a number. In DocBook, there is no equivalent structure
        # so we will use a footnote and try to keep the citation label
        # in the DocBook footnote label.
        self.visit_footnote_reference(node)

    def depart_citation_reference(self, node):
        self.depart_footnote_reference(node)


    def visit_classifier(self, node):
        elt = Element(u"type")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.temp_vals["classifiers"][-1].append(elt)
        self.parents_stack.append(elt)

    def depart_classifier(self, node):
        self.parents_stack.pop()


    def visit_colspec(self, node):
        elt = SubElement(self.parents_stack[-1], u"colspec")
        if node.has_key("colwidth"):
            elt.set(u"colwidth", u"%d*" % node["colwidth"])
        if node.get('stub'):
            elt.set(u"{%s}bold" % LDG_NS, u"true")
        # We add a column name on the <colspec> element and stock this name
        # in a temporary list that will be used for computing the entries
        # spans.
        num = len(self.temp_vals["colnames"])
        colname = u"col%d" % num
        elt.set(u"colname", colname)
        self.temp_vals["colnames"].append(colname)
        self.insert_classes(node, elt)

    def depart_colspec(self, node):
        pass


    def visit_comment(self, node):
        cmt = Comment()
        cmt.text = u" "
        self.parents_stack[-1].append(cmt)
        self.parents_stack.append(cmt)

    def depart_comment(self, node):
        cmt = self.parents_stack.pop()
        cmt.text += u" "


    def visit_compound(self, node):
        # In DocBook, there is no equivalent to a ReST compound paragraph.
        # we just ignore the element and process the contained nodes.
        pass

    def depart_compound(self, node):
        pass


    def visit_contact(self, node):
        # Only appears in the docinfo node.
        # The <address> element in the metadata element is used for the
        # address node and for the contact node.
        # If it has not been yet created, creates it and keeps it in
        # the temporary structure.
        if not self.temp_vals.has_key('metadata-address'):
            self.temp_vals['metadata-address'] = \
                SubElement(self.parents_stack[-1], u"address")
        addr_elt = self.temp_vals['metadata-address']
        self.insert_ids(node, addr_elt)
        self.insert_classes(node, addr_elt)
        # The contact node contains a text child or reference children with
        # email / web addresses.
        for child in node.children:
            if isinstance(child, Text):
                line_elt = SubElement(addr_elt, u"otheraddress")
                line_elt.text = child.astext()
            elif isinstance(child, reference):
                if child.get('refuri', u"").startswith("mailto:"):
                    line_elt = SubElement(addr_elt, u"email")
                    line_elt.text = child.astext()
                else:
                    line_elt = SubElement(addr_elt, u"otheraddress")
                    line_elt.text = child.astext()
        # The node has been processed.
        raise SkipNode

    def depart_contact(self, node):
        pass


    def visit_container(self, node):
        # In DocBook, there is no equivalent to a ReST container.
        # we just ignore the element and process the contained nodes.
        pass

    def depart_container(self, node):
        pass


    def visit_copyright(self, node):
        # Only appears in the docinfo node.
        # As the content of the copyright node is free, we translate it into
        # a <legalnotice> DocBook element instead of a <copyright> element.
        leg_elt = SubElement(self.parents_stack[-1], u"legalnotice")
        self.insert_ids(node, leg_elt)
        self.insert_classes(node, leg_elt)
        para_elt = SubElement(leg_elt, u"para")
        self.parents_stack.append(para_elt)

    def depart_copyright(self, node):
        self.parents_stack.pop()


    def visit_danger(self, node):
        elt = SubElement(self.parents_stack[-1], u"warning")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_danger(self, node):
        self.parents_stack.pop()


    def visit_date(self, node):
        # Only appears in the docinfo node.
        dte_elt = SubElement(self.parents_stack[-1], u"date")
        self.insert_ids(node, dte_elt)
        self.insert_classes(node, dte_elt)
        # The date node contains a text child with the date.
        for child in node.children:
            if isinstance(child, Text) or isinstance(child, reference):
                append_text(dte_elt, child.astext())
        # The node has been processed.
        raise SkipNode

    def depart_date(self, node):
        pass


    def visit_decoration(self, node):
        # The decoration node contains the header and the footer nodes.
        pass

    def depart_decoration(self, node):
        pass


    def visit_definition(self, node):
        elt = SubElement(self.parents_stack[-1], u"listitem")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_definition(self, node):
        self.parents_stack.pop()


    def visit_definition_list(self, node):
        elt = SubElement(self.parents_stack[-1], u"variablelist")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_definition_list(self, node):
        self.parents_stack.pop()


    def visit_definition_list_item(self, node):
        elt = SubElement(self.parents_stack[-1], u"varlistentry")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.temp_vals.setdefault("classifiers", []).append([])
        self.parents_stack.append(elt)

    def depart_definition_list_item(self, node):
        self.parents_stack.pop()
        classifiers = self.temp_vals["classifiers"].pop()
        if len(classifiers) > 0:
            term = self.temp_vals["term"]
            term.text += u" ("
            for cls in classifiers:
                term.append(cls)
                cls.tail = u", "
            classifiers[-1].tail = u")"
        if len(self.temp_vals["classifiers"]) == 0:
            self.temp_vals.pop("classifiers")
            self.temp_vals.pop("term")

    def visit_description(self, node):
        elt = SubElement(self.parents_stack[-1], u"listitem")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_description(self, node):
        self.parents_stack.pop()


    def visit_doctest_block(self, node):
        elt = SubElement(self.parents_stack[-1], u"programlisting")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)
        self.keep_whitespaces = True

    def depart_doctest_block(self, node):
        self.keep_whitespaces = False
        self.parents_stack.pop()


    def visit_emphasis(self, node):
        elt = SubElement(self.parents_stack[-1], u"emphasis")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_emphasis(self, node):
        self.parents_stack.pop()


    def visit_entry(self, node):
        elt = SubElement(self.parents_stack[-1], u"entry")
        self.insert_ids(node, elt)
        # Computes the index of the column where this entry is.
        # As some cells in previous rows might span over the current row,
        # we use a list ``temp_vals["rows_to_span"]`` that gives for each
        # column the number of rows to be spanned (``0`` means there is no
        # previous spanning cell over this row and thus the entry can be 
        # inserted in this cell).
        # Theorically, the table is well-formed (parsed and verified by the
        # ReST parser) and we will always find a free cell on the row where 
        # the entry can be inserted.
        colnum = self.temp_vals["entry_colnum"] + 1
        while colnum < len(self.temp_vals["rows_to_span"]):
            if self.temp_vals["rows_to_span"][colnum] == 0:
                break
            else:
                colnum += 1
        if colnum >= len(self.temp_vals["rows_to_span"]):
            raise DbkConversionError("Found an entry outside the table!")
        # Adds row spanning attribute on <entry> DocBook element
        rows_to_span = 0
        if node. has_key("morerows") and node["morerows"] > 0:
            rows_to_span = int(node["morerows"])
            elt.set(u"morerows", unicode(rows_to_span))
        # Adds column spanning attributes on <entry> DocBook element. The node
        # contains a morecols property but in DocBook, we must give the names
        # of the first column (the current one) and the last column (the
        # one whose index is ``current index + morecols``).
        last_colnum = colnum
        if node. has_key("morecols") and node["morecols"] > 0:
            last_colnum = colnum + int(node["morecols"])
            if last_colnum >= len(self.temp_vals["rows_to_span"]):
                raise DbkConversionError("Found an entry spreading out the "
                                         "table!")
            elt.set(u"namest", self.temp_vals["colnames"][colnum])
            elt.set(u"nameend", self.temp_vals["colnames"][last_colnum])
        # Changes the "number of rows to be spanned" in the cells of the
        # table (``self.temp_vals["rows_to_span"]`` list).
        # First, we decrement the "number of rows to be spanned" in the cells
        # we jumped over when computing the column index of this entry.
        # (``self.temp_vals["entry_colnum"]`` contains the number of the
        # column for the previous entry).
        for i in range(self.temp_vals["entry_colnum"] + 1, colnum):
            self.temp_vals["rows_to_span"][i] -= 1
        # Secondly, we insert the ``rows_to_span`` number for this entry into
        # the cells that this entry spans on.
        for i in range(colnum, last_colnum+1):
            self.temp_vals["rows_to_span"][i] = rows_to_span
        # Finally, we change the current column number for the entries.
        self.temp_vals["entry_colnum"] = last_colnum
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_entry(self, node):
        elt = self.parents_stack.pop()
        # When the table cell only contains a single paragraph, we directly
        # insert the text in the <entry>, without a <para> (thus the table is
        # simpler).
        if len(elt.getchildren()) == 1 and elt[0].tag == u"para":
            # The <entry> normally doesn't contain text, so we simply add the
            # <para> text and children in the <entry>.
            elt.text = elt[0].text
            elt.extend(elt[0].getchildren())
            # The <para> normally doesn't contain tail text, so we do nothing
            # on the tail attributes.
            # We then remove the <para> for the output tree.
            elt.remove(elt[0])

    def visit_enumerated_list(self, node):
        elt = SubElement(self.parents_stack[-1], u"orderedlist")
        self.insert_ids(node, elt)
        if node.has_key("enumtype") and node["enumtype"].strip() != "":
            if DBK_ENUM_STYLE.has_key(node["enumtype"].lower()):
                elt.set(u"numeration",
                        DBK_ENUM_STYLE[node["enumtype"].lower()])
        if node.has_key("start"):
            elt.set(u"{%s}first-number" % LDG_NS, unicode(node['start']))
        # Prefix and suffix properties don't exist in DocBook and thus are
        # ignored.
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_enumerated_list(self, node):
        self.parents_stack.pop()


    def visit_error(self, node):
        elt = SubElement(self.parents_stack[-1], u"caution")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_error(self, node):
        self.parents_stack.pop()


    def visit_field(self, node):
        elt = SubElement(self.parents_stack[-1], u"varlistentry")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_field(self, node):
        self.parents_stack.pop()


    def visit_field_body(self, node):
        elt = SubElement(self.parents_stack[-1], u"listitem")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_field_body(self, node):
        self.parents_stack.pop()


    def visit_field_list(self, node):
        elt = SubElement(self.parents_stack[-1], u"variablelist")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_field_list(self, node):
        self.parents_stack.pop()


    def visit_field_name(self, node):
        elt = SubElement(self.parents_stack[-1], u"term")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_field_name(self, node):
        self.parents_stack.pop()


    def visit_figure(self, node):
        # If the figure contains a caption, the caption will be used as
        # the figure title in DocBook. Else, we just insert a DocBook
        # <informalfigure> element (without title)
        cpt =  [child for child in node if isinstance(child, caption)]
        if len(cpt) > 0:
            elt_name = u"figure"
        else:
            elt_name = u"informalfigure"
        elt = SubElement(self.parents_stack[-1], elt_name)
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_figure(self, node):
        # Rearrange children order
        fig_elt = self.parents_stack.pop()
        ttl_elt = fig_elt.find(u"title")
        if ttl_elt is not None:
            fig_elt.remove(ttl_elt)
            fig_elt.insert(0, ttl_elt)
        if self.temp_vals.has_key('caption'):
            # If there was a ReST legend node in the ReST figure, it has
            # been inserted inside a <caption> element that we will had into
            # the <mediaobject> element.
            capt_elt = self.temp_vals.pop('caption')
            mdo_elt = fig_elt.find(u"mediaobject")
            if mdo_elt is not None:
                mdo_elt.append(capt_elt)


    def visit_footnote(self, node):
        # The ReST footnote node only contains the definition of the footnote.
        # In DocBook, footnotes are defined with their reference (inside the
        # actual text).
        # Therefore, we keep the footnote definition into the temporary
        # structure and we will put it in the DocBook document inside its
        # first reference after the processing of the document is finished.
        # The ReST citation nodes are processed as footnote nodes.
        elt = Element(u"footnote")
        self.insert_ids(node, elt)
        if node.has_key('ids'):
            for id_def in node['ids']:
                self.temp_vals['footnotes'][id_def] = elt
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_footnote(self, node):
        elt = self.parents_stack.pop()
        # If the numbering of the footnote is not automatic or if we are in
        # a citation node, we use the label to number the DocBook footnote.
        if ((not node.has_key('auto') or node['auto'] != 1) or
            isinstance(node, citation)) and self.temp_vals.has_key('label'):
            lab_elt = self.temp_vals.pop('label')
            label = lab_elt.text or u""
            elt.set(u"label", label)


    def visit_footnote_reference(self, node):
        # The ReST footnote_ref node only contains the reference to the
        # footnote that will be later defined.
        # In DocBook, footnotes are defined with their first reference (inside
        # the actual text).
        # Therefore, for the footnote_ref, we only insert a place holder inside
        # the output tree and will replace this place holder with the actual
        # footnote at the end of the processing of the document.
        # The ReST citation_ref nodes are processed as footnote_ref nodes.
        if node.has_key('refid'):
            elt = SubElement(self.parents_stack[-1], u"footnoteref")
            self.insert_ids(node, elt)
            elt.set(u"linkend", unicode(node['refid']))
            # In the temporary struture, we keep a list of all the
            # <footnoteref> element corresponding to the ``refid`` identifier.
            # This list will be used to insert the footnote definition.
            temp_key = "footnoteref_%s" % node['refid']
            self.temp_vals.setdefault(temp_key, []).append(elt)
            self.insert_classes(node, elt)
            # We keep the current <footnoteref> element into the temporary
            # structure for further use in the depart method.
            self.temp_vals['current_footnoteref'] = elt
            # We insert an artificial <label> element for retrieveing the label
            # associated to the footnote (the label is the text inside the
            # ReST node). Please note that the <label> element is not inserted
            # in the output tree but kept in the elements stack.
            lab_elt = Element(u"label")
            self.parents_stack.append(lab_elt)
        else:
            raise SkipNode

    def depart_footnote_reference(self, node):
        # If the footnote reference is not automatically numbered or if we
        # are in a citation reference, adds the label read inside the ReST
        # node into the "label" attribute of the DocBook <footnoteref>
        # output element.
        if node.has_key('refid'):
            ref_elt = self.temp_vals.pop('current_footnoteref')
            lbl_elt = self.parents_stack.pop()
            if (not node.has_key('auto') or node['auto'] != 1) or \
                    isinstance(node, citation):
                label = lbl_elt.text or u""
                ref_elt.set(u"label", label)


    def visit_generated(self, node):
        # The generated node are only used to insert the section
        # numbers that are automatically computed by ReST.
        # In DocBook, we don't need to numbre the sections as they will
        # be autmatically numbered.
        raise SkipNode

    def depart_generated(self, node):
        pass


    def visit_hint(self, node):
        elt = SubElement(self.parents_stack[-1], u"tip")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_hint(self, node):
        self.parents_stack.pop()


    def visit_image(self, node):
        container = SubElement(self.parents_stack[-1], u"mediaobject")
        self.insert_ids(node, container)
        img_obj = SubElement(container, u"imageobject")
        img_data = SubElement(img_obj, u"imagedata",
                              fileref=unicode(node['uri']) )
        if node.has_key('height'):
            img_data.set(u'depth', unicode(node['height']) )
        if node.has_key('width'):
            img_data.set(u'width', unicode(node['width']) )
        if node.has_key('scale'):
            img_data.set(u'scale', unicode(node['scale']) )
        # align doesn't have the same meaning in ReST and DocBook, so
        # we just ignore it
        if node.has_key('alt') and node['alt'].strip() != "":
            txt_obj = SubElement(container, u"textobject")
            phrs = SubElement(txt_obj, u"phrase")
            phrs.text = u" ".join(node['alt'].split())
        self.insert_classes(node, container)

    def depart_image(self, node):
        pass


    def visit_important(self, node):
        elt = SubElement(self.parents_stack[-1], u"important")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_important(self, node):
        self.parents_stack.pop()


    def visit_inline(self, node):
        elt = SubElement(self.parents_stack[-1], u"phrase")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_inline(self, node):
        self.parents_stack.pop()


    def visit_label(self, node):
        # The label node is inside a footnote or a citation node. When the
        # numbering is not automatic (always on citations and when auto=0 on
        # footnotes), it must be used as the label of the DocBook <footnote>
        # in the output tree.
        # The label is not inserted in the output tree but kept in the
        # temporary structure. It will be used in ``depart_footnote`` method.
        elt = Element(u"label")
        self.temp_vals['label'] = elt
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_label(self, node):
        self.parents_stack.pop()


    def visit_legend(self, node):
        # In DocBook, there is no equivalent to the ReST legend of a figure.
        # We put it in the caption of the <mediaobject> of the DocBook <figure>
        # (the ReST caption of the figure is inserted in the <title> of the
        # Doccbook <figure>).
        elt = Element(u"caption")
        self.insert_ids(node, elt)
        self.temp_vals['caption'] = elt
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_legend(self, node):
        self.parents_stack.pop()


    def visit_line(self, node):
        # In DocBook, there is no XML element that represent a line into
        # a <literallayout> element. Thus, we directly insert the text read
        # in the line node.
        # This text is inserted in the last XML element with the
        # ``visit_text`` method.
        # Between each line, we insert `new lines` characters (cf.
        # ``depart_line`` method.
        # As we cannot have nested <literallayout> elements, we insert, at
        # the beginning of a line, blank spaces to reflect the imbrication.
        prefix = u"  " * (self.temp_vals["nested_line_block"] - 1)
        append_text(self.parents_stack[-1], prefix)

    def depart_line(self, node):
        # We add a `new line` character at the end of the line.
        append_text(self.parents_stack[-1], u"\n")


    def visit_line_block(self, node):
        # The ReST line_block node can be translated to a DocBook
        # <literallayout> element. But, a <literallayout> cannot contain
        # nested <literallayout> elements. Therefore, we insert just one
        # <literallayout> and will insert spaces at the beginning of the lines
        # if there are nested <literallayout>.
        if self.parents_stack[-1].tag == u"literallayout":
            # This is a nested line_block node. We don't insert an XML element
            # but we increment the nesting counter (for inserting the correct
            # number of spaces at the beginning of the lines).
            self.temp_vals["nested_line_block"] += 1
        else:
            # This is the first line_block node. We insert an XML element
            # and initialize the nesting counter.
            elt = SubElement(self.parents_stack[-1], u"literallayout")
            self.insert_ids(node, elt)
            self.insert_classes(node, elt)
            self.parents_stack.append(elt)
            self.temp_vals["nested_line_block"] = 1

    def depart_line_block(self, node):
        if self.temp_vals["nested_line_block"] > 1:
            # We exit a nested line_block. We decrement the nesting counter.
            self.temp_vals["nested_line_block"] -= 1
        else:
            # We exit the first line_block node. We erase the nesting counter
            # and exit the DocBook <literallayout> output element.
            self.temp_vals.pop("nested_line_block")
            self.parents_stack.pop()


    def visit_list_item(self, node):
        elt = SubElement(self.parents_stack[-1], u"listitem")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_list_item(self, node):
        self.parents_stack.pop()


    def visit_literal(self, node):
        # Inside a literal, the whitespaces must be kept. So we set
        # ``keep_whitespaces`` flag to ``True``.
        elt = SubElement(self.parents_stack[-1], u"literal")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.keep_whitespaces = True
        self.parents_stack.append(elt)

    def depart_literal(self, node):
        self.parents_stack.pop()
        self.keep_whitespaces = False


    def visit_literal_block(self, node):
        # Inside a literal block, the whitespaces must be kept. So we set
        # ``keep_whitespaces`` flag to ``True``.
        # A literal block node is transformed into a <programlisting> element.
        elt = SubElement(self.parents_stack[-1], u"programlisting")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.keep_whitespaces = True
        self.parents_stack.append(elt)

    def depart_literal_block(self, node):
        self.parents_stack.pop()
        self.keep_whitespaces = False


    def visit_note(self, node):
        elt = SubElement(self.parents_stack[-1], u"note")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_note(self, node):
        self.parents_stack.pop()


    def visit_option(self, node):
        elt = SubElement(self.parents_stack[-1], u"term")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_option(self, node):
        self.parents_stack.pop()


    def visit_option_argument(self, node):
        elt = SubElement(self.parents_stack[-1], u"replaceable")
        self.insert_ids(node, elt)
        if node.has_key('delimiter'):
            elt.text = unicode(node['delimiter'])
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_option_argument(self, node):
        self.parents_stack.pop()


    def visit_option_group(self, node):
        # Does nothing as each option will be turned into a DocBook <term>
        # element.
        pass

    def depart_option_group(self, node):
        pass


    def visit_option_list(self, node):
        elt = SubElement(self.parents_stack[-1], u"variablelist")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_option_list(self, node):
        self.parents_stack.pop()


    def visit_option_list_item(self, node):
        elt = SubElement(self.parents_stack[-1], u"varlistentry")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_option_list_item(self, node):
        self.parents_stack.pop()


    def visit_option_string(self, node):
        elt = SubElement(self.parents_stack[-1], u"option")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_option_string(self, node):
        self.parents_stack.pop()


    def visit_organization(self, node):
        # Only appears in the docinfo node.
        org_elt = SubElement(self.parents_stack[-1], u"orgname")
        self.insert_ids(node, org_elt)
        self.insert_classes(node, org_elt)
        # The author node contains a text child with the organization name.
        # It can also contain reference nodes (email or web addresses).
        for child in node.children:
            if isinstance(child, Text):
                append_text(org_elt, child.astext())
            elif isinstance(child, reference):
                if child.has_key('refuri'):
                    lnk_elt = SubElement(org_elt, u"ulink")
                    lnk_elt.set(u"url", child['refuri'])
                    lnk_elt.text = child.astext()
                else:
                    append_text(org_elt, child.astext())
        # The node has been processed.
        raise SkipNode

    def depart_organization(self, node):
        pass


    def visit_paragraph(self, node):
        elt = SubElement(self.parents_stack[-1], u"para")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_paragraph(self, node):
        self.parents_stack.pop()


    def visit_pending(self, node):
        # The pending node indicates a place where the ReST processor will
        # later add some content. The ReST processor will replace this node
        # with another node.
        # Theorically, we have nothing to do here.
        pass

    def depart_pending(self, node):
        pass


    def visit_problematic(self, node):
        # This node is inserted when the ReST processor couldn't read
        # or understand something in the document. It contains the
        # source text that led to the error.
        elt = SubElement(self.parents_stack[-1], u"literal",
                         role=u"problematic")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.keep_whitespaces = True
        if node.has_key('refid'):
            elt2 =  SubElement(elt, u"link",
                               linkend=unicode(node['refid']) )
            self.parents_stack.append(elt2)
        else:
            self.parents_stack.append(elt)

    def depart_problematic(self, node):
        self.parents_stack.pop()
        self.keep_whitespaces = False


    def visit_raw(self, node):
        # If the raw data is a DocBook excerpt, inserts it untouched. Data in
        # other formats are skipped.
        ### ENHANCE ME: we should perhaps do something with SVG data (insert
        ### a figure) or MathML data (insert an equation).
        if node.has_key('format') and node['format'].lower() == 'docbook':
            xml_str = node.astext()
            xml_root = fromstring("<root>%s</root>" % xml_str)
            self.parents_stack[-1].extend(xml_root.getchildren())
        raise SkipNode

    def depart_raw(self, node):
        pass


    def visit_reference(self, node):
        elt_name = None
        if node.has_key('refuri'):
            elt_name = u"ulink"
            att_name = u"url"
            target = unicode(node['refuri'])
        elif node.has_key('refid'):
            elt_name = u"link"
            att_name = u"linkend"
            target = unicode(node['refid'])
        if elt_name is not None:
            elt = SubElement(self.parents_stack[-1], elt_name)
            self.insert_ids(node, elt)
            elt.set(att_name,target)
            self.insert_classes(node, elt)
            self.parents_stack.append(elt)
        else:
            raise DbkConversionError("Reference to an unknown target: %s"
                                     % node)

    def depart_reference(self, node):
        if node.has_key('refuri') or node.has_key('refid'):
            self.parents_stack.pop()


    def visit_revision(self, node):
        # Only appears in the docinfo node.
        # The <edition> element in the metadata element is used for the
        # revision node and for the version node. It should contain:
        # ``{version text}, {revision text}``
        # If it has not been yet created, we create the <edition> element
        # and keep it in the temporary structure.
        if not self.temp_vals.has_key('metadata-edition'):
            self.temp_vals['metadata-edition'] = \
                SubElement(self.parents_stack[-1], u"edition")
            self.temp_vals['metadata-edition'].text = u""
        edt_elt = self.temp_vals['metadata-edition']
        self.insert_ids(node, edt_elt)
        self.insert_classes(node, edt_elt)
        # The revision node contains a text child with the revision data. It
        # may also contain reference nodes (email or web addresses).
        data = u""
        for child in node.children:
            if isinstance(child, Text) or isinstance(child, reference):
                data += child.astext()
        if len(edt_elt.text) > 0:
            edt_elt.text = u"%s, %s" % (edt_elt.text, data)
        else:
            edt_elt.text = data
        # The node has been processed.
        raise SkipNode

    def depart_revision(self, node):
        pass


    def visit_row(self, node):
        elt = SubElement(self.parents_stack[-1], u"row")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        # Initializes a temporary counter that allows us to know the column
        # that the current entry is in
        self.temp_vals["entry_colnum"] = -1
        self.parents_stack.append(elt)

    def depart_row(self, node):
        self.parents_stack.pop()
        self.temp_vals.pop("entry_colnum")


    def visit_rubric(self, node):
        elt = SubElement(self.parents_stack[-1], u"bridgehead")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_rubric(self, node):
        self.parents_stack.pop()


    def visit_section(self, node):
        # Finds the name of the element this section node must be converted to.
        elt_name = None
        classes_to_ignore = []
        parent_name = self.parents_stack[-1].tag
        if parent_name == u"docbook-excerpt":
            # Arbitrary root node outside DocBook structure
            parent_name = None
        # Tries to find a class specifying which DocBook element the section
        # node must be converted to.
        if node.has_key("classes"):
            for name in ("book", "part", "article", "chapter", "appendix",
                         "section"):
                if name in node["classes"]:
                    elt_name = name
                    classes_to_ignore.append(name)
                    break
        # Tries to find a default mapping giving the DocBook element the
        # section must be converted to, when this section occurs inside
        # a given DocBook element.
        # Else, the section will be converted into a <section> element.
        if elt_name is None:
            elt_name = SECTION_DEFAULT_MAPPING.get(parent_name, u"section")
        # Checks the name of the DocBook element is licit inside the parent
        # element.
        if parent_name is not None \
                and parent_name not in DBK_LICIT_PARENTS[elt_name]:
            raise DbkConversionError("In DocBook structure, can't have a "
                                     "<%s> element into a <%s> element"
                                     % (elt_name, parent_name))
        # Finally builds the DocBook element
        elt = SubElement(self.parents_stack[-1], elt_name)
        self.insert_ids(node, elt)
        self.insert_classes(node, elt, ignore=classes_to_ignore)
        self.parents_stack.append(elt)

    def depart_section(self, node):
        self.parents_stack.pop()


    def visit_sidebar(self, node):
        elt = SubElement(self.parents_stack[-1], u"sidebar")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_sidebar(self, node):
        sdb = self.parents_stack.pop()
        # If there was a subtitle, adds a sidebarinfo element and inserts
        # in this new element the title and subtitle of the sidebar.
        if self.temp_vals.has_key('sidebar-subtitle'):
            sdbi = Element(u"sidebarinfo")
            sdb.insert(0, sdbi)
            ttl_elt = sdb.find(u"title")
            sdb.remove(ttl_elt)
            sdbi.append(ttl_elt)
            sdbi.append(self.temp_vals.pop('sidebar-subtitle'))


    def visit_status(self, node):
        # Only appears in the docinfo node.
        inf_elt = SubElement(self.parents_stack[-1], u"releaseinfo")
        self.insert_ids(node, inf_elt)
        self.insert_classes(node, inf_elt)
        # The status node contains a text child with the status information. 
        # It may also contain reference nodes (email or web addresses).
        for child in node.children:
            if isinstance(child, Text):
                append_text(inf_elt, child.astext())
            elif isinstance(child, reference):
                if child.has_key('refuri'):
                    lnk_elt = SubElement(inf_elt, u"ulink")
                    lnk_elt.set(u"url", child['refuri'])
                    lnk_elt.text = child.astext()
                else:
                    append_text(inf_elt, child.astext())
        # The node has been processed.
        raise SkipNode

    def depart_status(self, node):
        pass


    def visit_strong(self, node):
        elt = SubElement(self.parents_stack[-1], u"emphasis", role=u"bold")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_strong(self, node):
        self.parents_stack.pop()


    def visit_subscript(self, node):
        elt = SubElement(self.parents_stack[-1], u"subscript")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_subscript(self, node):
        self.parents_stack.pop()


    def visit_substitution_definition(self, node):
        # Place holder where the ReST processor defines a substitution.
        # Theorically, we must skip the node
        raise SkipNode

    def depart_substitution_definition(self, node):
        pass


    def visit_substitution_reference(self, node):
        # Place holder where the ReST processor inserts a reference to a
        # substitution. Theorically, we have nothing to do.
        pass

    def depart_substitution_reference(self, node):
        pass


    def visit_subtitle(self, node):
        elt = Element(u"subtitle")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        if isinstance(node.parent, document) \
                and self.temp_vals.has_key('metadata'):
            # The <subtitle> element is the subtitle of the document,
            # adds it to the metadata element (that should exist in the
            # temporary structure).
            self.temp_vals['metadata'].append(elt)
        elif isinstance(node.parent, sidebar):
            # The <subtitle> element is stored inside the temporary structure
            # and will be processed inside the ``depart_sidebar`` method to be
            # inserted in a <sidebarinfo> metadata element.
            self.temp_vals['sidebar-subtitle'] = elt
        else:
            # Actually we should never get here, but just in case we simply
            # add the <subtitle> element inside the parent element.
            self.parents_stack[-1].append(elt)
        self.parents_stack.append(elt)

    def depart_subtitle(self, node):
        self.parents_stack.pop()


    def visit_superscript(self, node):
        elt = SubElement(self.parents_stack[-1], u"superscript")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_superscript(self, node):
        self.parents_stack.pop()


    def visit_system_message(self, node):
        # System messages (errors) are already displayed by the ReST
        # processor.
        elt = SubElement(self.parents_stack[-1], u"warning",
                         role=u"system_message")
        self.insert_ids(node, elt)
        title = u"### "
        if node.has_key('type'):
            title += unicode(node['type'].upper())
        else:
            title += u"SYSTEM MESSAGE"
        if node.has_key('line'):
            title += u" on line %d" % node['line']
        title_elt = SubElement(elt, u"title")
        title_elt.text = title
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_system_message(self, node):
        elt = self.parents_stack.pop()
        if node.has_key('backrefs') and len(node['backrefs']) > 0:
            see_para = SubElement(elt,u"para")
            see_para.text = u"See "
            for idref in node['backrefs']:
                lnk =  SubElement(see_para,u"link",
                                  linkend = unicode(idref) )
                lnk.text = u"this occurrence"
                lnk.tail = u", "
            see_para.getchildren()[-1].tail = u"."


    def visit_table(self, node):
        # If the table node contains a title, we create a <table> DocBook
        # element, else we create an <informaltable> DocBook element.
        ttl =  [child for child in node if isinstance(child, title)]
        if len(ttl) > 0:
            elt_name = u"table"
        else:
            elt_name = u"informaltable"
        elt = SubElement(self.parents_stack[-1], elt_name)
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)
        # Initializes a list for the columns names. This list will be filled
        # when we insert the <colspec> DocBooks elements and will be used for
        # computing the spans in the entry nodes (in DocBook, the spans
        # use the columns names).
        self.temp_vals["colnames"] = []

    def depart_table(self, node):
        self.parents_stack.pop()
        self.temp_vals.pop("colnames")


    def visit_target(self, node):
        # If the target contains something, we are surely inside a paragraph
        # on an inline target. Therefore, we add a phrase DocBook element that
        # will hold the target id (in order to have an existing target for
        # the links).
        # Else, we simply add an anchor.
        if len(node.children) > 0:
            elt = SubElement(self.parents_stack[-1], u"phrase")
            self.insert_ids(node, elt)
            self.insert_classes(node, elt)
            self.parents_stack.append(elt)
        else:
            # If the target is empty, it is certainly the specification of
            # a link. We just ignore it as it has been preprocessed by the
            # ReST reader.
            pass

    def depart_target(self, node):
        if len(node.children) > 0:
            self.parents_stack.pop()


    def visit_tbody(self, node):
        elt = SubElement(self.parents_stack[-1], u"tbody")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        # Initializes a temporary list containing the various cells of the
        # table. In this each cell of this list, we will put the number of
        # rows spanned by the entry displayed in this cell. This will help us
        # computing the column that the current entry is in (it depends on the
        # entries of the previous rows that can span over the cells of the
        # current row).
        # The list is initialized with as many cells as there are columns.
        self.temp_vals["rows_to_span"] = [0]*len(self.temp_vals["colnames"])
        self.parents_stack.append(elt)

    def depart_tbody(self, node):
        self.parents_stack.pop()
        self.temp_vals.pop("rows_to_span")


    def visit_term(self, node):
        elt = SubElement(self.parents_stack[-1], u"term")
        self.insert_ids(node, elt)
        self.temp_vals["term"] = elt
        elt.text = u""
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_term(self, node):
        self.parents_stack.pop()


    def visit_tgroup(self, node):
        elt = SubElement(self.parents_stack[-1], u"tgroup")
        self.insert_ids(node, elt)
        elt.set(u"cols", unicode(node["cols"]))
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_tgroup(self, node):
        self.parents_stack.pop()


    def visit_thead(self, node):
        elt = SubElement(self.parents_stack[-1], u"thead")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        # Initializes a temporary list containing the various cells of the
        # table. See tbody visit method for explanations.
        self.temp_vals["rows_to_span"] = [0]*len(self.temp_vals["colnames"])
        self.parents_stack.append(elt)

    def depart_thead(self, node):
        self.parents_stack.pop()
        self.temp_vals.pop("rows_to_span")


    def visit_tip(self, node):
        elt = SubElement(self.parents_stack[-1], u"tip")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_tip(self, node):
        self.parents_stack.pop()


    def visit_title(self, node):
        elt = Element(u"title")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        if isinstance(node.parent, document) \
                and self.temp_vals.has_key('metadata'):
            # The <title> element is the title of the document,
            # adds it to the metadata element (that should exist in the
            # temporary structure).
            self.temp_vals['metadata'].append(elt)
        elif isinstance(node.parent, topic) and \
                ("abstract" in node.parent.get("classes", []) or
                 "dedication" in node.parent.get("classes", [])):
            # The title is not useful as we use specific DocBook elements
            # (<abstract> or <dedication>).
            raise SkipNode
        else:
            # Simply adds the <title> element inside the parent element.
            self.parents_stack[-1].append(elt)
        self.parents_stack.append(elt)

    def depart_title(self, node):
        self.parents_stack.pop()


    def visit_title_reference(self, node):
        elt = SubElement(self.parents_stack[-1], u"citetitle")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_title_reference(self, node):
        self.parents_stack.pop()


    def visit_topic(self, node):
        # There is no equivalent to ReST topics in DocBook. The closer element
        # is the sidebar, so we transform ReST topics in DocBook sidebars.
        # The topic is also used for abstracts and dedications in the
        # bibliographic fields of the docinfo node.
        # The topic can also be used to describe a figure.
        if "abstract" in node.get("classes", []):
            # Used in the docinfo element to describe the abstract.
            # We create an <abstract> element in the DocBook metadata element
            # (kept in the temporary structure).
            elt_name = u"abstract"
            parent = self.temp_vals.get("metadata", self.parents_stack[-1])
        elif "dedication" in node.get("classes", []):
            # Used in the docinfo element to describe the dedication.
            # We create a <dedication> element in the DocBook metadata element
            # (kept in the temporary structure).
           elt_name = u"dedication"
           parent = self.temp_vals.get("metadata", self.parents_stack[-1])
        elif "figure" in node.get("classes", []):
            # Used to describe a figure.
            # We create a <figure> element.
           elt_name = u"figure"
           parent = self.parents_stack[-1]
        else:
            elt_name = u"sidebar"
            parent = self.parents_stack[-1]
        elt = SubElement(parent, elt_name)
        self.insert_ids(node, elt)
        self.insert_classes(node, elt, 
                            ignore=("abstract", "dedication", "figure"))
        self.parents_stack.append(elt)

    def depart_topic(self, node):
        self.parents_stack.pop()


    def visit_transition(self, node):
        # There is no equivalent to ReST transitions in DocBook.
        # We just ignore them.
        pass

    def depart_transition(self, node):
        pass


    def visit_version(self, node):
        # Only appears in the docinfo node.
        # The <edition> element in the metadata element is used for the
        # revision node and for the version node. It should contain:
        # ``{version text}, {revision text}``
        # If it has not been yet created, we create the <edition> element
        # and keep it in the temporary structure.
        if not self.temp_vals.has_key('metadata-edition'):
            self.temp_vals['metadata-edition'] = \
                SubElement(self.parents_stack[-1], u"edition")
            self.temp_vals['metadata-edition'].text = u""
        edt_elt = self.temp_vals['metadata-edition']
        self.insert_ids(node, edt_elt)
        self.insert_classes(node, edt_elt)
        # The revision node contains a text child with the revision data. It
        # may also contain reference nodes (email or web addresses).
        data = u""
        for child in node.children:
            if isinstance(child, Text) or isinstance(child, reference):
                data += child.astext()
        if len(edt_elt.text) > 0:
            edt_elt.text = u"%s, %s" % (data, edt_elt.text)
        else:
            edt_elt.text = data
        # The node has been processed.
        raise SkipNode

    def depart_version(self, node):
        pass


    def visit_warning(self, node):
        elt = SubElement(self.parents_stack[-1], u"warning")
        self.insert_ids(node, elt)
        self.insert_classes(node, elt)
        self.parents_stack.append(elt)

    def depart_warning(self, node):
        self.parents_stack.pop()
