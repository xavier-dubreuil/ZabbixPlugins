#!/usr/bin/python

import sys
import os
import json
import httplib
import ConfigParser
import getpass

# Configuration file
script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
conf_file  = script_dir+"/script_sabnzbd.conf"

# Configuration variables
config = ConfigParser.RawConfigParser()
if os.access(conf_file, os.R_OK):
    config.read(conf_file)

#
# Script print functions
#
def actionPrint(str):
    sys.stdout.write(str.ljust(50))
    sys.stdout.flush()
    
def actionOK():
    print "[ \033[32mOK\033[0m ]"

def actionKO(error):
    print "[ \033[31mKO\033[0m ] : "+error


#
# SabNZBd API get
#
# Get the API informations
#
def getJSON():
    try:
        conn = httplib.HTTPConnection(config.get('Connection', 'host'), config.get('Connection', 'port'))
        conn.request("GET", "/sabnzbd/api?mode=queue&output=json&apikey="+config.get('Connection', 'apikey'))
        r1 = conn.getresponse()
    except Exception:
        return { "error" : "SabNZBD is not reachable" }

    if r1.status != 200:
        return { "error" : "SabNZBD is not reachable" }

    return json.loads(r1.read())


#
# Database Version
#
# Print the MySQL Version
#
def version(param):
    os.system('sabnzbdplus -v | grep sabnzbdplus')


#
# Database Ping
#
# Print the current status:
# - 1 : Server started
# - 0 : Server stopped
#
def ping(param):
    json = getJSON()
    if "queue" in json or "status" in json:
        print "1"
    else :
        print "0"


#
# Disk Space function
#
# Print the disk space values: Used, Free or Total
# 2 param needed:
# - Disk  : download | complete
# - Value : used | free | total
#
def disk(param):

    disk = {
        "download" : "1",
        "complete" : "2"
    }
    vals = {"used", "free", "total"}

    if param[0] not in disk or param[1] not in vals:
        return

    json = getJSON()

    if "queue" not in json:
        print 0
        return

    free = float(json["queue"]["diskspace"+disk[param[0]]])
    total = float(json["queue"]["diskspacetotal"+disk[param[0]]])

    if param[1] == "used":
        print total - free

    elif param[1] == "free":
        print free

    elif param[1] == "total":
        print total


#
# Download informations
#
# Print download informations:
# - Rate  : current download rate
# - limit : current download limit rate
#
def download(param):

    vals = {
        "rate" : "kbpersec",
        "limit" : "speedlimit"
    }

    json = getJSON()

    if "queue" not in json:
        print 0
        return

    value = json["queue"][vals[param[0]]]

    if value == "":
        value = "0.00"

    print value


#
# Queue size
#
# Print the queue size
#
def queue(param):

    json = getJSON()

    if "queue" not in json:
        print 0
        return

    print json["queue"]["noofslots"]


def getKeyboard(text, default, secret):

    title = text.ljust(25)
    if default == "":
        title += "".rjust(15)+" : "
    else:
        title += str("[ "+default+" ]").rjust(15)+" : "
        
    value = ""
    if secret:
        while value == "":
            value = getpass.getpass(title)
    else:
        value = raw_input(title)
        if value == "":
            value = default
    
    return value
        

#
# Configure method
#
def configure(param):


    # Check configuration file write availability
    actionPrint("Opening configuration file")
    try:
        handle_file = open(conf_file, 'wb')
    except:
        actionKO('Unable to open for writing configuration file: '+conf_file)
        sys.exit(1)
    actionOK()

    # Add token to configuration
    if not config.has_section("Connection"):
        config.add_section("Connection")
    
    # MySQL informations   
    config.set("Connection", "host"  , getKeyboard("Hostname", "localhost", False))
    config.set("Connection", "port"  , getKeyboard("Port"    , "80"       , False))
    config.set("Connection", "apikey", getKeyboard("API Key" , ""         , False))
    
    # Check configuration file write availability
    actionPrint("Writing configuration file")
    try:
        config.write(handle_file)
    except:
        actionKO('Unable to write the configuration file: '+conf_file)
        sys.exit(1)
    actionOK()


#
# Function list definition
#
functions = {
    "configure"   : {
        "function" : configure,
        "argv"     : 0
    },
    "ping"   : {
        "function" : ping,
        "argv"     : 0
    },
    "version"  : {
        "function" : version,
        "argv"     : 0
    },
    "disk"     : {
        "function" : disk,
        "argv"     : 2
    },
    "download" : {
        "function" : download,
        "argv"     : 1
    },
    "queue"    : {
        "function" : queue,
        "argv"     : 0
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
