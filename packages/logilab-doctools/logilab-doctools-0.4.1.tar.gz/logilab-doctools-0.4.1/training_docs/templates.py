# -*- coding: utf-8 -*-
"""
Module containing the templates used to produce the PDF documents.
"""
__docformat__ = "restructuredtext en"

import os.path as osp
from reportlab.lib.units import cm
from reportlab.lib.colors import black
from reportlab.platypus import PageTemplate, Frame
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.pagesizes import A4, landscape

from utils import style_title, style_normal_left
from logilab.doctools import DATA_DIR

COMPANY_LOGO = osp.join(DATA_DIR, "logo-logilab.png")


class AttendanceListPageTemplate(PageTemplate):
    """
    Class defining the page template used to draw the attendance list.
    """
    def __init__(self, reference, title, instructor, template_id=""):
        """
        :parameter reference: Reference of the training session
        :type reference: unicode

        :parameter title: Title of the training session
        :type title: unicode

        :parameter instructor: Name of the instructor
        :type instructor: unicode
        """
        self.training_ref = reference
        self.training_title = title
        self.instructor_name = instructor
        main_frames = [
            Frame(1*cm, 1.7*cm, 13.35*cm, 15.8*cm,
                  leftPadding=0*cm, bottomPadding=0*cm,
                  rightPadding=0*cm, topPadding=0*cm),
            Frame(15.35*cm, 1.7*cm, 13.35*cm, 15.8*cm,
                  leftPadding=0*cm, bottomPadding=0*cm,
                  rightPadding=0*cm, topPadding=0*cm),
                      ]
        # Calls the base class initializer.
        PageTemplate.__init__(self, id=template_id, frames=main_frames,
                              pagesize=landscape(A4))

    def beforeDrawPage(self, canvas, document):
        """
        Overrides the method called before drawing on a new page of the PDF
        document. This method draws various static data on the page
        (logo, session reference, session title, instructor name).
        """
        # saves canvas state
        canvas.saveState()
        # Separator between the two sides of the page
        canvas.setStrokeColor(black)
        canvas.line(14.85*cm, 1*cm, 14.85*cm, 20*cm)
        # the logo is not drawn through the frame because image as flowable
        # cannot be aligned on the left (they are always centered)
        from PIL import Image as PImage
        img = PImage.open(COMPANY_LOGO)
        initial_width, initial_height = img.size
        img_height  = 1.3*cm
        img_width = img_height * float(initial_width) / float(initial_height)
        canvas.drawInlineImage(img, 1*cm, 18.8*cm,
                               img_width, img_height)
        canvas.drawInlineImage(img, 15.35*cm, 18.8*cm,
                               img_width, img_height)
        # Draws the top frames (title and session information)
        top_content = []
        top_content.append(Paragraph(u"<b>Feuille de présence</b>",
                                     style_title))
        top_content.append(Spacer(1, 0.5*cm))
        tit_para = Paragraph(u"Cours : %s" % self.training_title,
                             style_normal_left)
        ref_para = Paragraph(u"Référence : %s" % self.training_ref,
                             style_normal_left)
        tab = Table([ [tit_para, ref_para] ], [8.85*cm, 4.5*cm], None)
        tab.setStyle(
            TableStyle([ ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                         ('VALIGN',        (0,0), (-1,-1), 'TOP'),
                         ('LEFTPADDING',   (0,0), ( 0,-1), 0),
                         ('LEFTPADDING',   (1,0), (-1,-1), 0.5*cm),
                         ('RIGHTPADDING',  (0,0), ( 0,-1), 0.5*cm),
                         ('RIGHTPADDING',  (1,0), (-1,-1), 0),
                         ('TOPPADDING',    (0,0), (-1,-1), 0),
                         ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                       ])
                    )
        top_content.append(tab)
        top_left_f = Frame(1*cm, 17.7*cm, 13.35*cm, 1.6*cm,
                           leftPadding=0*cm, bottomPadding=0*cm,
                           rightPadding=0*cm, topPadding=0*cm)
        top_left_f.addFromList(top_content[:], canvas)
        top_right_f = Frame(15.35*cm, 17.7*cm, 13.35*cm, 1.6*cm,
                            leftPadding=0*cm, bottomPadding=0*cm,
                            rightPadding=0*cm, topPadding=0*cm)
        top_right_f.addFromList(top_content[:], canvas)
        # Draws the bottom frames (instructor information)
        bottom_content = []
        bottom_content.append(Paragraph(u"Signature du formateur (%s) :"
                                        % self.instructor_name,
                                        style_normal_left))
        bottom_left_f = Frame(1*cm, 1*cm, 13.35*cm, 0.5*cm,
                              leftPadding=0*cm, bottomPadding=0*cm,
                              rightPadding=0*cm, topPadding=0*cm)
        bottom_left_f.addFromList(bottom_content[:], canvas)
        bottom_right_f = Frame(15.35*cm, 1*cm, 13.35*cm, 0.5*cm,
                               leftPadding=0*cm, bottomPadding=0*cm,
                               rightPadding=0*cm, topPadding=0*cm)
        bottom_right_f.addFromList(bottom_content[:], canvas)
        # Puts back the canvas in its previous state
        canvas.restoreState()


class FeedbackCardPageTemplate(PageTemplate):
    """
    Class defining the page template used to draw the feedback cards.
    """
    def __init__(self, reference, title, template_id=""):
        """
        :parameter reference: Reference of the training session
        :type reference: unicode

        :parameter title: Title of the training session
        :type title: unicode
        """
        self.training_ref = reference
        self.training_title = title
        main_frames = [
            Frame(1*cm, 1*cm, 19*cm, 23.8*cm,
                  leftPadding=0*cm, bottomPadding=0*cm,
                  rightPadding=0*cm, topPadding=0*cm)
                      ]
        # Calls the base class initializer.
        PageTemplate.__init__(self, id=template_id, frames=main_frames,
                              pagesize=A4)

    def beforeDrawPage(self, canvas, document):
        """
        Overrides the method called before drawing on a new page of the PDF
        document. This method draws various static data on the page
        (logo, session reference, session title, instructor name).
        """
        # saves canvas state
        canvas.saveState()
        # the logo is not drawn through the frame because image as flowable
        # cannot be aligned on the left (they are always centered)
        from PIL import Image as PImage
        img = PImage.open(COMPANY_LOGO)
        initial_width, initial_height = img.size
        img_height  = 1.8*cm
        img_width = img_height * float(initial_width) / float(initial_height)
        canvas.drawInlineImage(img, 1*cm, 27*cm,
                               img_width, img_height)
        # Draws the top frame (title and session information)
        top_content = []
        top_content.append(Paragraph(u"<b>Feuille d'évaluation du cours</b>",
                                     style_title))
        top_content.append(Spacer(1, 0.75*cm))
        tit_para = Paragraph(u"Cours : %s" % self.training_title,
                             style_normal_left)
        ref_para = Paragraph(u"Référence : %s" % self.training_ref,
                             style_normal_left)
        tab = Table([ [tit_para, ref_para] ], [13*cm, 6*cm], None)
        tab.setStyle(
            TableStyle([ ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                         ('VALIGN',        (0,0), (-1,-1), 'TOP'),
                         ('LEFTPADDING',   (0,0), ( 0,-1), 0),
                         ('LEFTPADDING',   (1,0), (-1,-1), 0.5*cm),
                         ('RIGHTPADDING',  (0,0), ( 0,-1), 0.5*cm),
                         ('RIGHTPADDING',  (1,0), (-1,-1), 0),
                         ('TOPPADDING',    (0,0), (-1,-1), 0),
                         ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                       ])
                    )
        top_content.append(tab)
        top_f = Frame(1*cm, 25*cm, 19*cm, 1.9*cm,
                      leftPadding=0*cm, bottomPadding=0*cm,
                      rightPadding=0*cm, topPadding=0*cm)
        top_f.addFromList(top_content, canvas)
        # Puts back the canvas in its previous state
        canvas.restoreState()
