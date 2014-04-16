'''
Created on 16.04.2014

@author: Christoph Gerneth
'''
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from optparse import OptionParser
from datetime import datetime

from stundenplanparser.stundenplanparser import Timetableparser



usage = """
Zeige deinen Tagesstundenplan an
"""
parser = OptionParser(usage=usage)
parser.add_option("-u", "--user", dest="user", help="your Username (e.g. if1184")
parser.add_option("-p", "--pass", dest="passwd", help="your password")
parser.add_option("-f", dest="university", default="fhin", help="the university. e.g. fhin for Ingolstadt")

(options, args) = parser.parse_args()

x = Timetableparser()
x.read(options.user, options.passwd, options.university)


print "Deine Faecher dieses Semester:"
for num, subs in enumerate(x.subjects):
    print "%02i: %s" % (num, subs)
print
    
print "Heute auf dem Plan:"
table_today = []
for term in x.getTermsByDate(datetime.today().date()):
    table_today.append(term)
table_today.sort(key=lambda x: x.zeit_von, reverse=False)
for term in table_today:
    print term

