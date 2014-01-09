# This file is for (for example) Apache with mod_wsgi.
import os
import PPBottleApp

# Note this is quite different from PricesPaid.py,
# which is the entry point for using bottle as your webserver.
application = PPBottleApp.app

def application(environ, start_response):
  os.environ['P3APISALT'] = environ['P3APISALT']
  return PPBottleApp.app(environ, start_response)


