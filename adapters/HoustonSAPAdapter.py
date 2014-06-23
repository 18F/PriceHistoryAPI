import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV,DATASOURCE

from Transaction import ensureZipCodeHasFiveDigits,MANUFACTURER_NAME,MANUFACTURER_PART_NUMBER,BUREAU,CONTRACT_NUMBER,TO_ZIP_CODE,FROM_ZIP_CODE,UNIT_OF_ISSUE

import datetime
import calendar

import sys, traceback
import logging
import os
from decimal import *
import math

logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)

def tryToInferUnitsFromDescriptionOrDefaultToOne(descr):
    return "1"

def convertFullFormatNumber(numberRepresentation):
    x = str(Decimal(numberRepresentation.replace('$','').replace(',','').replace('(','').replace(')','')))
    return x

def convertUnitsToClosestInteger(units):
    x = str(int(round(float(units.replace(',','')))))
    return x

def getDictionaryFromHoustonSAP(raw,datasource):
    try:
# Choosing the "Charge Processing Date" as the official date"
        d = datetime.datetime.strptime(raw.data[3].strip(' \t\n\r'),"%m/%d/%Y")
        return { \
        DATASOURCE : datasource, \
        LONGDESCR : replaceUndumpableData(raw.data[9]),   \
        DATE : replaceUndumpableData(d.date().isoformat()), \
        "Invoice Id" : replaceUndumpableData(raw.data[0]), \
        "Invoice Line Item Id" : replaceUndumpableData(raw.data[1]), \
        "Invoice Doc Type Id - Descr" : replaceUndumpableData(raw.data[2]), \
        "Invoice Date" : replaceUndumpableData(raw.data[3]), \
        "Invoice Post Date" : replaceUndumpableData(raw.data[4]), \
        "Fisc Year" : replaceUndumpableData(raw.data[5]), \
        "Invoice Vendor Id" : replaceUndumpableData(raw.data[6]), \
        VENDOR : replaceUndumpableData(raw.data[7]), \
        "Material Id" : replaceUndumpableData(raw.data[8]), \
        DESCR : replaceUndumpableData(raw.data[9]), \
        "Material Group ID" : replaceUndumpableData(raw.data[10]), \
        "Material Group Desc" : replaceUndumpableData(raw.data[11]), \
        "Material Class ID" : replaceUndumpableData(raw.data[12]), \
        "Material Class Desc" : replaceUndumpableData(raw.data[13]), \
        "Invoice Line Item Amount" : replaceUndumpableData(raw.data[14]), \
        PRICE : replaceUndumpableData(convertFullFormatNumber(raw.data[14])), \
        UNITS : replaceUndumpableData(convertUnitsToClosestInteger(raw.data[15])), \
        "Uom Id" : replaceUndumpableData(raw.data[16]), \
        UNIT_OF_ISSUE : replaceUndumpableData(raw.data[17]), \
        "PO" : replaceUndumpableData(raw.data[18]), \
        "PO Line" : replaceUndumpableData(raw.data[19]), \
        "PO Doc Type" : replaceUndumpableData(raw.data[20]), \
        "Purch Org Id" : replaceUndumpableData(raw.data[21]), \
        "Purch Org Descr" : replaceUndumpableData(raw.data[22]), \
        "Ext Purch Itm Catg Id - Descr" : replaceUndumpableData(raw.data[23]), \
        "PO Short Text" : replaceUndumpableData(raw.data[24]), \
        "PO Vendor" : replaceUndumpableData(raw.data[25]), \
        AGENCY : replaceUndumpableData(raw.data[26]), \
        "PO Purch Grp" : replaceUndumpableData(raw.data[27]), \
        "OA" : replaceUndumpableData(raw.data[28]), \
        AWARDIDIDV : replaceUndumpableData(raw.data[22])   
        }
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)      
        logger.error("don't know what went wrong here")
        return {}

def loadHoustonSAPFromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
   try:
        logger.error('HoustonSAP reader opened:'+filename)
        transactions = []
        with open(filename, 'rb') as f:
            basename = os.path.basename(filename)
            reader = csv.reader(f)
            logger.error('USASpending reader opened:'+filename)
            n = len(transactions)
            i = 0
            notFoundFirstRecord = True
            for row in reader:
                tr = RawTransaction("spud")
                tr.data = row;
                try:
                    if (notFoundFirstRecord):
                        result = False
                        notFoundFirstRecord = False;
                    else:
                        bt = BasicTransaction(adapter,tr,basename)
                        if (pattern):
                            result = re.search(pattern, bt.getSearchMemento())
                        else:
                            result = True
                    if (result):
                        if (bt.isValidTransaction()):
                            transactions.append(bt)
                            i = i + 1
                    if (i+n) > LIMIT_NUM_MATCHING_TRANSACTIONS:
                        break
                except:
                    print "Error on this row:"
                    print repr(row)
        return transactions
   except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
