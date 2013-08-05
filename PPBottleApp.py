from bottle import Bottle, run, template,request,TEMPLATE_PATH,static_file

from SearchApi import searchApi

from ppconfig import MasterPassword,MasterUsername,PathToDataFiles

app = Bottle()

def does_authenticate(user,password):
    return (user == MasterUsername and password == MasterPassword)

@app.route('/api',method='POST')
def pptriv():
    user = request.forms.get('user')
    password = request.forms.get('password')
    if (not does_authenticate(user,password)):
        return template('BadAuthentication')        
    search_string = request.forms.get('search_string')
    psc_pattern = request.forms.get('psc_pattern')
    print "API search_string" + search_string
    return searchApi(PathToDataFiles,search_string,psc_pattern)


