#!/usr/bin/python

import sys
import os
import re
import ConfigParser
import getpass
import StringIO
import subprocess
import shutil

# Configuration file
script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
conf_file  = script_dir+"/zabbix-plugins.conf"

# configuration variable
config = ConfigParser.RawConfigParser()


# Constant Variables
zp_plugins_dir   = script_dir+"/plugins"

# Install variables
function = None
plugins  = []


#
# Usage function
#
def usage():
    print "Zabbix plugin installer"
    print ""
    print "./zabbix-plugins.py action [options] plugin1 plugin2 ..."
    print ""
    print "Options :"
    print "\t--help           : show this help"
    print "\t--no-server      : Do not install Zabbix Server part"
    print "\t--no-agent       : Do not install Zabbix Agent part"
    print "\t--agent-dir      : Set the Zabbix agent directory"
    print "\t--server-dir     : Set the Zabbix server directory"
    print ""


#
# Script print functions
#
def actionPrint(str):
    print (str.ljust(50)),
    
def actionOK():
    print "[ \033[32mOK\033[0m ]"

def actionKO(error):
    print "[ \033[31mKO\033[0m ] : "+error

#
# Install configuration loading method
#
# Load the congifuration file and check sections and options
#
def loadConfig():

    global config

    sections = {
        "ZabbixServer" : ["Install", "Directory", "DBHost", "DBPort", "DBName", "DBUser", "DBPass"],
        "ZabbixAgent"  : ["Install", "Directory", "Scripts", "configure", "Userparameters"]
    }

    try:
        config.read(conf_file)
    except:
        print "Configuration file ("+conf_file+") not found"
        sys.exit(-1)

    for section in sections:
        if not config.has_section(section):
            print "Error in configuration file : "+conf_file
            print "Missing section: "+section
            sys.exit(1)
        for option in sections[section]:
            if not config.has_option(section, option):
                print "Error in configuration file : "+conf_file
                print "Missing option: ["+section+"] "+option
                sys.exit(1)
            

#
# List plugins function
#
def listPlugins():
    print "List of available plugins :"
    for filename in sorted(os.listdir(zp_plugins_dir)):
        print "- "+filename


def getPluginFiles(path):

    files = {
        "path"          : path,
        "userparameter" : [],
        "script"        : [],
        "template"      : []
    }
    
    for filename in sorted(os.listdir(path)):
        part = filename.split("_")
        if part[0] in files:
            files[part[0]].append(filename)
    
    return files


#
# Install Plugin function
#
def installPlugins():

    # Check if Zabbix server directory is writeable
    if config.get("ZabbixServer", "Install"):
        if not os.access(config.get("ZabbixServer", "Directory"), os.W_OK):
            print "Zabbix Server directory does not exists or is not writeable: "+config.get("ZabbixServer", "Directory")
            print "Please check your Zabbix installation or modify zabbix_plugins.conf"
            sys.exit(1)

    if config.get("ZabbixAgent", "Install"):
        if not os.access(config.get("ZabbixAgent", "Directory"), os.W_OK):
            print "Zabbix Agent directory does not exists or is not writeable : "+config.get("ZabbixAgent", "Directory")
            print "Please check your Zabbix installation or modify zabbix_plugins.conf"
            sys.exit(1)

    # List plugins to install
    for plugin in plugins:

        if plugin != plugins[0]:
            print ""

        print "Installing plugin "+plugin

        # Load Script directory
        actionPrint("Loading Plugin directory")
        zp_plugin_dir = zp_plugins_dir+"/"+plugin
        try:
            zp_plugin_files = getPluginFiles(zp_plugin_dir)
        except:
            actionKO("Unknow plugin")
            continue
        actionOK()
        
        # Agent Script installation
        installScript(zp_plugin_files)
        
        # Agent userparameters installation
        installUserParameter(zp_plugin_files)

        # Server help items installation
        installHelpItems(zp_plugin_files)


def configurePlugins():
    print "configurePlugins"


#
# Script install function
#
def installScript(files):

    if not config.get("ZabbixAgent", "Install"):
        return

    if len(files["script"]) == 0:
        return

    actionPrint(" - [Agent] Installing Scripts")

    script_install_dir = config.get("ZabbixAgent", "Scripts")
    
    # Check and create script installation directory
    try:
        if not os.path.exists(script_install_dir):
            os.makedirs(script_install_dir)
    except:
        print "Inexistent script directory and cannot create: "+script_install_dir
        return


    # Copy script file
    for script_file in files["script"]:
        try:
            shutil.copyfile(files["path"]+"/"+script_file, script_install_dir+"/"+script_file)
        except:
            actionKO("Unable to install script "+files["path"]+"/"+script_file+" in "+script_install_dir+"/"+script_file)
            return

    actionOK()
    

#
# UserParameter install functions
#
def installUserParameter(files):

    if not config.get("ZabbixAgent", "Install"):
        return

    if len(files["userparameter"]) == 0:
        return

    actionPrint(" - [Agent] Installing Userparameters")

    param_install_dir = config.get("ZabbixAgent", "Userparameters")

    # Check and create script installation directory
    try:
        if not os.path.exists(param_install_dir):
            os.makedirs(param_install_dir)
    except:
        actionKO("Inexistent userparameters directory and cannot create: "+param_install_dir)
        return

    # Open param file
    for filename in files["userparameter"]:
        src = files["path"]+"/"+filename
        dest = config.get("ZabbixAgent", "Userparameters")+"/"+filename
    
        # Read user parameter file
        try:
            with open (src, "r") as myfile:
                data=myfile.read()
        except:
            actionKO("Unable to read file: "+src)
            return

        # Write new userparameter file
        try:
            with open (dest, "w") as myfile:
                myfile.write(data.replace("[SCRIPT_DIRECTORY]", config.get("ZabbixAgent", "Scripts")))
        except:
            actionKO("Unable to install file: "+dest)
            return
            
    actionOK()
    

#
# Help items install function
#
def installHelpItems(files):

    if not config.get("ZabbixServer", "Install"):
        return

    if len(files["userparameter"]) == 0:
        return

    actionPrint(" - [Server] Installing Help Items")
    
    # MySQL command line
    mysql = "mysql"
    mysql += " -h"+config.get("ZabbixServer", "DBHost")
    mysql += " -P"+config.get("ZabbixServer", "DBPort")
    mysql += " -u"+config.get("ZabbixServer", "DBUser")
    mysql += " -p"+config.get("ZabbixServer", "DBPass")
    mysql += " "+config.get("ZabbixServer", "DBName")
    
    # Build MySQL insert request
    request=""

    # List userparameters files
    for filename in files["userparameter"]:
        src = files["path"]+"/"+filename

        # Read user parameter file
        try:
            with open (src, "r") as myfile:
                data=myfile.readlines()
        except:
            actionKO("Unable to read file: "+src)
            return

        # Create MySQL parameter request
        for line in data:
            m = re.search(r'^# \[HelpItem\] ([^=]*)=(.*)$', line)
            if m == None:
                continue

            request += "INSERT INTO help_items (itemtype, key_, description)\n"
            request += "    Values (0, '"+m.group(1).strip(" ")+"', '"+m.group(2).strip(" ")+"')\n"
            request += "ON DUPLICATE KEY UPDATE\n"
            request += "    itemtype = VALUES(itemtype),\n"
            request += "    description = VALUES(description);\n"

    # Insert Help items in database
    os.popen("echo \""+request+"\" | "+mysql)
    p = os.popen("echo $?")
    if p.read().rstrip('\n') != "0":
        actionKO("Failed populate database")
        return

    actionOK()


# Script actions list
actions = {
    "list"      : listPlugins,
    "install"   : installPlugins,
    "configure" : configurePlugins
}


#
# Main part
#
if __name__ == "__main__":

    loadConfig()

    for item in sys.argv:
        if item == sys.argv[0]:
            continue
        
        arg = item.split('=')
        
        if arg[0] in ["-h", "--help"]:
            usage()
            sys.exit(0)
        elif arg[0] == "--server-dir":
            config.set("ZabbixServer", "Directory", arg[1].rstrip("/"))
        elif arg[0] == "--agent-dir":
            config.set("ZabbixAgent", "Directory", arg[1].rstrip("/"))
        elif arg[0] == "--no-server":
            config.set("ZabbixServer", "Install", False)
        elif arg[0] == "--no-agent":
            config.set("ZabbixAgent", "Install", False)
        else:
            if function == None:
                if arg[0] in actions:
                    function = actions[arg[0]]
                else:
                    print "Undefined action "+arg[0]
                    usage()
                    sys.exit(1)
            else:
                plugins.append(arg[0])
        
    if function == None:
        usage()
        sys.exit(1)

    function()

    sys.exit(0)
