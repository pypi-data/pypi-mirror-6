# -*- coding: utf-8 -*-
"""
Module containing various useful things including the styles for the PDF
rendering.
"""
__docformat__ = "restructuredtext en"

from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import  TA_LEFT, TA_CENTER

# Defining paragraph styles used in PDF generation

style_title = ParagraphStyle("title")
style_title.fontSize = 15
style_title.fontName = "Helvetica"
style_title.alignment = TA_CENTER

style_normal_left = ParagraphStyle("normal_left")
style_normal_left.fontSize = 10
style_normal_left.firstLineIndent = -0.5*cm
style_normal_left.leftIndent = 0.5*cm
style_normal_left.alignment = TA_LEFT

style_normal_center = ParagraphStyle("normal_center")
style_normal_center.fontSize = 10
style_normal_center.firstLineIndent = -0.5*cm
style_normal_center.centerIndent = 0.5*cm
style_normal_center.alignment = TA_CENTER


