#!/usr/bin/python

import sys
import os
import re
import ConfigParser
import getpass
import StringIO
import subprocess
import shutil

# Constant Variables

zp_plugins_dir   = "plugins"
zp_plugins_conf  = "plugins.conf"

zb_install_dir   = "/etc/zabbix"
zb_userparam_dir = "zabbix_agentd.conf.d"
zb_scripts_dir   = "zabbix_agentd_scripts"
zb_server_conf   = "zabbix_server.conf"
zb_agent_conf    = "zabbix_agent.conf"


# Install variables

function    = None
plugins     = []
agent       = True
server      = True


#
# Usage function
#
def usage():
    print "Zabbix plugin installer"
    print ""
    print "./zabbix-plugins.py -h|--help"
    print "./zabbix-plugins.py list"
    print "./zabbix-plugins.py [-dir=Zabbix_dir] [--no-server|--no-agent] install plugin1 plugin2 ..."
    print ""
    print "Install :"
    print "\t--dir=Zabbix_dir : Set the Zabbix install directory"
    print "\t--no-server      : Do not install Zabbix Server part"
    print "\t--no-agent       : Do not install Zabbix Agent part"
    print ""


#
# Script print functions
#
def actionPrint(str):
    print (str.ljust(50)),
    
def actionOK():
    print "[ \033[32mOK\033[37m ]"

def actionKO(error):
    print "[ \033[31mKO\033[37m ] : "+error


#
# List plugins function
#
def listPlugins():
    print "List of available plugins :"
    for filename in sorted(os.listdir(pluginsDir)):
        if os.path.isfile(pluginsDir+"/"+filename+"/"+installFile):
            print "- "+filename


#
# Install Plugin function
#
def installPlugins():

    actionPrint("Check Zabbix installation dir")
    
    # Check if Zabbix install directory exists
    if not os.access(zb_install_dir, os.F_OK):
        actionKO("Zabbix directory does not exist: "+zb_install_dir)
        return
    
    actionOK()
    print ""

    # List plugins to install
    for plugin in plugins:

        actionPrint("Loading plugin "+plugin)

        zp_plugin_dir = zp_plugins_dir+"/"+plugin
        zp_plugin_conf = zp_plugin_dir+"/"+zp_plugins_conf

        # Check plugin directory
        if not os.path.isdir(zp_plugin_dir):
            actionKO("Plugin does not exist")
            continue
        
        # Check plugin installation configuration file
        if not os.path.isfile(zp_plugin_conf):
            actionKO("Plugin install configuration file missing")
            continue

        # Load Install configuration file
        cfg = ConfigParser.ConfigParser()
        cfg.optionxform = str
        cfg.read(zp_plugin_conf)

        # Check Install configuration file parameters
        if not cfg.has_section("Plugin"):
            actionKO("Bad Configuration file")
            continue

        actionOK()
        
        # Script install
        if cfg.has_option("Plugin","script.file") and agent == True:
            installScript(plugin, cfg)

        if cfg.has_option("Plugin","userparam") and agent == True:
            installUserParameter(plugin, cfg)
        
        if cfg.has_section("HelpItems") and server == True:
            installHelpItems(plugin, cfg)


#
# Script install function
#
def installScript(plugin, cfg):

    actionPrint("Installing Script to Zabbix agent")

    script_install_dir = zb_install_dir+"/"+zb_scripts_dir

    # check if Zabbix
    if not os.access(script_install_dir, os.W_OK):
        actionKO("Script directory not writable: "+script_install_dir)
        return

    # Plugin script file
    script_file = cfg.get("Plugin", "script.file")
    script_path = zp_plugins_dir+"/"+plugin+"/"+script_file

    # Check script file
    if not os.path.isfile(script_path):
        actionKO("Plugin script file missing : "+script_path)
        return
    
    # Copy script file
    shutil.copyfile(script_path, script_install_dir+"/"+script_file)

    actionOK()
    
    # Configure script
    if cfg.has_option("Plugin","script.conf") and cfg.has_section("ScriptProperties"):

        actionPrint("Configuring Script to Zabbix agent")
        print ""
        
        conf_file = cfg.get("Plugin", "script.conf")

        # Open config file
        prop = open (script_install_dir+"/"+conf_file, "w")
        
        # Parse config variables and write in file
        for key,value in cfg.items("ScriptProperties"):
            if value == "[PASSWORD]":
                value = getpass.getpass(key+" : ")
            else:
                tmp = raw_input(key+" ["+value+"] : ")
                if tmp != "":
                    value = tmp
            prop.write(key+"="+value+"\n")
        prop.flush()
        prop.close()
        
        actionPrint("Configure Script to Zabbix agent")
        actionOK()
    

#
# UserParameter install functions
#
def installUserParameter(plugin, cfg):

    actionPrint("Installing Userparameters to Zabbix agent")

    param_install_dir = zb_install_dir+"/"+zb_userparam_dir

    # check if Zabbix
    if not os.access(param_install_dir, os.W_OK):
        actionKO("Script directory not writable: "+param_install_dir)
        return

    param_file = cfg.get("Plugin", "userparam")
    param_path = zp_plugins_dir+"/"+plugin+"/"+param_file

    # Check param file
    if not os.path.isfile(param_path):
        actionKO("Plugin userparameter file missing : "+param_path)
        return

    # Open param file
    with open (param_path, "r") as myfile:
        data=myfile.readlines()
    
    # Change the Zabbix ins all dir
    for i in range(0,len(data)):
        data[i] = re.sub('/etc/zabbix', zb_install_dir, data[i]);
    
    # Write user parameter file
    with open (param_install_dir+"/"+param_file, "w") as myfile:
        myfile.writelines(data)

    actionOK()

#
# Help items install function
#
def installHelpItems(plugin, cfg):

    actionPrint("Installing help items to Zabbix server")

    conf_file = zb_install_dir+"/"+zb_server_conf

    # check Zabbix server configuration file
    if not os.access(conf_file, os.W_OK):
        actionKO("Zabbix server configuration not readable: "+conf_file)
        return

    # Open Zabbix configuration file
    ini_str = '[root]\n' + open(conf_file, 'r').read()
    ini_fp = StringIO.StringIO(ini_str)
    zab = ConfigParser.ConfigParser()
    zab.optionxform = str
    zab.readfp(ini_fp)
    
    # Get MySQL informations
    dbhost = " -h"+zab.get("root", "DBHost") if zab.has_option("root", "DBHost") else ""
    dbport = " -P"+zab.get("root", "DBPort") if zab.has_option("root", "DBPort") else ""
    dbname = " "+(zab.get("root", "DBName") if zab.has_option("root", "DBName") else "zabbix")
    dbuser = " -u"+(zab.get("root", "DBUser") if zab.has_option("root", "DBUser") else "zabbix")
    dbpass = " -p"+zab.get("root", "DBPassword") if zab.has_option("root", "DBPassword") else ""

    # Build MySQL insert request
    request=""

    for key,value in cfg.items("HelpItems"):
        request += "INSERT INTO help_items (itemtype, key_, description) "
        request += "Values (0, '"+key+"', '"+value+"') "
        request += "ON DUPLICATE KEY UPDATE "
        request += "itemtype = VALUES(itemtype),"
        request += "description = VALUES(description); "
    
    # Insert Help items in database
    os.popen("echo \""+request+"\" | mysql"+dbhost+dbport+dbuser+dbpass+dbname)
    p = os.popen("echo $?")
    if p.read().rstrip('\n') == "0":
        actionOK()
    else:
        actionKO("Failed populate database")

#
# Main part
#
if __name__ == "__main__":

    for item in sys.argv:
        if item == sys.argv[0]:
            continue
        
        arg = item.split('=')
        
        if arg[0] in ["-h", "--help"]:
            usage()
            sys.exit(0)
        elif arg[0] == "--dir":
            zb_install_dir = arg[1].rstrip("/")
        elif arg[0] == "--no-server":
            server = False
        elif arg[0] == "--no-agent":
            agent = False
        elif arg[0] == "list":
            function = listPlugins
        elif arg[0] == "install":
            function = installPlugins
        else:
            plugins.append(arg[0])

    if function == None:
        usage()
        sys.exit(1)
        
    function()
