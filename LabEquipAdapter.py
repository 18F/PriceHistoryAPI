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
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

def getDictionaryFromLabEquipment (raw, datasource):
    try:
        d = datetime.datetime.strptime(raw.data[21].strip(' \t\n\r'),"%m/%d/%Y")
        return { \
         DATASOURCE : datasource, \
         UNITS : replaceUndumpableData(raw.data[37]), \
         PRICE : replaceUndumpableData(raw.data[38]), \
         AGENCY : replaceUndumpableData(raw.data[1]), \
         VENDOR : replaceUndumpableData(raw.data[29]),    \
         PSC : replaceUndumpableData(raw.data[13]),  \
         DESCR : replaceUndumpableData(raw.data[35]),   \
         LONGDESCR : replaceUndumpableData(raw.data[36]),   \
         DATE : replaceUndumpableData(d.date().isoformat()), \
         AWARDIDIDV : replaceUndumpableData(raw.data[19]), \
        "Point of Contact" : replaceUndumpableData(raw.data[2]),   \
        "Buyer_Division" : replaceUndumpableData(raw.data[3]),   \
        "Category" :replaceUndumpableData(raw.data[24]),   \
        "Seller Type" : replaceUndumpableData(raw.data[25]),   \
        "Seller Award Type" : replaceUndumpableData(raw.data[26]),   \
        "Purchase Description" : replaceUndumpableData(raw.data[31]),   \
        "Set Aside Type" : replaceUndumpableData(raw.data[32]),   \
        "Commodity Type" : replaceUndumpableData(raw.data[12]),   \
        }
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)      
        logger.error("don't know what went wrong here")
        
    #other data fields can still be included    
def loadLabequipmentFromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
    try:
        transactions = []
        with open(filename, 'rb') as f:
            basename = os.path.basename (filename)
            reader = csv.reader (f)
            logger.info('Lab Equipment reader opened:'+filename)
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
        logger.info('number returned:'+str(i))
        return transactions                
    except IOError as e:
         logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
         print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)      
        logger.error("don't know what went wrong here2")
            
