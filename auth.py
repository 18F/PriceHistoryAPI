# This file is responsible for checking secure hashes
# against configured user/password sistuations.
import os
import random,string
import datetime
import LogActivity

import pickle
import hashlib
from ppApiConfig import RelativePathToHashesFile,TokenTimeout

hashes = {}

GLOBAL_BAD_LOGIN = {}

# Load from disk
def loadHashes():
    hshs_file = RelativePathToHashesFile
    if os.path.exists(hshs_file):
        hashes = pickle.load(open(hshs_file, "rb"))
    else:
        hashes = {}
    return hashes

def record_bad_login(username):
    if username not in GLOBAL_BAD_LOGIN:
        GLOBAL_BAD_LOGIN[username] = [0,datetime.datetime.now()]
    else:
        GLOBAL_BAD_LOGIN[username][0] = GLOBAL_BAD_LOGIN[username][0]+1
        GLOBAL_BAD_LOGIN[username][1] = datetime.datetime.now()

def does_authenticate(username,password,p3apisalt):
    hashes = loadHashes()
    if username in GLOBAL_BAD_LOGIN:
        timenow = datetime.datetime.now()
        timestamp = GLOBAL_BAD_LOGIN[username][1]
        timedelta = timenow - timestamp
        if (timedelta >=  datetime.timedelta(seconds=ppApiConfig.LIMIT_TIME_TO_RETRY)):
            # An hour has gone by, so we givem them a pass....
            GLOBAL_BAD_LOGIN.pop(username, None)

    if username in GLOBAL_BAD_LOGIN:
        count = GLOBAL_BAD_LOGIN[username][0]
        if (count >= ppApiConfig.LIMIT_NUMBER_BAD_LOGINS):
            # Probably should have a separate log message for this..
            LogActivity.logTooManyLoginAttempts(username)
            return False;
            
    if username not in hashes:
        LogActivity.logBadCredentials(username)
        record_bad_login(username)
        return False;
    if hashes[username] == hashlib.sha256(password+p3apisalt).hexdigest():
        return True;
    else:
        LogActivity.logBadCredentials(username)
        record_bad_login(username)
        return False;

GLOBAL_SESSION_DICT = {}

def create_session_id():
    session_id = get_rand_string(13);
    acsrf = get_rand_string(13);
    timestamp = datetime.datetime.now();
    GLOBAL_SESSION_DICT[session_id] = [acsrf,timestamp]
    return session_id;

def update_acsrf(session_id):
    acsrf = get_rand_string(13);
    timestamp = datetime.datetime.now();
    GLOBAL_SESSION_DICT[session_id] = [acsrf,timestamp]
    return session_id;
    
    
CHARS = string.ascii_letters + string.digits
def get_rand_string(length):
    return ''.join(random.choice(CHARS) for i in range(length))

def is_valid_acsrf(session_id):
    if (session_id in GLOBAL_SESSION_DICT):
        timestamp = GLOBAL_SESSION_DICT[session_id][1]
        timenow = datetime.datetime.now()
        timedelta = timenow - timestamp
        if (timedelta < datetime.timedelta(seconds=TokenTimeout)):
            return True
        else:
            LogActivity.logTimeout(session_id)
            return False
    else:
        LogActivity.logMissingSession(session_id)
        return False;
        

def get_acsrf(session_id):
    timestamp = GLOBAL_SESSION_DICT[session_id][1]
    return GLOBAL_SESSION_DICT[session_id][0]
    
