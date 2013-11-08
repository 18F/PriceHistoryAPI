# These configuration are necessary if you are using Bottle as your webserver
BottlePortNumber = 8080
BottleHostname = 'localhost'
PathToDataFiles = "../cookedData"
URLToPPSearchApi = "https://shdsapi.org/api"
URLToPPSearchApiSolr = "https://shdsapi.org/apisolr"
URLToSolr = 'http://localhost:8983/solr'
WsgiAbsolutePath = '/home/robert/PricesPaid/PricesPaidAPI'

RelativePathToHashesFile = "../configuration/p3api.hashes.txt"
P3APISALT = "defaultSalt"
# I'm going to use a 10-minute timeout
TokenTimeout = 600


LIMIT_NUMBER_BAD_LOGINS = 5

# We'll make them wait one hour if they have 5 bad logins.
LIMIT_TIME_TO_RETRY = 60*60

MAXIMUM_NUMBER_TO_LOAD = 1000*5000

LIMT_NUM_MATCHING_TRANSACTIONS = 1000
