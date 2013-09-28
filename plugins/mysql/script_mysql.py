#!/usr/bin/python

import sys
import os
import ConfigParser
import ZabbixPlugins

#
# Configuration reference
#
configReference = [
    { "name" : "Connection", "options" : [
        { "name" : "dbhost", "desc" : "Database Host"    , "default" : "localhost", "secret" : False },
        { "name" : "dbport", "desc" : "Database Port"    , "default" : "3306"     , "secret" : False },
        { "name" : "dbname", "desc" : "Database Name"    , "default" : "zabbix"   , "secret" : False },
        { "name" : "dbuser", "desc" : "Database Username", "default" : "zabbix"   , "secret" : False },
        { "name" : "dbpass", "desc" : "Database Password", "default" : ""         , "secret" : True }]
    }
]

# Configuration file
configFilename = "script_mysql.conf"


#
# Command line options
#
def mysqlCmd(admin):

    list = {
        "dbhost" : { "opt" : "-h", "admin" : [ True, False ] },
        "dbport" : { "opt" : "-P", "admin" : [ True, False ] },
        "dbname" : { "opt" : ""  , "admin" : [ False ] },
        "dbuser" : { "opt" : "-u", "admin" : [ True, False ] },
        "dbpass" : { "opt" : "-p", "admin" : [ True, False ] }
    }

    if admin:
        cmd = "mysqladmin"
    else :
        cmd = "mysql -N"

    for item in list:
        value = zp.get('Connection', item)
        if value == False:
            return False
        if admin in list[item]["admin"]:
            cmd += " "+list[item]["opt"]+str(value)
    cmd += " 2>/dev/null"

    return cmd


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
    mysql = mysqlCmd(True)
    if not mysql:
        print 0
        return False

    lines = zp.execute(mysqlCmd(True)+' ping | grep -c alive')
    if not lines:
        print 0
        return False

    print lines[0].rstrip('\n')

#
# Database Discovery
#
# Function to list databases on MySQL server
# Return the list in format for Zabbix discovery
#
def db_discovery(param):
    mysql = mysqlCmd(False)
    if not mysql:
        print 0
        return False

    lines = zp.execute("echo 'show databases;' | "+mysql)
    if not lines:
        print 0
        return False

    print "{";
    print "\t\"data\":[";

    for i in range(0,len(lines)):
        line = lines[i].rstrip('\n')
        item = '\t\t{\n\t\t\t"{#DBNAME}":"'+line.rstrip('\n')+'"}'
        if i < len(lines)-1:
            item += ','
        else:
            item += ']}'
        print item

    return True


#
# Database size
#
# Print the size in Octet of a database
#
def db_size(param):
    mysql = mysqlCmd(False)
    if not mysql:
        print 0
        return False

    request = "select sum(data_length + index_length) from information_schema.TABLES where TABLE_SCHEMA = '"+param[0]+"';"

    lines = zp.execute("echo \""+request+"\" | "+mysql)
    if not lines:
        print 0
        return False

    if len(lines) == 0:
        print 0
        return False

    print lines[0].rstrip('\n');


#
# Configure method
#
def configure(param):

    zp.configure()

#
# Function list definition
#
keysReference = {
    "configure"    : { "function" : configure   , "argv" : 0},
    "version"      : { "function" : version     , "argv" : 0},
    "status"       : { "function" : ping        , "argv" : 0},
    "db.discovery" : { "function" : db_discovery, "argv" : 0},
    "db.size"      : { "function" : db_size     , "argv" : 1}
}

#
# Main part
#
if __name__ == "__main__":

    zp = ZabbixPlugins.ZabbixPlugins(keysReference, configReference, configFilename)

    zp.start()

    sys.exit(0)
