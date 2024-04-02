"""
<plugin key="IthoWifi" name="IthoWifi" author="Mark Heinis" version="0.0.1" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-Itho-Wifi-Plugin">
    <description>
        Plugin for sending commands to your Itho Wifi module.
        More info on that itho wifi module here: https://github.com/arjenhiemstra/ithowifi
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="nrg-itho-abcd.local"/>
        <param field="Port" label="Port" width="30px" required="true" default="80"/>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json
import requests

class IthoPlugin:
    httpConn = None
    oustandingPings = 0
    sendLow = '/api.html?rfremotecmd=low'
    sendMedium = '/api.html?rfremotecmd=medium'
    sendHigh = '/api.html?rfremotecmd=high'

    def __init__(self):
        self.update_interval = 3
        self.debug_level = None

    def onStart(self):
        if Parameters["Mode6"] == "":
            Parameters["Mode6"] = "-1"
        if Parameters["Mode6"] != "0": 
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
            
        self.debug_level = Parameters["Mode6"]
        
        if ( 1 not in Devices ):
            Options = {
                "LevelActions": "|",
                "LevelNames": "Off|Low|Medium|High",
                "LevelOffHidden": "true",
                "SelectorStyle": "0"
            }
            Domoticz.Device(Name="Ventilation", Unit=1, TypeName="Selector Switch", Image=7, Options=Options).Create()
            Domoticz.Log("Ventilation selector device created.")
        
    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called: " + str(Status) + " | " + Connection.Address + ":" + Connection.Port)
        return True

    def onStop(self):
        Domoticz.Debug("Itho Plugin stopped")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called with data: " + str(Data))

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if Unit == 1:  # Ventilation selector device
            address = Parameters["Address"]
            port = Parameters["Port"]
            base_url = f"http://{address}:{port}"
            if Level == 0 or Level == 10:  # Low
                Domoticz.Debug("Sending Low command")
                response = requests.get(base_url + self.sendLow)
                Domoticz.Debug("Response from server: " + str(response.status_code))
                Devices[Unit].Update(nValue=0, sValue="10")
            elif Level == 20:  # Medium
                Domoticz.Debug("Sending Medium command")
                response = requests.get(base_url + self.sendMedium)
                Domoticz.Debug("Response from server: " + str(response.status_code))
                Devices[Unit].Update(nValue=20, sValue="20")
            elif Level == 30:  # High
                Domoticz.Debug("Sending High command")
                response = requests.get(base_url + self.sendHigh)
                Domoticz.Debug("Response from server: " + str(response.status_code))
                Devices[Unit].Update(nValue=30, sValue="30")

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called for connection to: " + Connection.Address + ":" + Connection.Port)
 
global _plugin
_plugin = IthoPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
