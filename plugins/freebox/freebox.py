#!/usr/bin/python

import sys
import os
import json
import httplib
import urllib
import ConfigParser
import time

# Configuration file
conf_file = "freebox.ini"

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
        uri += api.get("API", "fb_api_url") if api.has_option("API", "fb_api_url") else ""
        uri += api.get("API", "fb_api_version") if api.has_option("API", "fb_api_version") else ""
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


#
# Configure method
#
def configure(param):

    # Create ConfigParser
    global api

    # Call api version
    json = httpJson(fb_url_api_version, {})
    if not json:
        return

    # Configuration filling
    if not api.has_section("API"):
        api.add_section("API")
    api.set("API", "fb_type"       , json["device_type"])
    api.set("API", "fb_name"       , json["device_name"])
    api.set("API", "fb_uid"        , json["uid"])
    api.set("API", "fb_api_url"    , json["api_base_url"])
    api.set("API", "fb_api_version", "v"+str(int(float(json["api_version"]))))

    # Construct authorize parameters
    data = {
        "app_id"      : app_id,
        "app_name"    : app_name,
        "app_version" : app_version,
        "device_name" : device_name}

    print "Please accept authorize on Freebox"

    # Call authorize function
    json = httpJson(fb_url_login_authorize, data)
    if not json:
        return
    
    # Waiting token state
    state = "pending"
    while state == "pending":
        time.sleep(3);
        token = httpJson(fb_url_login_authorize+"/"+str(json["track_id"]), {})
        state = token["status"]

    # Configuration filling
    if state == "granted":
        if not api.has_section("Authorize"):
            api.add_section("Authorize")
        api.set("Authorize", "token", json["app_token"])

    # Writing configuration
    with open(conf_file, 'wb') as configfile:
        api.write(configfile)


#
# API login function
#
def login():

    global fb_token

    # Call API to log in
    login = httpJson(fb_url_login, {})
    if not login:
        return False
    
    # Construction for API session
    data = {
        "app_id": app_id,
        "password": hmac_sha1(api.get("Authorize", "token"), login["challenge"])}

    # Call API for a session
    session = httpJson(fb_url_login_session, data)
    if not session:
        return False

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

