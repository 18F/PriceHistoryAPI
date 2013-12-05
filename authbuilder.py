# This file is responsible for checking secure hashes
# against configured user/password sistuations.
import random, string


import os
import pickle
import hashlib
P3APISALT = "defaultSalt"
RelativePathToPasswordFile = '../configuration/p3api.passwords.txt'
RelativePathToHashesFile = '../configuration/p3api.hashes.txt'

def generatePasswords():
    hsh_file = RelativePathToHashesFile
    pwd_file = RelativePathToPasswordFile
    pwds = {}
    hshs = {}
    for i in range(100):
        username = "user"+str(i)
        # Warning!  This is temporary!  We really want to
        # create random authenticationsecrets instead, but we need to
        # know the authenticationsecrets to mail them out to people,
        # So this is just a test.
        authenticationsecret = "pass"+str(i)

        length = 13
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'

        authenticationsecret = ''.join(random.choice(chars) for i in range(length))

        pwds[username] = authenticationsecret
        hshs[username] = hashlib.sha256(authenticationsecret+P3APISALT).hexdigest()

    # Save to disk
    pickle.dump(hshs, open(hsh_file, "wb"))
    pickle.dump(pwds, open(pwd_file, "wb"))

# invoke the function.
generatePasswords()
