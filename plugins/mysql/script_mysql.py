#!/usr/bin/python

import sys
import os
import ConfigParser
import getpass

# Configuration file
script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
conf_file  = script_dir+"/script_mysql.conf"

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
# Command line options
#
def mysql_opts():

    opts = " -h"+config.get('Connection', 'dbhost')
    opts += " -P"+config.get('Connection', 'dbport')
    opts += " -u"+config.get('Connection', 'dbuser')
    opts += " -p"+config.get('Connection', 'dbpass')

    return opts


#
# Database Version
#
# Print the MySQL Version
#
def version(param):
    os.system('mysql -V')


#
# Database Ping
#
# Print the current status:
# - 1 : Server started
# - 0 : Server stopped
#
def ping(param):
    os.system('mysqladmin '+mysql_opts()+' ping | grep -c alive')


#
# Database Discovery
#
# Function to list databases on MySQL server
# Return the list in format for Zabbix discovery
#
def db_discovery(param):
    proc = os.popen('echo "show databases;" | mysql -N '+mysql_opts())
    input = proc.readlines()

    print "{";
    print "\t\"data\":[";

    for i in range(0,len(input)):
        line = input[i].rstrip('\n')
        item = '\t\t{\n\t\t\t"{#DBNAME}":"'+line.rstrip('\n')+'"}'
        if i < len(input)-1:
            item += ','
        else:
            item += ']}'
        print item


#
# Database size
#
# Print the size in Octet of a database
#
def db_size(param):
    request = "select sum(data_length + index_length) from information_schema.TABLES where TABLE_SCHEMA = '"+param[0]+"';"
    os.system('echo "'+request+'" | mysql -N '+mysql_opts())


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
    config.set("Connection", "dbhost", getKeyboard("Database Host", "localhost", False))
    config.set("Connection", "dbport", getKeyboard("Database Port", "3306", False))
    config.set("Connection", "dbname", getKeyboard("Database Name", "zabbix", False))
    config.set("Connection", "dbuser", getKeyboard("Database Username", "zabbix", False))
    config.set("Connection", "dbpass", getKeyboard("Database Password", "", True))
    
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
    "version"   : {
        "function" : version,
        "argv"     : 0
    },
    "status"   : {
        "function" : ping,
        "argv"     : 0
    },
    "db.discovery"   : {
        "function" : db_discovery,
        "argv"     : 0
    },
    "db.size"   : {
        "function" : db_size,
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

    sys.exit(0)
