import Transaction
import time

# Note: For now, these are explict imports.
# Evntually, we want to make this automatic, and essentially
# create a dynamic array of adapters and loaders based on
# what we find in some directory so that it is easily
# extendable.  But that would be over-engineering if we did it now.
from FedBidAdapter import getDictionaryFromFedBid,loadFedBidFromCSVFile
from OS2Adapter import getDictionaryFromOS2,loadOS2FromCSVFile
from os import listdir
from os.path import isfile, join
import re

import logging
logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('/var/tmp/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)


# This is a little dangerous.
# I'm going to try to speed things up by caching the TransactionDirector
# in the a global variable.
# Since the behavior of the depends a lot on the WebServer process
# model, it is hard to understand how this works.  However,
# we have on our side the fact that this is essentially a read-only
# process at the scale we are currently considering.

globalTransactionDir = None
turnOnGlobalCache = True

# If we have everything in memory, I belive we
# can compute a huge number of matches.  However,
# we can't afford to send everything back to the browser...
# Actually, even better would be to make this limit a part of
# the API call.
LIMIT_NUM_RETURNED_TRANSACTIONS = 5000
# This is simple.  More sophisticated systems will be possible.
# This is a significatn limit on the number of records returned.
LIMIT_NUM_MATCHING_TRANSACTIONS = 5000*1000


def loadDirectory(dirpath,pattern):
    onlyfiles = [ f for f in listdir(dirpath) if isfile(join(dirpath,f)) ]
    transactions = []
    onlycsvfiles = [ f for f in onlyfiles if re.search(".csv$",f)]
    for filename in onlycsvfiles:
        if len(transactions) > LIMIT_NUM_MATCHING_TRANSACTIONS:
            break
        version = Transaction.parseFormatVersion(filename)
        if not version:
             logger.error('File in wrong format: '+dirpath+filename)
        else:
            # FedBid data has number 1
            # This would be better with a functional "cond" type operator
            adapter = None
            logger.error('version:'+version)
            if (version == '1'):
                adapter = getDictionaryFromFedBid
                transactions.extend(loadFedBidFromCSVFile(dirpath+"/"+filename,\
                     pattern, adapter,LIMIT_NUM_MATCHING_TRANSACTIONS))
            elif (version == '2'):
                adapter = getDictionaryFromOS2
                transactions.extend(loadOS2FromCSVFile(dirpath+"/"+filename,\
                     pattern, adapter,LIMIT_NUM_MATCHING_TRANSACTIONS))
            else:
                logger.error('Unknown version')
                raise Exception('Unknown Format Version')

            logger.info('Number Transactions Read From Directory' \
                  +str(len(transactions)))

    return transactions

# mod_wsgi pipe output to the error log.  The Bottle webserver doesn't,
# so this difference can be a little confusing.
def searchApi(pathToData,search_string,psc_pattern):
    global globalTransactionDir
    localTransactionDir = None
    
    timeSearchBegin = time.clock()

    transaction = None

    if turnOnGlobalCache:
        if (globalTransactionDir is None):
            print "Using cache."
            t0 = time.clock()
            globalTransactionDir = Transaction.TransactionDirector()
            # it would be better to control whether it is loaded,
            # but this should work
            globalTransactionDir.transactions = loadDirectory(pathToData,None)
            numRows = len(globalTransactionDir.transactions)
            print "Time To Load ALL Data: " +str(time.clock()-t0)
        else:
            print "Using Cached globalTransactionDir"
        tsearch = time.clock()
        transactions = globalTransactionDir.findAllMatching(search_string,\
                                                            psc_pattern)
        print "Time To Search ALL Data for "+search_string + ": " +\
          str(time.clock()-tsearch)
    else:
        # this code is without caching
        print "Not using cache."
        localTransactionDir = Transaction.TransactionDirector()        
        t1 = time.clock()

        globalTransactionDir.transactions = \
          loadDirectory(pathToData,search_string,psc_pattern)
        numRows = len(globalTransactionDir.transactions)
        print "Time To Load Data for "+search_string + ": " +str(time.clock()-t1)
        transactions = localTransactionDir.transactions
        
    print "Total Number of Transactions in Dataset: "+str(len(transactions))
    
    transactions = [tr.dict for tr in transactions[0:LIMIT_NUM_RETURNED_TRANSACTIONS]]
    print "Second Total Number of Transactions in Dataset: "+str(len(transactions))
    transactionDict = dict(zip(range(0, len(transactions)),transactions))
    print "Time To Return from SearchApi: " +str(time.clock()-timeSearchBegin)
    return transactionDict
