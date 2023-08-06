# -*- coding: utf-8 -*-
"""
Module containing the entities representing the data.
"""
__docformat__ = "restructuredtext en"


class TrainingSession:
    def __init__(self):
        self.reference = u""
        self.title = u""
        self.instructor = u""
        self.attendees = [] # (name, company)
        self.days = [] # unicode
