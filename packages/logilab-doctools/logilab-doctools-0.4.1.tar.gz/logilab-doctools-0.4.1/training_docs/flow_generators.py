# -*- coding: utf-8 -*-
"""
Module containing the flow generators that produce the contents of the PDF
documents.
"""
__docformat__ = "restructuredtext en"

from reportlab.lib.units import cm
from reportlab.lib.colors import black
from reportlab.platypus import (Paragraph, Table, TableStyle, Spacer,
                                FrameBreak, PageBreak)

from utils import style_normal_left, style_normal_center
from xml.sax.saxutils import escape

def generate_attendance_list_flow(session):
    """
    Generates the content of a PDF attendance list for a training session.
    """
    flow = []
    for person, company in session.attendees:
        flow.append(FrameBreak())
        # Attendee name and company
        name_para = Paragraph(u"Nom : <b>%s</b>" % escape(person),
                              style_normal_left)
        company_para = Paragraph(u"Société : <b>%s</b>" % escape(company),
                                 style_normal_left)
        attendee_tab = Table([ [name_para, company_para] ],
                             [7.35*cm, 6*cm], None)
        attendee_tab.setStyle(
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
        flow.append(attendee_tab)
        flow.append(Spacer(1, 0.1*cm))
        # Signatures table
        content = [ [ Paragraph(u"Date", style_normal_center),
                      Paragraph(u"Signature", style_normal_center),
                      Paragraph(u"", style_normal_center),
                      ],
                    [ Paragraph(u"", style_normal_center),
                      [Paragraph(u"matin", style_normal_center),
                       Paragraph(u"09h00 - 12h30", style_normal_center),],
                      [Paragraph(u"après-midi", style_normal_center),
                       Paragraph(u"13h30 - 17h00", style_normal_center),]
                      ],
                  ]
        content.extend([ [day, Spacer(1, 1*cm), Spacer(1, 1*cm)]
                         for day in session.days])
        sign_tab = Table(content, [5.35*cm, 4*cm, 4*cm], None)
        sign_tab.setStyle(
            TableStyle([ ('ALIGN',         (0,0), (-1, 0), 'CENTER'),
                         ('ALIGN',         (0,1), (-1,-1), 'LEFT'),
                         ('SPAN',          (1,0), (-1, 0)),
                         ('SPAN',          (0,0), (0, 1)),
                         ('VALIGN',        (0,0), (1, 1), 'MIDDLE'),
                         ('VALIGN',        (0,1), (-1,-1), 'MIDDLE'),
                         ('LEFTPADDING',   (0,0), (-1,-1), 0.2*cm),
                         ('RIGHTPADDING',  (0,0), (-1,-1), 0.2*cm),
                         ('TOPPADDING',    (0,0), (-1,-1), 0.2*cm),
                         ('BOTTOMPADDING', (0,0), (-1,-1), 0.2*cm),
                         ('BOX',           (0,0), (-1,-1), 0.50, black),
                         ('INNERGRID',     (0,0), (-1,-1), 0.25, black),
                       ])
                    )
        flow.append(sign_tab)
    if flow:
        # Removes first frame break
        flow.pop(0)
    return flow


def generate_feedback_cards_flow(session):
    """
    Generates the content of a PDF set of feedback cards for a training
    session.
    """
    flow = []
    for person, company in session.attendees:
        flow.append(PageBreak())
        # Attendee name and company
        name_para = Paragraph(u"Nom : <b>%s</b>" % escape(person),
                              style_normal_left)
        company_para = Paragraph(u"Société : <b>%s</b>" % escape(company),
                                 style_normal_left)
        attendee_tab = Table([ [name_para, company_para] ],
                             [10*cm, 9*cm], None)
        attendee_tab.setStyle(
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
        flow.append(attendee_tab)
        flow.append(Spacer(1, 0.5*cm))
        # Signatures table
        content = []
        for title in [u"Support de cours", u"Contenu du cours",
                      u"Exercices", u"Autres"]:
            content.append([ [Paragraph(title, style_normal_left),
                              Spacer(1, 4.5*cm)] ])
        feedback_tab = Table(content, [19*cm], None)
        feedback_tab.setStyle(
            TableStyle([ ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                         ('VALIGN',        (0,0), (-1,-1), 'TOP'),
                         ('LEFTPADDING',   (0,0), (-1,-1), 0.2*cm),
                         ('RIGHTPADDING',  (0,0), (-1,-1), 0.2*cm),
                         ('TOPPADDING',    (0,0), (-1,-1), 0.2*cm),
                         ('BOTTOMPADDING', (0,0), (-1,-1), 0.2*cm),
                         ('BOX',           (0,0), (-1,-1), 0.50, black),
                         ('INNERGRID',     (0,0), (-1,-1), 0.25, black),
                       ])
                    )
        flow.append(feedback_tab)
    if flow:
        # Removes first page break
        flow.pop(0)        
    return flow

