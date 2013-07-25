import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE

import logging
logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('/var/tmp/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)


def getDictionaryFromFedBid(raw):
    return { \
    UNITS : replaceUndumpableData(raw.data[7]) , \
    PRICE : replaceUndumpableData(raw.data[8]), \
    AGENCY : replaceUndumpableData(raw.data[0]) , \
    VENDOR : replaceUndumpableData(raw.data[2]) , \
    PSC : replaceUndumpableData(raw.data[4]) ,  \
    DESCR : replaceUndumpableData(raw.data[5]+'  Additional Info:'+raw.data[6]),   \
# The FedBid data doesn't have dates. 
    DATE : "",   \
# here begin some less-standard fields
    "commodityType" : replaceUndumpableData(raw.data[3]) , \
    "awardIdIdv" : replaceUndumpableData(raw.data[1]) \
    }


# I think this will be better made into a pure function and
# perhaps actually separated into particular formats (to
# allow more override flexibility, like skipping the first row.)
def loadFedBidFromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
    try:
        transactions = []
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            logger.info('FedBid reader opened:'+filename)
            n = len(transactions)
            i = 0
            notFoundFirstRecord = True
            for row in reader:
                tr = RawTransaction("spud")
                tr.data = row;
                bt = BasicTransaction(adapter,tr)
                if (pattern):
                    result = re.search(pattern, bt.getSearchMemento())
                else:
                    result = True
# we skip the first record, this is for FedBid, needs to be
# adapter specific
                if (notFoundFirstRecord):
                    result = False
                    notFoundFirstRecord = False;
                if (result):
                    if (bt.isValidTransaction()):
                        transactions.append(bt)
                        i = i + 1

                if (i+n) > LIMIT_NUM_MATCHING_TRANSACTIONS:
                    break
        return transactions                
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
