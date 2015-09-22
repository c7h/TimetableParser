'''
Created on 28.03.2013

@note: Possible spelling errors are due to the wine.

@author: Christoph Gerneth
'''

import json
from datetime import datetime, date
import re
import requests



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
    
class LoginFailedException(Exception):
    pass

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
        
        url = "https://www2.primuss.de/stpl/login.php"
        values = {
                "user": username,
                "pwd": password,
                "mode": "login",
                "fh": fh,
                "lang": "de",
                "submitLogin":"Anmelden"
                }
        
        response = requests.post(url, data=values, params={"FH": fh, "Lang": "de"})
        the_page = response.text

        session_id_list = re.findall(r"(?:name\=\"Session\".{1,5}value\=\")([A-Za-z0-9]+)(?:\")", the_page)
        if len(session_id_list) == 0:
            #no session_id found... login failed?
            raise LoginFailedException("could not login")
        else:
            session_id = session_id_list.pop()

        semester_id = re.findall(r"sem=[0-9]*", the_page)[0].split("=")[1]
        
        post2_get_params = {
                "FH":fh, 
                "sem": semester_id, 
                "method": "list", 
                "Language": "",
                }

        form_data = {"showdate":"9/30/2015",
                    "viewtype":"week",
                    "timezone":"-5",
                    "Session":session_id,
                    "User":username,
                    "mode":"calendar",
                    "pers":"",}

        post2 = requests.post("https://www3.primuss.de/stpl/index.php", params=post2_get_params, data=form_data)
        output = post2.text
        
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

