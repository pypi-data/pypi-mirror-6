from logilab.common.testlib import TestCase,unittest_main

from logilab.doctools.rest_docbook import rest_dbk_transform
from lxml.etree import tostring


class ImagesTransformerTest(TestCase):

    def generic_test(self, rst, dbk):
        result = rest_dbk_transform(rst)
        res_string = ""
        for elt in result:
            res_string += tostring(elt)
        self.assertMultiLineEqual(res_string, dbk)

    def test_image_simple(self):
        rst = u"""
Simple image test.

.. image:: myfile.png

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple image test.</para><mediaobject xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><imageobject><imagedata fileref="myfile.png"/></imageobject></mediaobject><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_image_with_alt(self):
        rst = u"""
Image with alt test.

.. image:: myfile.png
   :alt: This is an alternate content that describes the image.
         It is very important to provide alternate content
         for the visually impaired users.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Image with alt test.</para><mediaobject xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><imageobject><imagedata fileref="myfile.png"/></imageobject><textobject><phrase>This is an alternate content that describes the image. It is very important to provide alternate content for the visually impaired users.</phrase></textobject></mediaobject><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_image_complex(self):
        rst = u"""
Complex image test.

.. image:: myfile.png
   :height: 14cm
   :width: 100%
   :scale: 97

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Complex image test.</para><mediaobject xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><imageobject><imagedata fileref="myfile.png" depth="14cm" width="100%" scale="97"/></imageobject></mediaobject><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_figure_simple(self):
        rst = u"""
Simple figure test.

.. figure:: myfile.png

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Simple figure test.</para><informalfigure xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><mediaobject><imageobject><imagedata fileref="myfile.png"/></imageobject></mediaobject></informalfigure><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_figure_with_caption(self):
        rst = u"""
Figure with caption test.

.. figure:: myfile.png

   This is the caption.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Figure with caption test.</para><figure xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>This is the caption.</title><mediaobject><imageobject><imagedata fileref="myfile.png"/></imageobject></mediaobject></figure><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

    def test_figure_with_legend(self):
        rst = u"""
Figure with legend test.

.. figure:: myfile.png

   This is the caption.

   This is a paragraph in the legend.

   This is another paragraph in the legend.

End of test.
"""
        dbk = u"""<para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">Figure with legend test.</para><figure xmlns:ldg="http://www.logilab.org/2005/DocGenerator"><title>This is the caption.</title><mediaobject><imageobject><imagedata fileref="myfile.png"/></imageobject><caption><para>This is a paragraph in the legend.</para><para>This is another paragraph in the legend.</para></caption></mediaobject></figure><para xmlns:ldg="http://www.logilab.org/2005/DocGenerator">End of test.</para>"""
        self.generic_test(rst, dbk)

if __name__ == '__main__':
    unittest_main()
