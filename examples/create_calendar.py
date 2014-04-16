'''
Created on 16.04.2014

@author: Christoph Gerneth
'''

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from optparse import OptionParser
from stundenplanparser.stundenplanparser import Timetableparser
from stundenplanparser.ical import ICal


usage = """
erstelle deinen Stundenplan als ical-datei.
"""
parser = OptionParser(usage=usage)
parser.add_option("-u", "--user", dest="user", help="your Username (e.g. if1184")
parser.add_option("-p", "--pass", dest="passwd", help="your password")
parser.add_option("-f", dest="university", default="fhin", help="the university. e.g. fhin for Ingolstadt")
parser.add_option("-o", "--out", dest="output", help="your output.ics")

(options, args) = parser.parse_args()

x = Timetableparser()
x.read(options.user, options.passwd, options.university)

out_ical = ICal(x.terms, options.user)
out_ical.write(options.output)