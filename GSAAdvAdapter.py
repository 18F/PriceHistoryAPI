import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV,DATASOURCE
     
import os
     
import logging
logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

# Note: Josh Royko said all of this AwardIdIdv is or a particular GSA schedule
# Note: Highest priority is remove redundancy with GSAAdvAdapater,
# create "Standard Fields" adapter and "Custom Fields" adapter separately.

def getDictionaryFromGSAAdv(raw,datasource):
    return { \
    DATASOURCE : datasource, \
    UNITS : replaceUndumpableData(raw.data[3]), \
    PRICE : replaceUndumpableData(raw.data[2]), \
    AGENCY : replaceUndumpableData(raw.data[10]), \
    VENDOR : replaceUndumpableData(raw.data[5]),    \
# We are loading the "SIN" special item number field as the PSC for now.
    PSC : replaceUndumpableData(raw.data[14]),  \
    DESCR : replaceUndumpableData(raw.data[7]),   \
    LONGDESCR : replaceUndumpableData(raw.data[8]),   \
    DATE : replaceUndumpableData(raw.data[6]), \
    AWARDIDIDV : replaceUndumpableData(raw.data[13]), \

# here begin some less-standard fields
# This data has significantly more fields--I am simply
# selecting the most salient.  I think the reality is this sort
# of analysis should be done in a crowd-source, "datapalooza" type approach.
    "Manufacturer Name" : replaceUndumpableData(raw.data[1]), \
    "Manufacturer Part Number" : replaceUndumpableData(raw.data[0]), \
    "Bureau" : replaceUndumpableData(raw.data[11]),   \
    "Contract Number" : replaceUndumpableData(raw.data[12]),   \
    "To Zip Code" : replaceUndumpableData(raw.data[16]), \
    "From Zip Code" : replaceUndumpableData(raw.data[15])  \
    }

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
        return transactions
   except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
