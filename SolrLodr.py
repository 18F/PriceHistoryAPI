#!/usr/local/bin/python

import solr
import sys, traceback


# This file is for (for example) Apache with mod_wsgi.
import sys, os

# import sys
# sys.path.insert(0, '../configuration/')

# The purpose of this file is to take the standard
# datafiles and load them into SOLR in such a way that they
# will be searchable.
# This is meant to be run from a command line because
# I assume it is to be invoked when you change the
# source data directory, which implies you are changing
# files and it will be easy to run it from a command line.
# Later, we can wrap this into something that allows
# a file to be uploaded through the API.
# We may someday need to manage the SOLR index with
# an administrative interface, but for now the goal is
# just to make it reflect the directory.  I'm assuming
# those are the simplest way to do these things.
import Transaction
import time

from ppApiConfig import PathToDataFiles, MAXIMUM_NUMBER_TO_LOAD

# Note: For now, these are explict imports.
# Evntually, we want to make this automatic, and essentially
# create a dynamic array of adapters and loaders based on
# what we find in some directory so that it is easily
# extendable.  But that would be over-engineering if we did it now.
from RevAucAdapter import getDictionaryFromRevAuc,loadRevAucFromCSVFile
from OS2Adapter import getDictionaryFromOS2,loadOS2FromCSVFile
from GSAAdvAdapter import getDictionaryFromGSAAdv,loadGSAAdvFromCSVFile
from LabEquipAdapter import getDictionaryFromLabEquipment,loadLabequipmentFromCSVFile
from USASpendingAdapter import getDictionaryFromUSASpending,loadUSASpendingFromCSVFile


from os import listdir
from os.path import isfile, join
import re

import logging

import SearchApi

logger = logging.getLogger('PPSolrLodr')
hdlr = logging.FileHandler('../logs/PPSolrLodr.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

LIMIT_NUM_MATCHING_TRANSACTIONS = 5000*1000*100;

# create a connection to a solr server
# This needs to come from ppconfig
solrCon = solr.SolrConnection('http://localhost:8983/solr')

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
        
idcnt = 0;

def loadChunk(filename,chunk):
    global idcnt
    l = []
    for t in chunk:
        d = {}
        # we need to look at the dictionary and map
        # non standard fields to those matching our "dynamic field" name
        # in the schema.
        for key, value in t.dict.items():
            v = unicode(value, errors='ignore')
            # This unicode stuff needs to be changed at the source..
            # We should not carry around bad data and then cover it up like this!
            if (key in Transaction.STANDARD_FIELDS):
              d[unicode(key,errors='ignore')] = v;
            else:
              # I think _txt might be clearer!
              d[key+"_t"] = v;

        # possibly the addtion of this id field should actually be done
        # when we create the objects!  That would make the class useful!
        d['id'] = filename+"_"+str(idcnt);
        idcnt = idcnt+1;

        l.append(d);
    try:
        print "about to add "+str(len(l))
        solrCon.add_many(l)
        solrCon.commit()
        print "success"
    except:
        print "failure"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)      
        logger.error("don't know what went wrong here")

    
def loadSolr(filename,transactions):
    global idcnt
    chunkedTransactions = list(chunks(transactions, 1000))
    for chunk in chunkedTransactions:
        loadChunk(filename,chunk)

# Before we load, we need to delete!
# This seems a little dangerous, but there is not much we can do.

# We really want to make this a command-line argument so 
# that we can load one data file at a time.
response = solrCon.delete_query('*:*')
solrCon.commit()

SearchApi.applyToLoadedFiles(PathToDataFiles,None,loadSolr,MAXIMUM_NUMBER_TO_LOAD)
