import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV

     
import logging
logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('/var/tmp/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

# Note: Josh Royko said all of this AwardIdIdv is or a particular GSA schedule
# Note: Highest priority is remove redundancy with FedBidAdapater,
# create "Standard Fields" adapter and "Custom Fields" adapter separately.

def getDictionaryFromOS2(raw):
    return { \
    UNITS : replaceUndumpableData(raw.data[16]), \
    PRICE : replaceUndumpableData(raw.data[19]), \
    AGENCY : replaceUndumpableData(raw.data[48]), \
    VENDOR : replaceUndumpableData(raw.data[64]),    \
# I know all of this data is office supplies---this may not be too accurate
# but it matches
    PSC : replaceUndumpableData('7510'),  \
    DESCR : replaceUndumpableData(raw.data[5]),   \
    # DANGER!  HACK!
    # I think the OS2 data has a better version than this!
    LONGDESCR : replaceUndumpableData(raw.data[5]),   \
    DATE : replaceUndumpableData(raw.data[1]), \
# I need to check this---Josh Royko told me in an email, but I don't really
# remember what he said
    AWARDIDIDV : replaceUndumpableData("GS Schedule-75 (maybe)"), \
# here begin some less-standard fields
# This data has significantly more fields--I am simply
# selecting the most salient.  I think the reality is this sort
# of analysis should be done in a crowd-source, "datapalooza" type approach.
    "contractNumber" : replaceUndumpableData(raw.data[0]), \
    "Revised Ord_date" : replaceUndumpableData(raw.data[1]), \
    "Report Month" : replaceUndumpableData(raw.data[3]),   \
    "Ord_num" : replaceUndumpableData(raw.data[4]),   \
    "Mfr_Name" : replaceUndumpableData(raw.data[6]),   \
    "Mfr_Part_No" : replaceUndumpableData(raw.data[9]), \
    "FSC" : replaceUndumpableData(raw.data[17]), \
    "Dbt_Crdt_Ind" : replaceUndumpableData(raw.data[36]), \
    "Tot_Recyc_Percent" : replaceUndumpableData(raw.data[42]), \
    "Dlvry_Method" : replaceUndumpableData(raw.data[43]), \
    "Pay_Method" : replaceUndumpableData(raw.data[56]), \
    "To_zip_code" : replaceUndumpableData(raw.data[60]), \
    "From_zip_code" : replaceUndumpableData(raw.data[61])  \
    }

def loadOS2FromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
   try:
        logger.error('FedBid reader opened:'+filename)
        transactions = []
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            logger.error('FedBid reader opened:'+filename)
            n = len(transactions)
            i = 0
            for row in reader:
                tr = RawTransaction("spud")
                tr.data = row;
                bt = BasicTransaction(adapter,tr)
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
