#!/usr/bin/python

import sys,os,json,httplib

host = "localhost"
port = "8080"
apikey = "5c7831f258b42b38ed64ddd89f956c15"


#
# SabNZBd API get
#
# Get the API informations
#
def getJSON():
    try:
        conn = httplib.HTTPConnection(host, port)
        conn.request("GET", "/sabnzbd/api?mode=queue&output=json&apikey="+apikey)
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


#
# Function list definition
#
functions = {
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
