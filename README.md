ZabbixPlugin
============

Overview
--------

ZabbixPlugin contains templates and scripts for those applications:
- Apache2
- LM-Sensors
- MySQL
- SabNZBd

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

Coming soon

