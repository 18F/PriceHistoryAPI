# This file is for (for example) Apache with mod_wsgi.

import PPBottleApp

# Note this is quite different from PricesPaid.py,
# which is the entry point for using bottle as your webserver.
application = PPBottleApp.app