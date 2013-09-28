#!/usr/bin/python

import sys
import os
import ConfigParser
import getpass

# Script path
scriptPath = os.path.abspath(os.path.dirname(sys.argv[0]))

class ZabbixPlugins:

    # 
    functionRef = None
    
    configRef = None
    
    configFile = None

    config = ConfigParser.RawConfigParser()

    def __init__(self, functionRef, configRef, configFile):
        
        self.functionRef = functionRef
        
        self.configRef = configRef
        
        self.configFile = scriptPath+"/"+configFile
        
        try:
            self.config.read(self.configFile)
        except:
            None

    #
    # Script print functions
    #
    def cmd(self, str):
        sys.stdout.write(str.ljust(50))
        sys.stdout.flush()
        
    def cmdOK(self):
        print "[ \033[32mOK\033[0m ]"
    
    def cmdKO(self, error):
        print "[ \033[31mKO\033[0m ] : "+error
    
    
    
    def inputValue(self, text, default, secret):
    
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
    def configure(self):
    
        # initiate configuration
        config = ConfigParser.RawConfigParser()
    
        # Parsing erence sections
        for section in self.configRef:
        
            # add the section to configuration
            config.add_section(section["name"])
            
            # Parsing section options
            for option in section["options"]:
                
                # Get value from keyboard
                value = self.inputValue(option["desc"], option["default"], option["secret"])
                
                # Add option value in configuration
                config.set(section["name"], option["name"], value)
                
        # Write configuration to file
        self.cmd("Writing configuration file")
        try:
            handle_file = open(self.configFile, 'wb')
            config.write(handle_file)
        except:
            self.cmdKO('Unable to write the configuration file: '+self.configFile)
            sys.exit(1)
        self.cmdOK()
    
    def get(self, section, option):
    
        if not self.config.has_section(section):
            return False
        
        if not self.config.has_option(section, option):
            return False
        
        return self.config.get(section, option)

    
    def execute(self, cmd):
        
        # Execute cmd
        res = os.popen(cmd)
        
        # Get cmd return value
        p = os.popen("echo $?")
        
        # Return false if cmd failed
        if p.read().rstrip('\n') != "0":
            return False
        
        return res.readlines()
    
    
    def start(self):
    
        # Get the function name on first argument
        func  = sys.argv[1] if len(sys.argv) > 1 else ""
    
        # Get the parameter on second argument
        param = sys.argv[2:] if len(sys.argv) > 2 else ""
    
        # Check if function exists in functions array
        if func in self.functionRef and len(sys.argv) - 2 == self.functionRef[func]["argv"]:
    
            # Call the function with the parameter
            return self.functionRef[func]["function"](param)
        
        return False