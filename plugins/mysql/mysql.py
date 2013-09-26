#!/usr/bin/python

import sys,os

DBHost="localhost"
DBPort="3306"
DBName="zabbix"
DBUser="zabbix"
DBPass=""

#
# Command line options
#
# The arguments are taken from the Zabbix server configuration file:
# /etc/zabbix/zabbix_server.conf
#
def mysql_opts():
    proc = os.popen('cat /etc/zabbix/zabbix_server.conf | egrep "^DB*"')
    input = proc.readlines()

    opts = []
    options = {
        "DBHost":"-h",
        "DBPort":"-P",
        "DBUser":"-u",
        "DBPassword":"-p"
    }
    for line in input:
        fields = line.rstrip('\n').split('=')
        if fields[0] in options:
            opts.insert(len(opts),options[fields[0]]+fields[1])

    return ' '.join(opts)


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
    request = "select sum(data_length + index_length) from information_schema.TABLES where TABLE_SCHEMA = '"+param+"';"
    os.system('echo "'+request+'" | mysql -N '+mysql_opts())


#
# Function list definition
#
functions = {
    "version"      : version,
    "ping"         : ping,
    "db.discovery" : db_discovery,
    "db.size"      : db_size
}


#
# Main part
#
if __name__ == "__main__":

    # Get the function name on first argument
    func  = sys.argv[1] if len(sys.argv) > 1 else "Usage"

    # Get the parameter on second argument
    param = sys.argv[2] if len(sys.argv) > 2 else ""

    # Check if function exists in functions array
    if func in functions:

        # Call the function with the parameter
        functions[func](param)
