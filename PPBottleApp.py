# This should actually be renamed so that it is not confused
# with the file of the same name in PricesPaidGUI
from bottle import Bottle, run, template,request,TEMPLATE_PATH,static_file
from bottle import response

import urllib
import urlparse
import json
import os
import PriceHistoryAuth.LogActivity
import sys

from StandardCSVReader import loadFromCSVString,getDictionaryFromStandard

from SearchApi import searchApiSolr,getP3ids

from SolrLodr import loadSolr

from ppApiConfig import PathToDataFiles,URLToSolr,LIMIT_NUM_MATCHING_TRANSACTIONS,\
    CAS_SERVER,CAS_PROXY,CAS_RETURN_SERVICE_URL,CAS_LEVEL_OF_ASSURANCE,CAS_CREATE_SESSION_IF_AUTHENTICATED,CAS_LEVEL_OF_ASSURANCE_PREDICATE

app = Bottle()

import PriceHistoryAuth.auth
import PriceHistoryAuth.pycas

import logging
logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

P3APISALT = None

def convertPSCToLegalPattern(str):
    if (str is None) or (str == 'None') or (str == ''):
        return '*';
    else:
        return str;

# this needs to be improved, but basically,
# we don't want them to do a blank search.
# it could be prevented at the GUI layer as well.
def convertSearchStringToLegalPattern(str):
    if (str is None) or (str == 'None') or (str == ''):
        return 'nothing at all, choose something';
    else:
        return str;

def processSearchRequest(user,password,search_string,
                         psc_pattern,clientData,numRows = LIMIT_NUM_MATCHING_TRANSACTIONS):
    global P3APISALT
    if (P3APISALT is None):
        P3APISALT=os.environ.get("P3APISALT")
    if (not PriceHistoryAuth.auth.does_authenticate(user,password,P3APISALT)):
        dict = {0: {"status": "BadAuthentication"}}
        logger.error('Bad Authentication Request '+ repr(user))
        return dict;
    search_string = convertSearchStringToLegalPattern(search_string);
    psc_pattern = convertPSCToLegalPattern(psc_pattern);

    if (numRows is None):
        numRows = LIMIT_NUM_MATCHING_TRANSACTIONS;
    result = searchApiSolr(URLToSolr,PathToDataFiles,search_string,psc_pattern,numRows)
    if clientData:
        result["clientdata"] = clientData
    return result

def processSearchRequestSession(session,acsrf,search_string,
                         psc_pattern,clientData,numRows = LIMIT_NUM_MATCHING_TRANSACTIONS):
    global P3APISALT

    PriceHistoryAuth.LogActivity.logDebugInfo("processSearchRequestSession fired:"+repr(session))

    if (P3APISALT is None):
        P3APISALT=os.environ.get("P3APISALT")
# Here we need to use session and acsrf
    if (not PriceHistoryAuth.auth.is_valid_acsrf(session,acsrf)):
        PriceHistoryAuth.LogActivity.logDebugInfo("not valid:"+repr(session)+repr(acsrf))
        dict = {0: {"status": "BadAuthentication"}}
        logger.error('Bad Authentication Request '+ repr(session))
        return dict;
    search_string = convertSearchStringToLegalPattern(search_string);
    psc_pattern = convertPSCToLegalPattern(psc_pattern);

    if (numRows is None):
        numRows = LIMIT_NUM_MATCHING_TRANSACTIONS;
    result = searchApiSolr(URLToSolr,PathToDataFiles,search_string,psc_pattern,numRows)
    if clientData:
        result["clientdata"] = clientData
    return result;


@app.route('/hello',method='GET')
def trivtest():
    return "true"

# The problem is this is using Pythonism (the unicode string)
# when it shouldn't.  I need to look into Bottle and 
# understand do whatever it does to convert unicode strings
# to javascript strings...
def jsonp(request, dictionary):
    if (request.query.callback):
        return "%s(%s)" % (request.query.callback, json.dumps(dictionary))
    return dictionary

@app.route('/',method='GET')
def apisolr():
    user = request.query.get('p3username')
    password = request.query.get('p3password')
    clientData = request.query.get('clientdata')
    numRows = request.query.get('numRows')
    search_string = request.query.get('search_string')
    psc_pattern = request.query.get('psc_pattern')
    if (request.query.callback):
        response.content_type = "application/javascript"
        return jsonp(request,
                     processSearchRequest(user,password,
                                          search_string,psc_pattern,clientData,numRows))
    return processSearchRequest(user,password,
                                search_string,psc_pattern,clientData,numRows)

@app.route('/session',method='GET')
def apisolr():
    session = request.query.get('p3session_id')
    acsrf = request.query.get('p3acsrf')
    numRows = request.query.get('numRows')
    clientData = request.query.get('clientdata')
    search_string = request.query.get('search_string')
    psc_pattern = request.query.get('psc_pattern')
    if (request.query.callback):
        response.content_type = "application/javascript"
        return jsonp(request,
                     processSearchRequestSession(session,acsrf,
                                          search_string,psc_pattern,clientData,numRows))
    return processSearchRequestSession(session,acsrf,
                                search_string,psc_pattern,clientData,numRows)

@app.route('/',method='POST')
def apisolr():
    user = request.forms.get('username')
    password = request.forms.get('password')
    clientData = request.forms.get('clientdata')
    search_string = request.forms.get('search_string')
    psc_pattern = request.forms.get('psc_pattern')
    max_results = request.forms.get('numRows')
    logger.error('Normal post called '+ repr(user))
    return processSearchRequest(user,password,search_string,psc_pattern,clientData,max_results)

def processFromIds(user,password,p3ids,numRows = LIMIT_NUM_MATCHING_TRANSACTIONS):
    global P3APISALT
    if (P3APISALT is None):
        P3APISALT=os.environ.get("P3APISALT")
    if (not PriceHistoryAuth.auth.does_authenticate(user,password,P3APISALT)):
        dict = {0: {"status": "BadAuthentication"}}
        logger.error('Bad Authentication Request '+ repr(user))
        return dict;
    return getP3ids(URLToSolr,PathToDataFiles,p3ids,numRows)

@app.route('/fromIds',method='POST')
def fromIds():
    user = request.forms.get('username')
    password = request.forms.get('password')
    p3ids = request.forms.get('p3ids')
    logger.error('fromIds post called '+ repr(user))
    return processFromIds(user,password,p3ids)



@app.route('/AddCSVFile',method='POST')
def addCSVFile():
    user = request.forms.get('username')
    password = request.forms.get('password')
    global P3APISALT
    if (P3APISALT is None):
        P3APISALT=os.environ.get("P3APISALT")
    if (not PriceHistoryAuth.auth.does_authenticate(user,password,P3APISALT)):
        dict = {0: {"status": "BadAuthentication"}}
        logger.error('Bad Authentication Request '+ repr(user))
        return dict;
    csv_file = request.forms.get('csv_file')
    filename = "SAMPLEUPLOAD"
    trans = loadFromCSVString(csv_file,getDictionaryFromStandard,filename)
    
    try:
        loadSolr(filename,trans)
    except:
        return "Probably failed: "+repr(sys.exc_info()[0])
    return "Might have added "+repr(len(trans))+" rows."





# This is a count to keep things straight
requestNumber = 0

# map
mapRequestToReturnURL = {}


@app.route('/ReturnSessionViaMax/<requestId:int>')
def returnSessionViaMax(requestId):
    global mapRequestToReturnURL
    PriceHistoryAuth.LogActivity.logDebugInfo("return ID:"+repr(requestId))

    PriceHistoryAuth.LogActivity.logPageTurn("nosession","ReturnMaxLoginPage")

    ticket = request.query['ticket']
    PriceHistoryAuth.LogActivity.logDebugInfo("MAX AUTHENTICATED ticket :"+ticket)

    amendedReturnURL = CAS_CREATE_SESSION_IF_AUTHENTICATED+"/"+repr(requestId)

    status, id, cookie = PriceHistoryAuth.pycas.check_authenticated_p(CAS_LEVEL_OF_ASSURANCE_PREDICATE,ticket,CAS_SERVER, 
                                                     amendedReturnURL, lifetime=None, secure=1, protocol=2, path="/", opt="")
    maxAuthenticatedProperly = (status == PriceHistoryAuth.pycas.CAS_OK);

    PriceHistoryAuth.LogActivity.logDebugInfo("MAX AUTHENTICATED WITH ID:"+id)

    PriceHistoryAuth.LogActivity.logDebugInfo("ReturnSessionViaMax authenticated :"+repr(maxAuthenticatedProperly))
    if (maxAuthenticatedProperly):
        sendTokensBackTo = mapRequestToReturnURL[requestId]
        response.status = 303 
        domain,path = urlparse.urlparse(CAS_RETURN_SERVICE_URL)[1:3]
        secure=1
        setCookieCommand = PriceHistoryAuth.pycas.make_pycas_cookie("gateway",domain,path,secure)
        strip = setCookieCommand[12:]
# We will set this cookie to make it easier for the user
# to avoid multiple logins---but technically, this is not 
# what is being used and the user, who is probably using the API,
# will want to ignore this.
        response.set_header('Set-Cookie', strip)
        ses_id = PriceHistoryAuth.auth.create_session_id()
        acsrf = PriceHistoryAuth.auth.get_acsrf(ses_id)
        response.add_header('Location',sendTokensBackTo+"?p3session_id="+ses_id+"&p3acsrf="+acsrf)
        return "You will be redirected."+strip+sendTokensBackTo
    else:
        PriceHistoryAuth.LogActivity.logBadCredentials("Failed to Authenticate with Max")
        return template('Login',message='Improper Credentials.',
                    footer_html=FOOTER_HTML,
                    extra_login_methods=EXTRA_LOGIN_METHODS,
                        goog_anal_script=GoogleAnalyticsInclusionScript)

@app.route('/GetTokensViaMax')
def getTokensViaMax():
    PriceHistoryAuth.LogActivity.logPageTurn("nosession","GetTokensViaMax")
    global requestNumber
    global mapRequestToReturnURL

    sendTokensBackTo = request.query['redirectbackto']
    response.status = 303 
    domain,path = urlparse.urlparse(CAS_RETURN_SERVICE_URL)[1:3]
    secure=1
    setCookieCommand = PriceHistoryAuth.pycas.make_pycas_cookie("gateway",domain,path,secure)
    strip = setCookieCommand[12:]
    response.set_header('Set-Cookie', strip)
    opt=""
    # There is a danger that we might have multiple requested
    # get crossed here because we are treating this "statelessly".
    # Since we need to make sure that we go back to the proper 
    # redirect, we add the request number to the URL
    amendedReturnURL = CAS_CREATE_SESSION_IF_AUTHENTICATED+"/"+repr(requestNumber)
    mapRequestToReturnURL[requestNumber] = sendTokensBackTo
    requestNumber = requestNumber + 1
    location = PriceHistoryAuth.pycas.get_url_redirect_as_string(CAS_SERVER,amendedReturnURL,opt,secure)
    response.set_header('Location',location)
    return "You will be redirected."+strip+location

