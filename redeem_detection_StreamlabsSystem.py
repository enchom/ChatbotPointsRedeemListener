#---------------------------
#   Import Libraries
#---------------------------

import clr
clr.AddReference("IronPython.Modules.dll")
clr.AddReference("websocket-sharp.dll")

import time
import os
import sys
import json
import WebSocketSharp
import codecs

def log(s):
    Parent.Log(ScriptName, str(s))

#---------------------------
#   Settings class
#---------------------------
class MySettings(object):
    def __init__(self, settings_file=None):
        try:
            with codecs.open(settings_file, encoding="utf-8-sig", mode="r") as f:
                saved_settings = json.load(f, encoding="utf-8")
            self.reload(saved_settings)
        except:
            self.UserId = ''
            self.OAuth = ''

    def reload(self, json_data):
        self.UserId = json_data['UserId'].strip()
        self.OAuth = json_data['OAuth'].strip()

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Redeem Detection"
Website = None
Description = "Please enter valid OAuth token and User ID"
Creator = "Enchom"
Version = "1.0.0.0"

#---------------------------
#   Global Variables
#---------------------------
global NotificationHandler
NotificationHandler = None
global ws
ws = None

SettingsFile = ""
ScriptSettings = None

TOPIC = 'channel-points-channel-v1'

def start_websocket():
    global ws
    if ws == None:
        ws = WebSocketSharp.WebSocket('wss://pubsub-edge.twitch.tv')
        ws.OnOpen += OnOpen
        ws.OnClose += OnClose
        ws.OnMessage += OnMessage
        ws.OnError += OnError
        ws.Connect()

def stop_websocket():
    global ws
    if ws != None:
        ws.Close()
        ws = None
        
def restart_websocket():
    global ws
    stop_websocket()
    start_websocket()

unacked_pings = 0
def ping():
    global ws, unacked_pings
    if unacked_pings > 3:
        restart_websocket()
    elif ws != None:
        conn = {}
        conn['type'] = 'PING'
        ws.Send(json.dumps(conn))

def pong():
    global unacked_pings
    unacked_pings = 0

def OnOpen(ws, e):
    conn = {}
    conn['type'] = 'LISTEN'
    conn['data'] = {
        'auth_token': ScriptSettings.OAuth,
        'topics': [TOPIC + '.' + ScriptSettings.UserId]
    }
    ws.Send(json.dumps(conn))

def OnClose(ws, e):
    pass

def OnMessage(ws, e):
    data = json.loads(e.Data)
    
    if data['type'] == 'PONG':
        pong()
    elif data['type'] == 'RESPONSE':
        if len(data['error']) == 0:
            log('Response: Successful')
        else:
            log('Response: ' + data['error'])
    elif data['type'] == 'RECONNECT':
        restart_websocket()
    else:
        NotificationHandler.on_event(data)

def OnError(ws, e):
    log(e.Message)
    log(e.Exception)
    

#---------------------------
#   Notification Handling
#---------------------------

class RedeemHandler(object):
    def __init__(self):
        pass

    def on_event(self, event):
        """
        The format of the event is completely untested. 
        
        The script subscribes only to reward-redeeming topic, but occasionally there can be other events (e.g. 'connected').
        Thus it is best to only react to a specific type only.
        
        An example format can be found in https://dev.twitch.tv/docs/pubsub under "Example: Channel Points Event Message".
        
        Assuming the correctness of the described format, some common values would be:
        
        user - event['data']['redemption']['user']['display_name']
        reward name - event['data']['redemption']['reward']['title']
        reward cost - event['data']['redemption']['reward']['cost']
        """
        if event['type'] == 'reward-redeemed':
            Parent.SendStreamMessage('Detected reward redeemed')
#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    global NotificationHandler, SettingsFile, ScriptSettings

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), 'Settings')
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    SettingsFile = os.path.join(os.path.dirname(__file__), 'Settings', 'settings.json')
    ScriptSettings = MySettings(SettingsFile)

    #   Start handler
    NotificationHandler = RedeemHandler()
    start_websocket()

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
ticks = 0
def Tick():
    global ticks
    ticks += 1
    if ticks % 500 == 0:
        ping()
        ticks = 0
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    stop_websocket()
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    if state:
        start_websocket()
    else:
        stop_websocket()

    return

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(json_data):
    global ScriptSettings
    json_data = json.loads(json_data)
    ScriptSettings.reload(json_data)

    ui_path = os.path.join(os.path.dirname(__file__), 'UI_Config.json')
    with open(ui_path, 'r') as f:
        json_ui = json.load(f)
    json_ui['UserId']['value'] = json_data['UserId'].strip()
    json_ui['OAuth']['value'] = json_data['OAuth'].strip()
    with open(ui_path, 'w') as f:
        f.write(json.dumps(json_ui, indent=4, sort_keys=True))

    return