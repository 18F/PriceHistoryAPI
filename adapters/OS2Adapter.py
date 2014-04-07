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

# Note: Josh Royko said all of this AwardIdIdv is or a particular GSA schedule
# Note: Highest priority is remove redundancy with OS2Adapater,
# create "Standard Fields" adapter and "Custom Fields" adapter separately.

def getDictionaryFromOS2(raw,datasource):
    try:
# Choosing the "Charge Processing Date" as the official date"
        d = datetime.datetime.strptime(raw.data[57].strip(' \t\n\r'),"%m-%d-%Y")
        return { \
        DATASOURCE : datasource, \
        UNITS : replaceUndumpableData(raw.data[16]), \
        PRICE : replaceUndumpableData(raw.data[19]), \
        AGENCY : replaceUndumpableData(raw.data[48]), \
        VENDOR : replaceUndumpableData(raw.data[64]),    \
    # I know all of this data is office supplies---this may not be too accurate
    # but it matches
        PSC : replaceUndumpableData(raw.data[17]),  \
        DESCR : replaceUndumpableData(raw.data[5]),   \
        # DANGER!  HACK!
        # I think the OS2 data has a better version than this!
        LONGDESCR : replaceUndumpableData(raw.data[5]),   \
    # Choosing the "Charge Processing Date" as the official date"
        DATE : replaceUndumpableData(d.date().isoformat()), \
        AWARDIDIDV : replaceUndumpableData("GSA Schedule-75"), \
    # here begin some less-standard fields
    # This data has significantly more fields--I am simply
    # selecting the most salient.  I think the reality is this sort
    # of analysis should be done in a crowd-source, "datapalooza" type approach.

        "Order Number" : replaceUndumpableData(raw.data[4]),   \
        MANUFACTURER_NAME : replaceUndumpableData(raw.data[7]),   \
        "isAbitlityOne" : replaceUndumpableData(raw.data[8]),   \
        MANUFACTURER_PART_NUMBER : replaceUndumpableData(raw.data[10]), \
        "Revised SubCategory" : replaceUndumpableData(raw.data[13]), \
        "Revised Category" : replaceUndumpableData(raw.data[14]), \
        UNIT_OF_ISSUE : replaceUndumpableData(raw.data[15]), \
        "UNSPSC" : replaceUndumpableData(raw.data[18]), \
        "Revised Dbt_Crdt_ind" : replaceUndumpableData(raw.data[37]), \
        "EEP_Ind" : replaceUndumpableData(raw.data[38]), \
        "CPG_Ind" : replaceUndumpableData(raw.data[39]), \
        "Comp_Remain_Toner" : replaceUndumpableData(raw.data[40]), \
        "Post_Cons_Percent" : replaceUndumpableData(raw.data[41]), \
        "Tot_Recyc_Percent" : replaceUndumpableData(raw.data[42]), \
        "Dlvry_Method" : replaceUndumpableData(raw.data[43]), \
        "Freight Charge" : replaceUndumpableData(raw.data[44]), \
        "Shipping Weight" : replaceUndumpableData(raw.data[45]), \
        "Sub_Agency1" : replaceUndumpableData(raw.data[52]), \
        "Sub_Agency2" : replaceUndumpableData(raw.data[53]), \
        "Sub_Agency3" : replaceUndumpableData(raw.data[54]), \
        "MAJCOM" : replaceUndumpableData(raw.data[55]), \
        "DODACC" : replaceUndumpableData(raw.data[56]), \
        "Pay Date" : replaceUndumpableData(raw.data[57]), \
        "Charge Processing Date" : replaceUndumpableData(raw.data[62]), \
        "Transaction Number" : replaceUndumpableData(raw.data[63]), \
        "Revised Socio Status" : replaceUndumpableData(raw.data[66]), \
        CONTRACT_NUMBER : replaceUndumpableData(raw.data[68]), \
        "Revised Ord_date" : replaceUndumpableData(raw.data[1]), \
        "Report Month" : replaceUndumpableData(raw.data[3]),   \
        "Ord_num" : replaceUndumpableData(raw.data[4]),   \
        "FSC" : replaceUndumpableData(raw.data[17]), \
        "Dbt_Crdt_Ind" : replaceUndumpableData(raw.data[36]), \
        "Tot_Recyc_Percent" : replaceUndumpableData(raw.data[42]), \
        "Dlvry_Method" : replaceUndumpableData(raw.data[43]), \
        "Pay_Method" : replaceUndumpableData(raw.data[56]), \
        TO_ZIP_CODE : replaceUndumpableData(raw.data[60]), \
        FROM_ZIP_CODE : replaceUndumpableData(raw.data[61])  \
        }
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)      
        logger.error("don't know what went wrong here")
        return {}

def loadOS2FromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
   try:
        logger.error('OS2 reader opened:'+filename)
        transactions = []
        with open(filename, 'rb') as f:
            basename = os.path.basename(filename)
            reader = csv.reader(f)
            logger.error('OS2 reader opened:'+filename)
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
