# -*- coding: utf-8 -*-
"""
Module containing the XML reader.
"""
__docformat__ = "restructuredtext en"

from lxml.etree import parse
from entities import TrainingSession

def read_session(filename):
    """
    Reads a file describing a training session and returns a
    ``TrainingSession`` object.
    """
    trs = TrainingSession()
    tree = parse(filename)
    root = tree.getroot()
    if root.tag != u"training-session":
        raise Exception("Unknown XML format")
    trs.reference = root.findtext(u"reference", u"")
    trs.title = root.findtext(u"title", u"") 
    trs.instructor = root.findtext(u"instructor", u"")
    for xml_day in root.xpath(u"day"):
        if xml_day.text.strip() != u"":
            trs.days.append(xml_day.text.strip())
    for xml_person in root.xpath(u"attendee"):
        name = xml_person.findtext(u"name", u"")
        company = xml_person.findtext(u"company", u"")
        trs.attendees.append((name, company))
    return trs

