import logging

logger = logging.getLogger('ActivityLogger')
hdlr = logging.FileHandler('../logs/Activity.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

# would I'm not loggin the password attempt as it might be 
# close to a real password, allowing someone to guess it 
def logBadCredentials(username):
    logger.info("Bad AuthenticationAttempt : "+username)

def logTooManyLoginAttempts(username):
    logger.info("TooManyLoginAttempts : "+username)

def logMissingSession(session_id):
    logger.info("Session id missing : "+session_id)

def logTimeout(session_id):
    logger.info("Session id timed out : "+session_id)

def logFeedback(session_id):
    logger.info("Feedback submitted : "+session_id)

def logSessionBegin(username,session_id):
    logger.info("SessionBegins : "+username+" : "+session_id)

def logPageTurn(session_id,page):
    logger.info("PageTurn : "+session_id+" : "+page)

def logSearchBegun(session_id,psc_pattern,search_string):
    logger.info("SearchBegun : "+session_id+" : "+str(psc_pattern)+" : "+str(search_string))

def logSearchDone(session_id,psc_pattern,search_string):
    logger.info("SearchDone  : "+session_id+" : "+str(psc_pattern)+" : "+str(search_string))

def logDebugInfo(info):
    logger.info("Debug Info : "+info)
