# This should actually be renamed so that it is not confused
# with the file of the same name in PricesPaidGUI
from bottle import Bottle, run, template,request,TEMPLATE_PATH,static_file
from bottle import response

import json

from SearchApi import searchApiSolr,getP3ids

from ppApiConfig import PathToDataFiles,URLToSolr,LIMIT_NUM_MATCHING_TRANSACTIONS

app = Bottle()

import auth

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
                         psc_pattern,numRows = LIMIT_NUM_MATCHING_TRANSACTIONS):
    if (not auth.does_authenticate(user,password)):
        dict = {0: {"status": "BadAuthentication"}}
        return dict;
    search_string = convertSearchStringToLegalPattern(search_string);
    psc_pattern = convertPSCToLegalPattern(psc_pattern);

    if (numRows is None):
        numRows = LIMIT_NUM_MATCHING_TRANSACTIONS;
    return searchApiSolr(URLToSolr,PathToDataFiles,search_string,psc_pattern,numRows)


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
    numRows = request.query.get('numRows')
    search_string = request.query.get('search_string')
    psc_pattern = request.query.get('psc_pattern')
    if (request.query.callback):
        response.content_type = "application/javascript"
        return jsonp(request,
                     processSearchRequest(user,password,
                                          search_string,psc_pattern,numRows))
    return processSearchRequest(user,password,
                                search_string,psc_pattern,numRows)

@app.route('/',method='POST')
def apisolr():
    user = request.forms.get('username')
    password = request.forms.get('password')
    search_string = request.forms.get('search_string')
    psc_pattern = request.forms.get('psc_pattern')
    max_results = request.forms.get('numRows')
    return processSearchRequest(user,password,search_string,psc_pattern,max_results)


def processFromIds(user,password,p3ids,numRows = LIMIT_NUM_MATCHING_TRANSACTIONS):
    if (not auth.does_authenticate(user,password)):
        dict = {0: {"status": "BadAuthentication"}}
        return dict;
    return getP3ids(URLToSolr,PathToDataFiles,p3ids,numRows)

@app.route('/fromIds',method='POST')
def fromIds():
    user = request.forms.get('username')
    password = request.forms.get('password')
    p3ids = request.forms.get('p3ids')
    return processFromIds(user,password,p3ids)




