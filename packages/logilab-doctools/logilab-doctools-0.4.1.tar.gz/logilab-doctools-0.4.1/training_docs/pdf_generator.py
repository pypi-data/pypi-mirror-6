# -*- coding: utf-8 -*-
"""
Module containing the functions that can produce the PDF documents for the
training sessions.
"""
__docformat__ = "restructuredtext en"

from reportlab.platypus import BaseDocTemplate
from templates import AttendanceListPageTemplate, FeedbackCardPageTemplate
from flow_generators import (generate_attendance_list_flow,
                             generate_feedback_cards_flow)


def write_attendance_list(filename, session):
    """
    Writes a PDF file containing the attendance list for a training session.
    """
    page_templates = [ AttendanceListPageTemplate(session.reference,
                                                  session.title,
                                                  session.instructor,
                                                  template_id="Page")
                     ]
    pdf_doc = BaseDocTemplate(filename, pageTemplates=page_templates,
                              allowSplitting=1)
    pdf_doc.build(generate_attendance_list_flow(session))

def write_feedback_cards(filename, session):
    """
    Writes a PDF file containing the feedback cards for a training session.
    """
    page_templates = [ FeedbackCardPageTemplate(session.reference,
                                                session.title,
                                                template_id="Card")
                     ]
    pdf_doc = BaseDocTemplate(filename, pageTemplates=page_templates,
                              allowSplitting=1)
    pdf_doc.build(generate_feedback_cards_flow(session))
