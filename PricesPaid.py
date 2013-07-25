# This file is for using Bottle as your webserver.
from bottle import Bottle, run, template,request

import sys
sys.path.insert(0, '../configuration/')
from ppconfig import BottlePortNumber,BottleHostname

import PPBottleApp

# This line is different from app.wsgi---this
# is if you want to run the Bottle webserver itself
# rather than Apache.  I am trying to maintain both,
# in particular because I don't know of a good way to
# implement SSH without Apache
run(PPBottleApp.app, host=BottleHostname, port=BottlePortNumber, debug=True,reloader=True)


