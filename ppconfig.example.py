# These configuration are necessary if you are using Bottle as your webserver
BottlePortNumber = 8080
BottleHostname = 'localhost'
MasterUsername = 'username_changeme'
MasterPassword = 'password_changeme'
PathToDataFiles = "../cookedData"

# I configure these in apache and /etc/hosts, so these are not real urls...
# at present, I hit the service only via the local machine.
URLToPPSearchApi = "https://shdsapi.org/api"
URLToPPSearchApiSolr = "https://shdsapi.org/apisolr"
