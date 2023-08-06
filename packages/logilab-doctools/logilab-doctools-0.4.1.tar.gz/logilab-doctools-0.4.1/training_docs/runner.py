# -*- coding: utf-8 -*-
"""
Module containing the function that can produce the two PDF documents
(attendance list and set of feedback cards for a training session described in
an XML file.
"""
__docformat__ = "restructuredtext en"

from reader import read_session
from pdf_generator import write_attendance_list, write_feedback_cards

def produce_docs(session_filename,
                 attendance_list_filename, feedback_cards_filename):
    """
    Produces the PDF documents necessary for a training session. These
    documents are: an attendance list and a set of feedback cards.

    :parameter session_filename: name of the XML file containing the
                                description of the training session.
    :type session_filename: str

    :parameter attendance_list_filename:
        name of the PDF file that will contain the attendance list. This file
        is produced by this function.
    :type attendance_list_filename: str

    :parameter feedback_cards_filename:
        name of the PDF file that will contain the set of feebback cards. This
        file is produced by this function.
    :type feedback_cards_filename: str
    """
    trn_sess = read_session(session_filename)
    write_attendance_list(attendance_list_filename, trn_sess)
    write_feedback_cards(feedback_cards_filename, trn_sess)


if __name__ == "__main__":
    import sys
    print sys.argv
    try:
        session_filename = sys.argv[1]
    except IndexError:
        sys.stderr.write("Usage: python runner.py my-session.xml\n")
        sys.exit(1)
    produce_docs(session_filename,
                 "liste-presence.pdf", "fiches-evaluation.pdf")
