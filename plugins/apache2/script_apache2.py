#!/usr/bin/python

import sys,os,json,httplib,re

host = "localhost"
port = "80"
uri = "/server-status"

slots = {
    "total"     : "",
    "waiting"   : "_",
    "starting"  : "S",
    "reading"   : "R",
    "sending"   : "W",
    "keepalive" : "K",
    "dns"       : "D",
    "closing"   : "C",
    "logging"   : "L",
    "finishing" : "G",
    "idel"      : "I",
    "open"      : ".",
}



#
# Apache Informations
#
# Get the server informations
#
def getInfos():
    try:
        conn = httplib.HTTPConnection(host, port)
        conn.request("GET", uri)
        r1 = conn.getresponse()
    except Exception:
        return False

    return r1.read()


#
# Version
#
# Print the Application Version
#
def version(param):
    os.system('apache2ctl -v 2>/dev/null | grep version')


#
# Ping
#
# Print the current status:
# - 1 : Server started
# - 0 : Server stopped
#
def ping(param):
    content = getInfos()
    if content == False:
        print "0"
    else :
        print "1"


def slot(param):

    if param[0] not in slots:
        print "0"
        return

    content = getInfos()

    content = content[(content.find('<pre>')+5):content.find('</pre>')].strip('\n')

    print content.count(slots[param[0]])


def vhost_discovery(param):

    proc = os.popen('apache2ctl -S 2>/dev/null | grep port | sed -e "s/^[ ]*//g"')
    input = proc.readlines()

    print "{";
    print "\t\"data\":[";

    for i in range(0,len(input)):
        line = input[i].rstrip('\n').split(' ')
        item = '\t\t{\n'
        item += '\t\t\t"{#VHPORT}":"'+line[1]+'"\n'
        item += '\t\t\t"{#VHNAME}":"'+line[3]+'"\n'
        item += '\t\t}'
        if i < len(input)-1:
            item += ','
        print item

    print '\t]'
    print '}'


def vhost_slot(param):

    if param[1] not in slots:
        print "0"
        return

    content = getInfos()

    content = content[(content.find('<table border="0">')+18):content.find('</table>')].strip('\n')

    start = 0
    end = 0
    count = 0

    while 1:
        start = content.find('<tr>', end)
        end = content.find('</tr>', start)
        if start < 0 or end < 0:
            break
        line = content[start+4:end].replace('\n', '')
        line = re.sub('<[^>]*>', ';', line)
        line = re.sub(';+', ';', line)

        items = line.split(';');
        if items[4] == slots[param[1]] and items[12] == param[0]:
            count += 1

    print count


    


#
# Function list definition
#
functions = {
    "ping" : {
        "function" : ping,
        "argv"     : 0
    },
    "version" : {
        "function" : version,
        "argv"     : 0
    },
    "slot" : {
        "function" : slot,
        "argv"     : 1
    },
    "vhost.discovery" : {
        "function" : vhost_discovery,
        "argv"     : 0
    },
    "vhost.slot" : {
        "function" : vhost_slot,
        "argv"     : 1
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
