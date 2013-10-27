import exceptions
import csv
import json
import re

import logging
logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

# These are fields that are more or less "standard" 
UNITS = "unitsOrdered"
PRICE = "unitPrice"
AGENCY = "contractingAgency"
VENDOR = "vendor"
PSC = "psc"
DESCR = "productDescription"
LONGDESCR = "longDescription"
DATE = "orderDate"
AWARDIDIDV = "awardIdIdv"
DATASOURCE = "dataSource"

STANDARD_FIELDS = [UNITS,PRICE,AGENCY,VENDOR,PSC,DESCR,LONGDESCR,DATE,AWARDIDIDV]
# Need to create Semi-standard fields here...

MANUFACTURER_NAME = "Manufacturer Name"
MANUFACTURER_PART_NUMBER =    "Manufacturer Part Number"
BUREAU = "Bureau"
CONTRACT_NUMBER = "Contract Number"
TO_ZIP_CODE = "To Zip Code"
FROM_ZIP_CODE = "From Zip Code" 
UNIT_OF_ISSUE = "Unit of Issue"

SEMI_STANDARD_FIELDS = [MANUFACTURER_NAME,MANUFACTURER_PART_NUMBER,BUREAU,CONTRACT_NUMBER,TO_ZIP_CODE,FROM_ZIP_CODE,UNIT_OF_ISSUE]

def ensureZipCodeHasFiveDigits(zip):
    return zip.zfill(5)

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
    def __init__(self,adapter,raw,datasource):
        self.fields = None
        self.datasource = datasource
        self.dictionaryAdapter = adapter
        self.dict = self.getStandardDictionary(raw)

    def getStandardDictionary(self,rawTransaction):
        xdict = self.dictionaryAdapter(rawTransaction,self.datasource)
        xdict = self.cleanUpData(xdict)
        return xdict

    def cleanUpData(self,qdict):
        qdict[PRICE] = qdict[PRICE].replace("$","")
        # add a whitespace trim
        for key, value in qdict.iteritems():
            qdict[key] = value.strip();
        return qdict
    
    def getJSON(self):
        return json.dumps(self.dict)

    def getSearchMemento(self):
        return self.getJSON()

    # First check: we have to have a UnitPrice which is a number!
    def isValidTransaction(self):
        try:
            dummx =  float(self.dict[PRICE])
            dummy =  int(self.dict[UNITS])
            return True;
        except ValueError:
            return False;
    
class TransactionDirector:
    "Operations on the Universe of Transactions"
    def __init__(self):
        self.transactions = [];

    def addTransaction(self,name):
        self.transactions.append(name)

    def findAllMatching(self,pattern,psc_pattern):
        matches = []
        print "patterns"
        print pattern
        print psc_pattern
        for tr in self.transactions:
            matchesGeneral = False
            if ((pattern is None) or re.search(pattern, tr.getSearchMemento()) is not None):
                matchesGeneral = True
            matchesPSC = False
            if ((psc_pattern is None) or re.search(psc_pattern, tr.dict[PSC]) is not None):
                matchesPSC = True
            logger.info("matchs PSC, matchesGeneral"+str(matchesPSC)+"."+str(matchesGeneral)+"|"+tr.dict[PSC])
            if (matchesPSC and matchesGeneral):
                matches.append(tr)
        return matches
            

    
