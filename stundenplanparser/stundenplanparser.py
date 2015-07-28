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
        data = self.__parseHTML(username, password, fh)
        faecher = json.loads(data)

        for fach in faecher["events"]:
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
    

    def __parseHTML(self, username, password, fh="fhin"):
        
        url = "https://www2.primuss.de/stpl/index.php?FH=%s&Language=" % fh
        values = {"User": username,
                "userPassword": password,
                "mode": "login",
                "submitLogin":"Anmelden"}
        
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        
        session_id = re.findall(r"Session\" value=\"[A-Za-z0-9]*", the_page)[0].split("=\"")[1]
        semester_id = re.findall(r"sem=[0-9]*", the_page)[0].split("=")[1]
        
        post2 = "https://www2.primuss.de/stpl/index.php?FH=%s&User=%s&Session=%s&Language=&sem=%s&mode=cbGridWochenplanDaten&pers=undefined"\
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
        #return generator-object @TODO: filter-function and return list
        for termin in self.__termine:
            if termin.date == date:
                yield termin


    

