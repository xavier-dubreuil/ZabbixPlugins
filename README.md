ZabbixPlugin
============

Overview
--------

ZabbixPlugin contains templates and scripts for those applications:
- Apache2
- LM-Sensors
- MySQL
- SabNZBd

REQUIREMENTS
------------

ZabbixPlugin required :
- Python

Applications
------------

### Apache2

Included in the template:
- Slots occupations (Items, Graph)
- Version (Item)

### LM-Sensors

Included in the template :
- Fans (Discovery, Items, Triggers, Graph)
- Temperatures (Discovery, Items, Triggers, Graph)
- Voltages (Discovery, Items, Triggers, Graph)

Required :
- lm-sensors installed and configured

All triggers are set from lm-sensors values, make sure values are correctly defined

### MySQL

Included in the template :
- Databases size : (Discovery, Items, Triggers)

### SabNZBd

Included in the template :
- Disk Usage (Items, Graphs, Screen)
- Download speed (Items, Graph, Screen)
- Queue information (Item, Graph)
- Ping (Item, trigger)
- Version (Item, Screen)

Installation
------------

The installation is done using zabbix-plugin script :

List all the plugins available

    ./zabbix-plugin list

Installation of one or many plugins

    ./zabbix-plugin install lm-sensors mysql


Here is the help of the install script :

    Zabbix plugin installer

    ./zabbix-plugin -h|--help
    ./zabbix-plugin list
    ./zabbix-plugin [-dir=Zabbix_dir] [--no-server|--no-agent] install plugin1 plugin2 ...

    Install :
      --dir=Zabbix_dir : Set the Zabbix install directory
      --no-server      : Do not install Zabbix Server part
      --no-agent       : Do not install Zabbix Agent part

The default Installation directory is /etc/zabbix/. The installer will populate :
- zabbix_agentd_conf.d  : UserParameter configurations
- zabbix_agentd_scripts : Plugons scripts 

The server installation is used to add items keys in the database.
The database connection informations are read from zabbix_server.conf.
Make sure this file is present in the installation directory.