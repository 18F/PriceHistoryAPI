# This file is for (for example) Apache with mod_wsgi.
import sys, os

import sys
sys.path.insert(0, '../configuration/')
# There is currently nothing in configuration that we are using

# These are requires if you are using mod_wsgi.
# I know, I know, this should not be needed, but I haven't found a way
# around it yet.
WsgiAbsolutePath = '/home/robert/PricesPaid/application'

sys.path = [WsgiAbsolutePath] + sys.path
os.chdir( WsgiAbsolutePath )

from bottle import TEMPLATE_PATH
TEMPLATE_PATH.insert(0,WsgiAbsolutePath)

import PPBottleApp

# Note this is quite different from PricesPaid.py,
# which is the entry point for using bottle as your webserver.
application = PPBottleApp.app