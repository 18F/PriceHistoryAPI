# This file is responsible for checking secure hashes
# against configured user/password sistuations.
import os
import pickle
import hashlib
from ppApiConfig import RelativePathToHashesFile,P3APISALT

# Load from disk
def loadPasswords():
    hsh_file = RelativePathToHashesFile
    if os.path.exists(hsh_file):
        pwds = pickle.load(open(hsh_file, "rb"))
    else:
        pwds = {}
    return pwds

def does_authenticate(username,password):
    hshs = loadPasswords()
    print len(hshs)
    print username
    # Check password
    # Likely need to catch an exception here
    if hshs[username] == hashlib.sha256(password+P3APISALT).hexdigest():
        print "Good"
        return True;
    else:
        print "No match"
        # here we should log the failure.
        return False;

