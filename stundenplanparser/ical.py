'''
Created on 16.04.2014

@author: Christoph Gerneth
'''
from datetime import datetime
import sys

try:
    from icalendar import Calendar, Event
except ImportError:
    print """
    icalendar-library not found - no problem!
    use
    
    $ git clone https://github.com/collective/icalendar.git
    $ cd icalendar
    $ python setup.py install
    
    or install manually!
    """
    sys.exit()
    
    
class ICal(object):
    version = '2.0'
    def __init__(self, data_in, owner = "Student"):
        cal = Calendar()
        cal.add('prodid', '-//Stundenplan von %s //thi.de//' % owner)
        cal.add('description', "Stundenplan")
        cal.add('version', self.version)
        self.cal = cal
        self.data = data_in
    
    def write(self, output_file):
        for term in self.data:
            event = Event()
            event.add('dtstart', term.zeit_von)
            event.add('dtend', term.zeit_bis)
            event.add('summary', term.fach.pop().__repr__())
            event.add('location', term.raum)
            event.add('dtstamp', datetime.today())
            event['uid'] = str(term.__hash__())+'@haw-ingolstadt.de'
            event.add('priority', 1)
            self.cal.add_component(event)
            
        with open(output_file, 'wb') as f:
            f.write(self.cal.to_ical())
        