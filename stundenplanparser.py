'''
Created on 28.03.2013

@note: Possible spelling errors are due to the wine.

@author: Christoph Gerneth
'''

import json
from datetime import datetime, date
import urllib
import urllib2
import re
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


class Fach(object):
    def __init__(self, name, dozent, kurzfrom):
        self.name = name.encode("utf-8")
        self.dozent = dozent.encode("utf-8")
        self.kurzform = kurzfrom

        
    def __repr__(self, *args, **kwargs):
        return "%s bei %s" % (self.name, self.dozent)
    
    def __eq__(self, other):
        #have to use both __hash__ and __eq__ to get set() working
        return True
    
    def __hash__(self):
        return hash((self.dozent, self.name, self.kurzform))

class Termin(object):
    '''
    @param fach: fach-object
    '''
    def __init__(self, fach, datum, von, bis, raum, kommentar=None):
        self.fach = fach
        self.date = datum
        self.raum = raum
        self.zeit_von = von
        self.zeit_bis = bis    
        self.comment = kommentar
    
    def __repr__(self):
        date = datetime.strftime(self.date, "%d.%B.%Y")
        von = datetime.strftime(self.zeit_von, "%H:%M")
        bis = datetime.strftime(self.zeit_bis, "%H:%M")
        return "%-15s von %s bis %s Uhr: %s" % (date, von, bis, self.fach)
    

class Timetableparser(object):
    
    def __init__(self):
        self.__faecher = set()
        self.__termine = []
        
    def read(self, username, password, fh):
        semester_id = self.getSemesterIDforDate()
        
        data = self.__parseHTML(username, password, semester_id, fh)
        faecher = json.loads(data)

        for fach in faecher["events7"]:
            try:
                f = fach[20]
                raum = f["raeume"].replace("in ", "")
                kommentar = f["kommentar"]
                name = f["fach_name"]
                kurzform = f["fach_kurzform"]
                dozent = f["dozenten"].replace("bei ", "")
                datum = datetime.strptime(f["datum"], "%d.%m.%Y").date()
                zeitbis = datetime.combine(datum, datetime.strptime(f["zeitbis"], "%H.%M").time())
                zeitvon = datetime.combine(datum, datetime.strptime(f["zeitvon"], "%H.%M").time())
            except KeyError:
                continue
            #serialize
            self.__faecher.add(Fach(name, dozent, kurzform))
            subject = self.__faecher.intersection(set([Fach(name, dozent, kurzform)]))
            term = Termin(subject, datum, zeitvon, zeitbis, raum, kommentar)
            #print "parsed", term
            self.__termine.append(term)
    
    def getSemesterIDforDate(self, sem_date=datetime.today()):
        '''calculate semester-id. Value changes for every semester'''
        today = sem_date
        
        ws = date(today.year, 9, 30)
        ss = date(today.year, 3, 15)
        semester_id = today.year - 1992 #offset
        
        if ss <= today <= ws:
            #sommersemester
            semester_id += 1
        elif ws < today:
            #naechstes semester im jahr
            semester_id += 2
                  
        return semester_id
        
        
    def __parseHTML(self, username, password, semester_id, fh="fhin"):
        
        url = "https://hiplan.haw-ingolstadt.de/stpl/index.php?FH=%s&Language=" % fh
        values = {"User": username,
                "userPassword": password,
                "mode": "login",
                "submitLogin":"Anmelden"}
        
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        
        session_id = re.findall(r"Session=[A-Za-z0-9]*", the_page)[0].split("=")[1]
        
        
        post2 = "https://hiplan.haw-ingolstadt.de/stpl/index.php?FH=%s&User=%s&Session=%s&Language=&sem=%s&mode=cbGridWochenplanDaten&pers=undefined"\
        % (fh, username, session_id, semester_id)
        
        req2 = urllib2.Request(post2)
        response2 = urllib2.urlopen(req2)
        output = response2.read()
        
        return output
        
          
    @property  
    def subjects(self):
        return self.__faecher
    
    @property
    def terms(self):
        return self.__termine
    
    def getTermsByDate(self, date):
        #return generator-object
        for termin in self.__termine:
            if termin.date == date:
                yield termin

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
            
        
        

            
if __name__ == "__main__":
    
    from optparse import OptionParser  
    
    usage = """
    convert your Timetable to a ical-file
    """
     
    parser = OptionParser(usage=usage)
    parser.add_option("-u", "--user", dest="user", help="your Username (e.g. if1184")
    parser.add_option("-p", "--pass", dest="passwd", help="your password")
    parser.add_option("-o", "--out", dest="output", help="your output.ical")
    parser.add_option("-f", dest="university", default="fhin", help="the university. e.g. fhin for Ingolstadt")
    
    (options, args) = parser.parse_args()
    
    x = Timetableparser()
    x.read(options.user, options.passwd, options.university)
    
    print "Subjects:"
    for subs in x.subjects:
        print subs
    print
        
    print "heute auf dem Plan:"
    table_today = []
    for term in x.getTermsByDate(datetime.today().date()):
        table_today.append(term)
    table_today.sort(key=lambda x: x.zeit_von, reverse=False)
    for term in table_today:
        print term
    
    out_ical = ICal(x.terms, options.user)
    out_ical.write(options.output)
        
    

