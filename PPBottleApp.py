from bottle import Bottle, run, template,request,TEMPLATE_PATH,static_file

from SearchApi import searchApi

# Hopefully this will work!
PathToBottleWebApp = "./"
PathToDataFilesOnRobsMachine = "../cookedData"

PathToJSFiles=PathToBottleWebApp+"js/"
PathToCSSFiles=PathToBottleWebApp+"css/"
PathToJSPlugins=PathToJSFiles + "plugins/"
PathToSlickGridMaster=PathToBottleWebApp+"/SlickGrid-master/"

app = Bottle()

# Bottle seems to be fairly restrictive with static files,
# there might be a better way to do this.
@app.route('/js/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToJSFiles)

@app.route('/css/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToCSSFiles)

@app.route('/js/plugins/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToJSFiles + "plugins/")

@app.route('/SlickGrid-master/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToSlickGridMaster)

@app.route('/SlickGrid-master/css/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToSlickGridMaster+"css/")

@app.route('/SlickGrid-master/images/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToSlickGridMaster+"images/")

@app.route('/SlickGrid-master/css/smoothness/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToSlickGridMaster+"css/smoothness/")

@app.route('/SlickGrid-master/css/smoothness/images/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToSlickGridMaster+"css/smoothness/images")

@app.route('/SlickGrid-master/lib/<filename>')
def server_static(filename):
    return static_file(filename, root=PathToSlickGridMaster+"lib/")

def does_authenticate(user,password):
    return (user == "contractofficer" and password == "savegovmoney")


from bottle import template

@app.route('/')
def login():
    return template('Login')

@app.route('/PricesPaid',method='POST')
def pptriv():
    user = request.forms.get('user')
    password = request.forms.get('password')
    if (not does_authenticate(user,password)):
        return template('BadAuthentication')
    search_string = request.forms.get('search_string')
    search_string = search_string if search_string is not None else "Dell Latitude"
    return template('MainPage',search_string=search_string,user=user,password=password)

@app.route('/api',method='POST')
def pptriv():
    user = request.forms.get('user')
    password = request.forms.get('password')
    if (not does_authenticate(user,password)):
        return template('BadAuthentication')        
    search_string = request.forms.get('search_string')
    print "API search_string" + search_string
    return searchApi(PathToDataFilesOnRobsMachine,search_string)


