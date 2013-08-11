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

import solr

import logging
logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('/var/tmp/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)


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

# Note: Eventually, we need to do some sort of auto-loading to get this to work.
VERSION_ADAPTER_MAP = { '1': [loadFedBidFromCSVFile,getDictionaryFromFedBid],
                        '2': [loadOS2FromCSVFile,getDictionaryFromOS2] }

# This routine needs to become the basis of the SolrLodr...
def loadDirectory(dirpath,pattern,version_adapter_map = VERSION_ADAPTER_MAP):
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
            logger.info('version:'+version)
            if (version in version_adapter_map):
                v = version_adapter_map[version]
                loader = v[0]
                adapter = v[1]
                transactions.extend(loader(dirpath+"/"+filename,\
                     pattern, adapter,LIMIT_NUM_MATCHING_TRANSACTIONS))
            else:
                logger.error('Unknown version')
                raise Exception('Unknown Format Version')

    logger.info('Total Number Transactions Read From Directory' \
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
            timeToLoadAll = "Time To Load ALL Data: " +str(time.clock()-t0)
            print timeToLoadAll
            logger.info(timeToLoadAll)
            logger.info("Num Rows in globalTransaction "+str(numRows))        
        else:
            print "Using Cached globalTransactionDir"
        tsearch = time.clock()
        logger.info("Searching for search_string,psc" + search_string+","+psc_pattern)
        transactions = globalTransactionDir.findAllMatching(search_string,\
                                                            psc_pattern)
        timeToSearch = "Time To Search ALL Data for "+search_string + ": " +\
          str(time.clock()-tsearch)
        print timeToSearch
        logger.info(timeToSearch)        
    else:
        # this code is without caching
        print "Not using cache."
        logger.info("Not using cache.")        
        localTransactionDir = Transaction.TransactionDirector()        
        t1 = time.clock()

        logger.info("Searching for search_string,psc" + search_string+","+psc)        
        globalTransactionDir.transactions = \
          loadDirectory(pathToData,search_string,psc_pattern)
        numRows = len(globalTransactionDir.transactions)
        timeToLoad = "Time To Load Data for "+search_string + ": " +str(time.clock()-t1)
        logger.info(timeToLoad)
        print timeToLoad
        transactions = localTransactionDir.transactions
        
    totalNumber = "Total Number of Transactions in Dataset: "+str(len(transactions))
    print totalNumber
    logger.info(totalNumber)
        
    transactions = [tr.dict for tr in transactions[0:LIMIT_NUM_RETURNED_TRANSACTIONS]]
    secondTotal = "Second Total Number of Transactions in Dataset: "+str(len(transactions))
    print secondTotal
    logger.info(secondTotal)    
    transactionDict = dict(zip(range(0, len(transactions)),transactions))
    timeToReturn =  "Time To Return from SearchApi: " +str(time.clock()-timeSearchBegin)
    print timeToReturn
    logger.info(timeToReturn)    
    return transactionDict



def searchApiSolr(pathToData,search_string,psc_pattern):
# create a connection to a solr server
# This needs to come from ppconfig
    solrCon = solr.SolrConnection('http://localhost:8983/solr')
    localTransactionDir = None
    
    timeSearchBegin = time.clock()

    transaction = None

    print "Not using cache."
    logger.info("Not using cache.")        
    localTransactionDir = Transaction.TransactionDirector()        
    t1 = time.clock()

    logger.info("Searching for search_string,psc" + search_string+","+psc_pattern)
    
    # do a search
    mainSearch = Transaction.LONGDESCR+':'+search_string
    pscSearch = Transaction.PSC+':'+psc_pattern

    # the magic happens here...
    transactionDicts = solrCon.query(mainSearch + ' '+ pscSearch,rows=100)

    
    for hit in transactionDicts.results:
        print hit[Transaction.LONGDESCR]
    print repr(transactionDicts.results)

    transactionDicts = transactionDicts.results
    numRows = len(transactionDicts)
    timeToLoad = "Time To Load Data for "+search_string + ": " +str(time.clock()-t1)
    logger.info(timeToLoad)
    print timeToLoad


    
    totalNumber = "Total Number of Transactions in Dataset: "+str(len(transactionDicts))
    print totalNumber
    logger.info(totalNumber)
        
    transactionDicts = transactionDicts[0:LIMIT_NUM_RETURNED_TRANSACTIONS]
    
    secondTotal = "Second Total Number of Transactions in Dataset: "+str(len(transactionDicts))
    print secondTotal
    logger.info(secondTotal)    
    numberedTransactionDict = dict(zip(range(0, len(transactionDicts)),transactionDicts))
    timeToReturn =  "Time To Return from SearchApi: " +str(time.clock()-timeSearchBegin)
    print timeToReturn
    logger.info(timeToReturn)    
    return numberedTransactionDict
