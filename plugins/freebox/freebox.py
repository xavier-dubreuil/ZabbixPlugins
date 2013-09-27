#!/usr/bin/python

import sys
import os
import json
import httplib
import urllib
import ConfigParser
import time

# Configuration file
script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
conf_file  = script_dir+"/freebox.ini"

# Freebox host
fb_host        = "mafreebox.freebox.fr"

# Freebox url
fb_url_api_version     = "/api_version"
fb_url_login           = "/login"
fb_url_login_authorize = fb_url_login+"/authorize"
fb_url_login_session   = fb_url_login+"/session"
fb_url_connection      = "/connection"
fb_url_connection_xdsl = fb_url_connection+"/xdsl"
fb_url_connection_ftth = fb_url_connection+"/ftth"
fb_url_rrd             = "/rrd/"

# Freebox variables
fb_type        = None
fb_name        = None
fb_uid         = None
fb_api_url     = None
fb_api_version = None

# Session
fb_token = None

# Script constants
app_id      ="ZabbixPlugins"
app_name    ="Zabbix Plugins"
app_version ="1.0"
device_name ="zabbix_agent"

# Freebox variables
api = ConfigParser.RawConfigParser()
if os.access(conf_file, os.R_OK):
    api.read(conf_file)

#
# Script print functions
#
def actionPrint(str):
    sys.stdout.write(str.ljust(50))
    sys.stdout.flush()
    
def actionOK():
    print "[ \033[32mOK\033[37m ]"

def actionKO(error):
    print "[ \033[31mKO\033[37m ] : "+error


#
# API call method
#
def httpJson(url, data):
    try:

        # Method detection
        method = "GET" if len(data) == 0 else "POST"
    
        # Header token
        header = {"X-Fbx-App-Auth": fb_token} if fb_token != None else {}

        # URI construction
        uri = "" 
        uri += fb_api_url if fb_api_url != None else ""
        uri += fb_api_version if fb_api_version != None else ""
        uri += url

        # HTTP call
        conn = httplib.HTTPConnection(fb_host, 80)
        conn.request(method, uri, json.dumps(data), header)
        res = conn.getresponse()
        
    except Exception:
        return False

    # Check HTTP Status
    if res.status != 200:
        return False

    # Get JSON response
    content = json.loads(res.read())

    # Version result
    if url == fb_url_api_version:
        return content

    # Check success
    if not content["success"]:
        return False

    # return result content
    return content["result"]


#
# HMAC SHA1 crypt method
#
def hmac_sha1(key, msg):
    from hashlib import sha1
    import hmac
    
    # Crypt message with key
    return hmac.new(key, msg, sha1).hexdigest()


def getAPIVersion():

    global fb_type,fb_name,fb_uid,fb_api_url,fb_api_version

    # Call api version
    json = httpJson(fb_url_api_version, {})
    if not json:
        return False

    fb_type        = json["device_type"]
    fb_name        = json["device_name"]
    fb_uid         = json["uid"]
    fb_api_url     = json["api_base_url"]
    fb_api_version = "v"+str(int(float(json["api_version"])))

    return True


#
# Configure method
#
def configure(param):

    # Create ConfigParser
    global api

    # Construct authorize parameters
    data = {
        "app_id"      : app_id,
        "app_name"    : app_name,
        "app_version" : app_version,
        "device_name" : device_name}

    # Check configuration file write availability
    actionPrint("Opening configuration file")
    try:
        handle_file = open(conf_file, 'wb')
    except:
        actionKO('Unable to open for writing conf file: '+conf_file)
        sys.exit(1)
    actionOK()

    # Get API informations
    actionPrint("Getting Freebox API informations")
    if not getAPIVersion():
        actionKO("Unable to get API informations")
        sys.exit(1)
    actionOK()

    actionPrint("Validate authorization on your Freebox")

    # Call authorize function
    json = httpJson(fb_url_login_authorize, data)
    if not json:
        actionKO("Unable to get authorization from API")
        sys.exit(1)

    # Waiting token state
    state = "pending"
    while state == "pending":
        time.sleep(3);
        token = httpJson(fb_url_login_authorize+"/"+str(json["track_id"]), {})
        if not token:
            actionKO("Unable to get authorization from API")
            sys.exit(1)
        state = token["status"]

    # Configuration filling
    if state != "granted":
        actionKO("Authorization refused")
        sys.exit(1)
    
    # Add token to configuration
    if not api.has_section("Authorize"):
        api.add_section("Authorize")
    api.set("Authorize", "token", json["app_token"])

    actionOK()        

    # Check configuration file write availability
    actionPrint("Writing configuration file")
    try:
        api.write(handle_file)
    except:
        actionKO('Unable to write the configuration file: '+conf_file)
        sys.exit(1)
    actionOK()


#
# API login function
#
def login():

    global fb_token

    if not getAPIVersion():
        print "0"
        sys.exit(1)

    # Call API to log in
    login = httpJson(fb_url_login, {})
    if not login:
        print "0"
        sys.exit(1)
    
    # Construction for API session
    data = {
        "app_id": app_id,
        "password": hmac_sha1(api.get("Authorize", "token"), login["challenge"])}

    # Call API for a session
    session = httpJson(fb_url_login_session, data)
    if not session:
        print "0"
        sys.exit(1)

    # Set Session to variable
    fb_token = session["session_token"]


#
# Get Connection informations
#
def connection(param):

    login()
    
    # Call API for connection informations
    json = httpJson(fb_url_connection, {})
    
    # Print value if exists
    if json and param[0] in json:
        print json[param[0]]
    else:
        print "0"
        sys.exit(1)


#
# Get Connection XDSL informations
#
def connectionXDSL(param):

    login()
    
    # Call API for XDSL connection informations
    json = httpJson(fb_url_connection_xdsl, {})
    
    # Print value if exists
    if json and param[0] in json and param[1] in json[param[0]]:
        print json[param[0]][param[1]]
    else:
        print "0"
        sys.exit(1)


#
# Get Connection FTTH informations
#
def connectionFTTH(param):

    login()
    
    # Call API for FTTH connection informations
    json = httpJson(fb_url_connection_ftth, {})
    
    # Print value if exists
    if json and param[0] in json and param[1] in json[param[0]]:
        print json[param[0]][param[1]]
    else:
        print "0"
        sys.exit(1)


#
# Get RRD informations
#
def rrd(param):

    login()
    
    timestamp = int(time.time())
    
    data = {
        "db"         : param[0],
        "fields"     : [ param[1] ],
        "date_start" : timestamp,
        "date_end"   : timestamp+10
    }
    
    # Call API for RRD informations
    json = httpJson(fb_url_rrd, data)

    # Print value if exists
    if json and "data" in json and len(json["data"]) > 0 and param[1] in json["data"][0]:
        print json["data"][0][param[1]]
    else:
        print "0"
        sys.exit(1)


#
# Function list definition
#
functions = {
    "configure"   : {
        "function" : configure,
        "argv"     : 0
    },
    "connection"   : {
        "function" : connection,
        "argv"     : 1
    },
    "connection.xdsl"   : {
        "function" : connectionXDSL,
        "argv"     : 2
    },
    "connection.ftth"   : {
        "function" : connectionFTTH,
        "argv"     : 2
    },
    "rrd"   : {
        "function" : rrd,
        "argv"     : 2
    }
}


#
# Main part
#
if __name__ == "__main__":

    # Get the function name on first argument
    func  = sys.argv[1] if len(sys.argv) > 1 else "Usage"

    # Get the parameter on second argument
    param = sys.argv[2:] if len(sys.argv) > 2 else ""

    # Check if function exists in functions array
    if func in functions and len(sys.argv) - 2 == functions[func]["argv"]:

        # Call the function with the parameter
        functions[func]["function"](param)

    sys.exit(0)