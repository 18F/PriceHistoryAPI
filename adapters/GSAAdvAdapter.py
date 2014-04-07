import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV,DATASOURCE

from Transaction import ensureZipCodeHasFiveDigits,MANUFACTURER_NAME,MANUFACTURER_PART_NUMBER,BUREAU,CONTRACT_NUMBER,TO_ZIP_CODE,FROM_ZIP_CODE,UNIT_OF_ISSUE

import datetime     

import sys, traceback
import logging
import os

logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

def getDictionaryFromGSAAdv(raw,datasource):
    try:
        d = datetime.datetime.strptime(raw.data[6].strip(' \t\n\r'),"%b %d %Y")
        return { \
            DATASOURCE : datasource, \
            UNITS : replaceUndumpableData(raw.data[3]), \
            PRICE : replaceUndumpableData(raw.data[2]), \
            AGENCY : replaceUndumpableData(raw.data[10]), \
            VENDOR : replaceUndumpableData(raw.data[5]),    \
        # We are loading the "SIN" special item number field as the PSC for now.
        # I don't think this data contains a PSC code!
#            PSC : '',  \
            DESCR : replaceUndumpableData(raw.data[7]),   \
            LONGDESCR : replaceUndumpableData(raw.data[8]),   \
            DATE : replaceUndumpableData(d.date().isoformat()), \
            AWARDIDIDV : "GSA Advantage", \
            "GSA Schedule Number" : replaceUndumpableData(raw.data[13]),\
            "Special Item Number" : replaceUndumpableData(raw.data[14]),\
            UNIT_OF_ISSUE : replaceUndumpableData(raw.data[9]),\
            MANUFACTURER_NAME : replaceUndumpableData(raw.data[1]), \
            MANUFACTURER_PART_NUMBER : replaceUndumpableData(raw.data[0]), \
            BUREAU : replaceUndumpableData(raw.data[11]),   \
            CONTRACT_NUMBER : replaceUndumpableData(raw.data[12]),   \
            TO_ZIP_CODE : replaceUndumpableData(ensureZipCodeHasFiveDigits(raw.data[16])), \
            FROM_ZIP_CODE : replaceUndumpableData(ensureZipCodeHasFiveDigits(raw.data[15]))  \
        }
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)      
        logger.error("don't know what went wrong here")
        return {}


def loadGSAAdvFromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
   try:
        logger.error('GSAAdv reader opened:'+filename)
        transactions = []
        with open(filename, 'rb') as f:
            basename = os.path.basename(filename)
            reader = csv.reader(f)
            logger.error('GSAAdv reader opened:'+filename)
            n = len(transactions)
            i = 0
            for row in reader:
                tr = RawTransaction("spud")
                tr.data = row;
                try:
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
