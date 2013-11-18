import Transaction
import time
from decimal import *


import ppApiConfig

# Note: For now, these are explict imports.
# Evntually, we want to make this automatic, and essentially
# create a dynamic array of adapters and loaders based on
# what we find in some directory so that it is easily
# extendable.  But that would be over-engineering if we did it now.
from RevAucAdapter import getDictionaryFromRevAuc,loadRevAucFromCSVFile
from OS2Adapter import getDictionaryFromOS2,loadOS2FromCSVFile
from GSAAdvAdapter import getDictionaryFromGSAAdv,loadGSAAdvFromCSVFile
from LabEquipAdapter import getDictionaryFromLabEquipment,loadLabequipmentFromCSVFile

from os import listdir
from os.path import isfile, join
import re

import solr


import logging


from cStringIO import StringIO
import cPickle as pickle

logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
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
LIMIT_NUM_RETURNED_TRANSACTIONS = 1000
# This is simple.  More sophisticated systems will be possible.
# This is a significatn limit on the number of records returned,
# but seems like a reasonable safety valve.
ppApiConfig.LIMIT_NUM_MATCHING_TRANSACTIONS = 1000

# Note: Eventually, we need to do some sort of auto-loading to get this to work.
VERSION_ADAPTER_MAP = { '1': [loadRevAucFromCSVFile,getDictionaryFromRevAuc],
                        '2': [loadOS2FromCSVFile,getDictionaryFromOS2],
                        '3': [loadGSAAdvFromCSVFile,getDictionaryFromGSAAdv],
                        '4': [loadLabequipmentFromCSVFile,getDictionaryFromLabEquipment]}

# This routine needs to become the basis of the SolrLodr...

def applyToLoadedFiles(dirpath,pattern,funToApply,maximumToLoad = ppApiConfig.LIMIT_NUM_MATCHING_TRANSACTIONS,version_adapter_map = VERSION_ADAPTER_MAP):
    print "maximumToLoad "+  str(maximumToLoad)
    onlyfiles = [ f for f in listdir(dirpath) if isfile(join(dirpath,f)) ]
    onlycsvfiles = [ f for f in onlyfiles if re.search(".csv$",f)]
    for filename in onlycsvfiles:
        transactions = []
        print filename
        if len(transactions) > maximumToLoad:
            print "WEIRD!"
            break
        version = Transaction.parseFormatVersion(filename)
        if not version:
             logger.error('File in wrong format: '+dirpath+filename)
             print 'File in wrong format: '+dirpath+filename
        else:
            # RevAuc data has number 1
            # This would be better with a functional "cond" type operator
            adapter = None
            logger.info('version:'+version)
            print 'version:'+version
            if (version in version_adapter_map):
                v = version_adapter_map[version]
                loader = v[0]
                adapter = v[1]
                transactions.extend(loader(dirpath+"/"+filename,\
                     pattern, adapter,maximumToLoad))

                logger.info('Total Number Transactions Read From File'+filename \
                                +str(len(transactions)))
                funToApply(filename,transactions)
            else:
                logger.error('Unknown version')
                raise Exception('Unknown Format Version')

# Probably want to replace with the above lambda-lift
def loadDirectory(dirpath,pattern,version_adapter_map = VERSION_ADAPTER_MAP):
    onlyfiles = [ f for f in listdir(dirpath) if isfile(join(dirpath,f)) ]
    transactions = []
    onlycsvfiles = [ f for f in onlyfiles if re.search(".csv$",f)]
    for filename in onlycsvfiles:
        print filename
        if len(transactions) > ppApiConfig.LIMIT_NUM_MATCHING_TRANSACTIONS:
            break
        version = Transaction.parseFormatVersion(filename)
        if not version:
             logger.error('File in wrong format: '+dirpath+filename)
             print 'File in wrong format: '+dirpath+filename
        else:
            # RevAuc data has number 1
            # This would be better with a functional "cond" type operator
            adapter = None
            logger.info('version:'+version)
            if (version in version_adapter_map):
                v = version_adapter_map[version]
                loader = v[0]
                adapter = v[1]
                transactions.extend(loader(dirpath+"/"+filename,\
                     pattern, adapter,ppApiConfig.LIMIT_NUM_MATCHING_TRANSACTIONS))
            else:
                logger.error('Unknown version')
                raise Exception('Unknown Format Version')

    logger.info('Total Number Transactions Read From Directory' \
        +str(len(transactions)))
    return transactions

AGGREGATED_TEXT_FIELD = "text";

def searchApiSolr(URLToSolr,pathToData,search_string,psc_pattern,limit=ppApiConfig.LIMIT_NUM_MATCHING_TRANSACTIONS):
# create a connection to a solr server
    solrCon = solr.SolrConnection(URLToSolr)
    localTransactionDir = None
    
    timeSearchBegin = time.clock()

    transaction = None

    print "Not using cache."
    logger.info("Not using cache.")        
    localTransactionDir = Transaction.TransactionDirector()        
    t1 = time.clock()

    logger.info("Searching for search_string,psc" + search_string+","+psc_pattern)
    
    # do a search
    mainSearch = AGGREGATED_TEXT_FIELD+':'+search_string
    pscSearch = Transaction.PSC+':'+psc_pattern

    # the magic happens here...
    # you can add q_op='AND' here, but it seems to shut down all instances.  I'm afraid
    # I either need to use ediscmax or do something else.
    print "rows = "+ str(limit)
    if (psc_pattern == "*"):
        transactionDicts = solrCon.query(mainSearch,rows=limit,fl='*,score',deftype='edismax')
    else:
        transactionDicts = solrCon.query(mainSearch,rows=limit,fq=pscSearch,fl='*,score',deftype='edismax')
    return processSolrResults(transactionDicts)


def getP3ids(URLToSolr,pathToData,p3idsPickled,limit=ppApiConfig.LIMIT_NUM_MATCHING_TRANSACTIONS):
# create a connection to a solr server
    solrCon = solr.SolrConnection(URLToSolr)
    localTransactionDir = None
    
    transaction = None
    localTransactionDir = Transaction.TransactionDirector()        
    p3ids = pickle.loads(p3idsPickled)
    ids = ["id:"+x for x in p3ids]
    idSearch = ' OR '.join(ids)
    logger.info("idSearch"+repr(idSearch))    
    print "idSearch = " +repr(idSearch)
    transactionDicts = solrCon.query(idSearch,rows=limit,fl='*,score',deftype='edismax')
    return processSolrResults(transactionDicts)

def processSolrResults(transactionDicts):
    # This is a duplication that must be removed with the above.
    for hit in transactionDicts.results:
        # massage the score a little bit --- could normalize to
        # 100% to make a little nicer in the future...
        hit['score'] = int(Decimal(str(hit['score']*100)).quantize(Decimal('1'), rounding=ROUND_UP))
        hit['p3id'] = hit['id']
        # remove the version and the id which come back
        del hit['id']
        del hit['_version_']
        # remove the _t auto-tag so it will look nicer when rendered.
        for f in hit:
            if f[-2:] == '_t':
                hit[f[:-2]] = hit[f]
                del hit[f]

    transactionDicts = transactionDicts.results
    numRows = len(transactionDicts)
    transactionDicts = transactionDicts[0:LIMIT_NUM_RETURNED_TRANSACTIONS]
    
    numberedTransactionDict = dict(zip(range(0, len(transactionDicts)),transactionDicts))
    return numberedTransactionDict
