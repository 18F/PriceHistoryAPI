import exceptions
import csv
import json
import re

import logging
logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('/var/tmp/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

# These are fields that are more or less "standard"        
UNITS = "unitsOrdered"
PRICE = "unitPrice"
AGENCY = "contractingAgency"
VENDOR = "vendor"
PSC = "psc"
DESCR = "productDescription"
DATE = "orderDate"

def parseFormatVersion(filename):
    match = re.search(r"(\w+)-pppifver-(\w+)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+).csv",filename)
    if not match:
        return None
    else:
        return match.group(3)


def dumpOrReturnWarning(str):
    try:
        return json.dumps(str)
    except UnicodeDecodeError:
        return json.dumps("Bad Data, this string had non Unicode characters.")

# Having to call this function is a significant performance hit.
# It would be better to find the offensive data and remove it or
# fix it in our data files.  I may try to do that eventually.
def replaceUndumpableData(str):
    try:
        json.dumps(str)
        return str
    except UnicodeDecodeError:
        return "Bad Data, this string had non Unicode characters."
    
class RawTransaction:
    "Represents an Individual Transaction as read from a file"
    def __init__(self,name):
        self.data = None

class BasicTransaction:
    "A Dictionary of Partial scructured Data"
    def __init__(self,adapter,raw):
        self.fields = None
        self.dictionaryAdapter = adapter
        self.dict = self.getStandardDictionary(raw)

    def getStandardDictionary(self,rawTransaction):
        xdict = self.dictionaryAdapter(rawTransaction)
        xdict = self.cleanUpData(xdict)
        return xdict

    def cleanUpData(self,qdict):
        qdict['unitPrice'] = qdict['unitPrice'].replace("$","")
        return qdict
    
    def getJSON(self):
        return json.dumps(self.dict)

    def getSearchMemento(self):
        return self.getJSON()

    # First check: we have to have a UnitPrice which is a number!
    def isValidTransaction(self):
        try:
            dummx =  float(self.dict["unitPrice"])
            dummy =  int(self.dict["unitsOrdered"])
            return True;
        except ValueError:
            return False;
    
class TransactionDirector:
    "Operations on the Universe of Transactions"
    def __init__(self):
        self.transactions = [];

    def addTransaction(self,name):
        self.transactions.append(name)

    def findAllMatching(self,pattern):
        matches = []
        for tr in self.transactions:
            if pattern:
                result = re.search(pattern, tr.getSearchMemento())
                if (result):
                    matches.append(tr)
            else:
                matches.append(tr)
        return matches
            

    
