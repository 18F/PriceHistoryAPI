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
    logger.error('RAW:'+repr(raw.data))
    try:
#        d = datetime.datetime.strptime(raw.data[21].strip(' \t\n\r'),"%m/%d/%Y")
        d = datetime.datetime.today()
        logger.error('RAW0:'+replaceUndumpableData(raw.data[0]))
        logger.error('RAW1:'+replaceUndumpableData(raw.data[1]))
        logger.error('RAW2:'+replaceUndumpableData(raw.data[2]))
        logger.error('RAW3:'+replaceUndumpableData(raw.data[3]))
        logger.error('RAW4:'+replaceUndumpableData(raw.data[4]))
        logger.error('RAW5:'+replaceUndumpableData(raw.data[5]))
        logger.error('RAW6:'+replaceUndumpableData(raw.data[6]))
        logger.error('RAW7:'+replaceUndumpableData(raw.data[7]))
        logger.error('RAW8:'+replaceUndumpableData(raw.data[8]))
        return { \
            UNITS : replaceUndumpableData(raw.data[0]),\
            PRICE : replaceUndumpableData(raw.data[1]),\
            AGENCY : replaceUndumpableData(raw.data[2]),\
            VENDOR : replaceUndumpableData(raw.data[3]),\
            PSC : replaceUndumpableData(raw.data[4]),\
            DESCR : replaceUndumpableData(raw.data[5]),\
            LONGDESCR : replaceUndumpableData(raw.data[6]),\
            DATE : replaceUndumpableData(raw.data[7]),\
            AWARDIDIDV  : replaceUndumpableData(raw.data[8]),\
    # This needs to be put in a standard format and sorted properly.
            DATE : replaceUndumpableData(d.date().isoformat()) \
          }
    except:
        logger.error("don't know what went wrong here"+repr(sys.exc_info()[0]))
        return {}

def loadFromCSVString(csv_string,adapter,basename):
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
                bt = BasicTransaction(adapter,tr,basename)
                logger.error('BT:'+repr(bt))
#                logger.flush
#                logger.error('AT:'+repr(float(bt.dict[PRICE])))
#                logger.error('XT:'+repr(int(bt.dict[UNITS])))
#                if (bt.isValidTransaction()):
                transactions.append(bt)
                i = i + 1
            except:
                logger.error('ERROR:'+repr(sys.exc_info()[0]))
                print "error "+repr(sys.exc_info()[0])
                print "Error on this row:"
                print repr(row)
        logger.error('number returned:'+str(i))
        return transactions                

