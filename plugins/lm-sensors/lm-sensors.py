#!/usr/bin/python

import sys,os,re


regexp = {
    "fan"  : '^([^:]*):\s*([0-9]*) RPM.*min =\s*([-+]*[0-9]*) RPM, div =\s*([0-9]*).*$',
    "volt" : '^([^:]*):\s*([-+]*[0-9.]*) V.*min =\s*([-+]*[0-9.]*) V, max =\s*([-+]*[0-9.]*).*$',
    "temp" : '^([^:]*):\s*([-+]*[0-9.]*).*high =\s*([-+]*[0-9.]*).* hyst =\s*([-+]*[0-9.]*).*$'
}

values = {
    "fan.value"  : 2,
    "fan.min"    : 3,
    "fan.div"    : 4,
    "volt.value" : 2,
    "volt.min"   : 3,
    "volt.max"   : 4,
    "temp.value" : 2,
    "temp.high"  : 3,
    "temp.hyst"  : 4
}

def discovery(param):

    print "{";
    print "\t\"data\":[";

    if param[0] in regexp:

        regex = regexp[param[0]]
        list = sensors_regex(regex)

        for i in range(0,len(list)):
            m = list[i]
            item = '\t\t{\n'
            item += '\t\t\t"{#SENSORNAME}":"'+m.group(1)+'"\n'
            item += '\t\t}'
            if i < len(list)-1:
                item += ','
            print item

    print '\t]'
    print '}'


def value(param):

    if param[0] not in regexp:
        print "0"
        return

    if param[0]+'.'+param[1] not in values:
        print "0"
        return

    regex = regexp[param[0]]
    list = sensors_regex(regex)

    for item in list:
        if item.group(1) == param[2]:
            print item.group(values[param[0]+'.'+param[1]])
            return

    print "0"


def sensors_regex(regex):

    proc = os.popen("sensors")
    input = proc.readlines()

    res = []
    
    for i in range(0,len(input)):
        line = input[i].rstrip('\n')
        m = re.search(regex, line)
        if m != None:
            res.append(m)

    return res


#
# Function list definition
#
functions = {
    "discovery" : {
        "function" : discovery,
        "argv"     : 1
    },
    "value" : {
        "function" : value,
        "argv"     : 3
    },
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
