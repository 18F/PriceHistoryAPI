import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV,DATASOURCE

import datetime
import calendar

import sys, traceback
import logging
import os

logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

def getDictionaryFromStandard(raw,datasource):
    logger.errr('RAW:'+repr(raw))
    try:
        d = datetime.datetime.strptime(raw.data[21].strip(' \t\n\r'),"%m/%d/%Y")
        return { \
           DATASOURCE : datasource, \
           UNITS : replaceUndumpableData(raw.data[37]) , \
           PRICE : replaceUndumpableData(raw.data[38]), \
           AGENCY : replaceUndumpableData(raw.data[3]) , \
           VENDOR : replaceUndumpableData(raw.data[29]) , \
           PSC : replaceUndumpableData(raw.data[13]) ,  \
           DESCR : replaceUndumpableData(raw.data[24]),   \
           LONGDESCR : replaceUndumpableData(raw.data[35]) , \
    # This needs to be put in a standard format and sorted properly.
           DATE : replaceUndumpableData(d.date().isoformat()), \
    # here begin some less-standard fields
           AWARDIDIDV : replaceUndumpableData(raw.data[19]) \
          }
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)      
        logger.error("don't know what went wrong here")
        return {}

def loadFromCSVString(csv_string,adapter):
        transactions = []
        reader = csv.reader(csv_string.splitlines())
        n = len(transactions)
        i = 0
        notFoundFirstRecord = True
        for row in reader:
            logger.error("row ="+repr(row))            
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
        logger.info('number returned:'+str(i))
        return transactions                

