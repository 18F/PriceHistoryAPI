import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV,DATASOURCE

from Transaction import ensureZipCodeHasFiveDigits,MANUFACTURER_NAME,MANUFACTURER_PART_NUMBER,BUREAU,CONTRACT_NUMBER,TO_ZIP_CODE,FROM_ZIP_CODE,UNIT_OF_ISSUE

import datetime
import calendar

import sys, traceback
import logging
import os

logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)

def tryToInferUnitsFromDescriptionOrDefaultToOne(descr):
    return "1"

def getDictionaryFromUSASpending(raw,datasource):
    try:
# Choosing the "Charge Processing Date" as the official date"
        d = datetime.datetime.strptime(raw.data[14].strip(' \t\n\r'),"%m/%d/%Y")
        return { \
        DATASOURCE : datasource, \
        DESCR : replaceUndumpableData(raw.data[31]),   \
        UNITS : tryToInferUnitsFromDescriptionOrDefaultToOne(replaceUndumpableData(raw.data[32])), \
        PRICE : replaceUndumpableData(raw.data[4]), \
        AGENCY : replaceUndumpableData(raw.data[5]), \
        VENDOR : replaceUndumpableData(raw.data[43]),    \
    # I know all of this data is office supplies---this may not be too accurate
    # but it matches
        PSC : replaceUndumpableData(raw.data[80]),  \
        "product_service_code" : replaceUndumpableData(raw.data[80]),  \
        "naics_code" : replaceUndumpableData(raw.data[109]),  \
        LONGDESCR : replaceUndumpableData(raw.data[31]),   \
        DATE : replaceUndumpableData(d.date().isoformat()), \

        TO_ZIP_CODE : replaceUndumpableData(raw.data[63]), \
        "street_address" : replaceUndumpableData(raw.data[52]), \
        "city" : replaceUndumpableData(raw.data[55]), \
        "state" : replaceUndumpableData(raw.data[56]), \
        "vendor_state_code" : replaceUndumpableData(raw.data[59]), \
        "congressionaldistrict" : replaceUndumpableData(raw.data[58]), \
        "duns_number" : replaceUndumpableData(raw.data[64]), \
        "phoneno" : replaceUndumpableData(raw.data[67]), \
        "extent_competed" : replaceUndumpableData(raw.data[103]), \
        "reason_not_competed" : replaceUndumpableData(raw.data[104]), \

        AWARDIDIDV : replaceUndumpableData("USASpending")   
        }
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)      
        logger.error("don't know what went wrong here")
        return {}

def loadUSASpendingFromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
   try:
        logger.error('USASpending reader opened:'+filename)
        transactions = []
        with open(filename, 'rb') as f:
            basename = os.path.basename(filename)
            reader = csv.reader(f)
            logger.error('USASpending reader opened:'+filename)
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
