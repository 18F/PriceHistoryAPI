# These configuration are necessary if you are using Bottle as your webserver

# Note: Many of these are the same as ppGUIConfig.py.  This should be unified into a global 
# config and pushed into P3Auth or some other place where they can be shared to stay DRY.

BottlePortNumber = 8080
BottleHostname = 'localhost'
PathToDataFiles = "../cookedData"
URLToPPSearchApi = "http://localhost/api"
URLToPPSearchApiSolr = "http://localhost/apisolr"
URLToSolr = 'http://localhost:8983/solr'

RelativePathToHashesFile = "../configuration/p3api.hashes.txt"

# I'm going to use a 20-minute timeout
TokenTimeout = 600*2


LIMIT_NUMBER_BAD_LOGINS = 5

# We'll make them wait one hour if they have 5 bad logins.
LIMIT_TIME_TO_RETRY = 60*60

# Note: This may have to change when loading SOLRLodr
MAXIMUM_NUMBER_TO_LOAD = 1000*5000

LIMT_NUM_MATCHING_TRANSACTIONS = 1000

CAS_SERVER = 'http://127.0.0.1:8099'
CAS_RETURN_SERVICE_URL = 'http://127.0.0.1/apisolr/ReturnLoginViaMax'
CAS_CREATE_SESSION_IF_AUTHENTICATED = 'http://127.0.0.1/apisolr/ReturnSessionViaMax'
# This should be in the form of a python "requests" proxies dictionary
# CAS_SERVER_PROXY =  {
#  "http": "http://10.10.1.10:3128",
#   "https": "http://10.10.1.10:1080",
# }

CAS_PROXY =  {
}

CAS_LEVEL_OF_ASSURANCE = "assurancelevel3"
CAS_LEVEL_OF_ASSURANCE_PREDICATE_LOA3 = lambda loa,piv: {
    ("http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel3" == loa)
}
CAS_LEVEL_OF_ASSURANCE_PREDICATE_LOA2 = lambda loa,piv: {
    ("http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel2" == loa)
    or 
    ("http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel3" == loa)

}

CAS_LEVEL_OF_ASSURANCE_PREDICATE_LOA2_AND_PIV = lambda loa,piv: {
    (("http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel2" == loa)
    or
    ("http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel3" == loa))
    and
    ("urn:max:fips-201-pivcard" == piv)

}
CAS_PIV_CARD = lambda loa,piv: {
   ("urn:max:fips-201-pivcard" == piv)
}
CAS_PASSWORD_OR_PIV = lambda loa, piv: {
   ("urn:max:fips-201-pivcard" == piv)
   or
   ("urn:oasis:names:tc:SAML:1.0:am:password" == piv)
}
CAS_LEVEL_3 = lambda loa, piv: {
   ("urn:max:am:secureplus:federated-saml2:assurancelevel3" == piv)
}
CAS_LEVEL_OF_ASSURANCE_PREDICATE = CAS_PASSWORD_OR_PIV

