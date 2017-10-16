#!/usr/bin/env python

import urllib
import json
import os
import comm_devices_pi
import random

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

dev_states = {}

completion_speeches = ["Voila!", "And then there was light.", "Shazam!", "There you go.", "You're all set.", "That should do it", "Ta daaaa!", "Sure thing", "Your wish is my command", "Yes, master!"]

with open('input.json') as doc:
    home_data = json.load(doc)
    U_ID = int(home_data['u_id'], 16)
    devices = home_data['devices']
    dev_states = home_data['dev_states']

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    #print(json.dumps(req, indent=4))
    #print("Google's request reached")
    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    #print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    #print("Making the result")
    print("Devices: ")
    print(devices)
    socket_command = []
    result = req.get("result")
    parameters = result.get("parameters")
    print(parameters)
    name = parameters.get("dev_names")
    print(name)
    number = parameters.get("number")
    print(number)
    action = result.get("action")
    print(action)
    if(name):
        if(name == "device" or name == "lightbulb"):
            if(not(number)):
                speech = "Sorry, this name is invalid. Please follow the naming rules for your devices."
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }
        if(number):
            name += " " + str(number)


    print("Extracted name:", name)

    if(action == "home.connect"):
        mode = parameters.get("mode")
        if(mode == "connect"):
            socket_command.extend("C")
            if name in devices:
                speech = "This device already exists. You cannot use two devices with the same name. Please choose a new name for this device."
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }
            else:
                x = list(devices.values())
                for i in range(1,len(devices) + 2):
                    if(i not in x):
                        socket_command.extend(str(i))
                speech = comm_devices_pi.connect(socket_command)
                if(speech == "Connected"):
                    devices[name] = i
                    dev_states[name] = 0
                    home_data['devices'] = devices
                    home_data['dev_states'] = dev_states
                    with open("input.json", "w") as jsonfile:
                        json.dump(home_data, jsonfile)
                    speech = "The device has been connected as " + name
                print("Response:")
                print(speech)
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }
        elif(mode == "disconnect"):
            socket_command.extend("D")
            if not(name in devices):
                speech = "This device does not exist in your house. I'm pretty sure you haven't connected this before."
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }
            else:
                socket_command.extend(str(devices[name]))
                speech = comm_devices_pi.disconnect(socket_command)
                if(speech == "Device disconnected"):
                    del devices[name]
                    del dev_states[name]
                    speech = name + " has been disconnected."
                    home_data['devices'] = devices
                    home_data['dev_states'] = dev_states
                    with open("input.json", "w") as jsonfile:
                        json.dump(home_data, jsonfile)
                print("Response:")
                print(speech)
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }

    elif(action == "home.control"):
        bulbs = parameters.get("bulbs")
        state = parameters.get("state")
        st = 0
        st_all_ind = 0
        if(len(devices) == 0):
            speech = "You haven't connected any devices yet."
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                # "contextOut": [],
                "source": "my_server"
                }
        if(not(name)):
            socket_command.extend("A")
            if("all" in bulbs):
                if(len(bulbs) > 1):
                    bulbs_temp = []
                    for i in bulbs:
                        if(i != "all"):
                            bulbs_temp.append(i);
                    bulbs = bulbs_temp
                else:
                    if(state[0] == "on"):
                        st_all_ind = 7
                    else:
                        st_all_ind = 0
                    socket_command.append(str(st_all_ind))
                    socket_command.append(str("7"))
                    print(socket_command)
                    speech = comm_devices_pi.light(socket_command)
                    speech = completion_speeches[random.randint(0,len(completion_speeches) - 1)]
                    for i in dev_states:
                        if(state[0] == "on"):
                            dev_states[i] |= st_all_ind
                        else:
                            dev_states[i] &= st_all_ind
                    home_data['dev_states'] = dev_states
                    with open("input.json", "w") as jsonfile:
                        json.dump(home_data, jsonfile)
                    return {
                        "speech": speech,
                        "displayText": speech,
                        #"data": {},
                        # "contextOut": [],
                        "source": "my_server"
                        }
            bulbs_dict = []
            for i in range(len(bulbs)):
                if(bulbs[i] == "red green"):
                    try:
                        bulbs_dict.append(["red",state[i]])
                        bulbs_dict.append(["green",state[i]])
                    except:
                        bulbs_dict.append(["red",state[len(state) - 1]])
                        bulbs_dict.append(["green",state[len(state) - 1]])
                elif(bulbs[i] == "green yellow"):
                    try:
                        bulbs_dict.append(["green",state[i]])
                        bulbs_dict.append(["yellow",state[i]])
                    except:
                        bulbs_dict.append(["green",state[len(state) - 1]])
                        bulbs_dict.append(["yellow",state[len(state) - 1]])
                elif(bulbs[i] == "red yellow"):
                    try:
                        bulbs_dict.append(["red",state[i]])
                        bulbs_dict.append(["yellow",state[i]])
                    except:
                        bulbs_dict.append(["red",state[len(state) - 1]])
                        bulbs_dict.append(["yellow",state[len(state) - 1]])
                else:
                    try:
                        bulbs_dict.append([bulbs[i], state[i]])
                    except:
                        bulbs_dict.append([bulbs[i], state[len(state) - 1]])
            st = 0
            for i in bulbs_dict:
                if(i[0] == "red"):
                    st |= 4
                    if(i[1] == "on"):
                        st_all_ind |= 4
                    else:
                        i[1] = "on"
                elif(i[0] == "green"):
                    st |= 2
                    if(i[1] == "on"):
                        st_all_ind |= 2
                    else:
                        i[1] = "on"
                elif(i[0] == "yellow"):
                    st |= 1
                    if(i[1] == "on"):
                        st_all_ind |= 1
                    else:
                        i[1] = "on"
            socket_command.append(str(st_all_ind))
            socket_command.append(str(st))
            print("Command")
            print(socket_command)
            speech = comm_devices_pi.light(socket_command)
            for i in dev_states:
                effect = st & 4
                if(effect):
                    dev_states[i] &= 3
                    dev_states[i] |= (st_all_ind & 4)
                effect = st & 2
                if(effect):
                    dev_states[i] &= 5
                    dev_states[i] |= (st_all_ind & 2)
                effect = st & 1
                if(effect):
                    dev_states[i] &= 6
                    dev_states[i] |= (st_all_ind & 1)
            home_data['dev_states'] = dev_states
            with open("input.json", "w") as jsonfile:
                json.dump(home_data, jsonfile)
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                # "contextOut": [],
                "source": "my_server"
                }

        else:
            socket_command.extend("L")
            if(not(name in devices)):
                speech = "You haven't connected this device yet. Maybe you should do that first."
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }
            else:
                dev_id = devices[name]
                st = dev_states[name]
                socket_command.extend(str(dev_id))
            if("all" in bulbs):
                if(state[0] == "on"):
                    st = 7
                else:
                    st = 0
                socket_command.append(str(st))
                print("Command for all with name:")
                print(socket_command)
                speech = comm_devices_pi.light(socket_command)
                print("Response:")
                print(speech)
                if(speech == "Voila!"):
                    for i in dev_states:
                        dev_states[i] = st
                    home_data['dev_states'] = dev_states
                    with open("input.json", "w") as jsonfile:
                        json.dump(home_data, jsonfile)
                speech = completion_speeches[random.randint(0,len(completion_speeches) - 1)]
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }
            else:
                bulbs_dict = []
                bulbs_list = []
                if(len(bulbs) == len(state)):
                    for i in range(len(bulbs)):
                        bulbs_dict.append((bulbs[i],state[i]))
                else:
                    bulbs_dict.append((bulbs[i], state[0]))
                for i in bulbs_dict:
                    if(i[0] == "red green"):
                        bulbs_list.append(("red", i[1]))
                        bulbs_list.append(("green", i[1]))
                    elif(i[0] == "red yellow"):
                        bulbs_list.append(("red", i[1]))
                        bulbs_list.append(("yellow", i[1]))
                    elif(i[0] == "green yellow"):
                        bulbs_list.append(("green", i[1]))
                        bulbs_list.append(("yellow", i[1]))
                    else:
                        bulbs_list.append(i)
                print("State:",st)
                for i in bulbs_list:
                    print("i:",i)
                    if(i[0] == "red"):
                        st &= 3
                        if(i[1] == "on"):
                            st |= 4
                    if(i[0] == "green"):
                        st &= 5
                        if(i[1] == "on"):
                            st |= 2
                    if(i[0] == "yellow"):
                        st &= 6
                        if(i[1] == "on"):
                            st |= 1
                print("New State:", st)
                socket_command.append(str(st))
                print(socket_command)
                speech = comm_devices_pi.light(socket_command)
                print("Response:")
                print(speech)
                if(speech == "Voila!"):
                        dev_states[name] = st
                home_data['dev_states'] = dev_states
                with open("input.json", "w") as jsonfile:
                    json.dump(home_data, jsonfile)
                speech = completion_speeches[random.randint(0,len(completion_speeches) - 1)]
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }


    elif(action == "home.tell"):
        mode = parameters.get("mode")
        dev_list = ""
        if(mode == "tell"):
            if(len(devices) == 0):
                speech = "Nothing at the moment."
                return {
                    "speech": speech,
                    "displayText": speech,
                    #"data": {},
                    # "contextOut": [],
                    "source": "my_server"
                    }
            x = list(devices.keys())
            for i in x:
                if(i == x[-1]):
                    dev_list += "and " + i + "."
                else:
                    dev_list += i + ", "
            if(len(devices) == 1):
                dev_list = dev_list[4:]
            speech = "I am connected to " + dev_list
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                # "contextOut": [],
                "source": "my_server"
                }
    elif(action == "home.show"):
        mode = parameters.get("mode")
        if(not(name) in devices):
            speech = "This device doesn't exist in your home."
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                # "contextOut": [],
                "source": "my_server"
                }
        else:
            print("Reached here")
            print(devices[name])
            print(dev_states[name])
            speech = comm_devices_pi.show(["S", str(devices[name]), str(dev_states[name])])
            print("Reached here too")
            if(speech == "Here"):
                speech = name + " should be flashing right about now"
            return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            # "contextOut": [],
            "source": "my_server"
            }
            
    else:
        return {"speech": "I'm sorry! I cannot perform this action",
        "displayText": "I'm sorry! I cannot perform this action",
        #"data": {},
        # "contextOut": [],
        "source": "my_server"}

if __name__ == '__main__':
    port = 5000

    print("Starting app on port", str(port))

    app.run(debug=False, port=port, host="")
