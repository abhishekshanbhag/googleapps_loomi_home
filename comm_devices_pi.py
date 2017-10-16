import serial

from datetime import datetime
import json


with open('input.json') as doc:
    data = json.load(doc)
    U_ID = int(data['u_id'], 16)

#ser = serial.Serial('/dev/tty.usbserial-A601D97W') #For Mac
ser = serial.Serial('/dev/ttyUSB0')    #For RPi

def connect(params):
    mode = params[0]
    dev_id = hex(int(params[1]))
    ser.write(bytes.fromhex('7e'))
    ser.write(mode.encode())
    for i in range(0,12):
        uid_byte = hex((U_ID >> 8*i) & 0xff)
        try:
            ser.write(bytes.fromhex(uid_byte[2:]))
        except:
            ser.write(bytes.fromhex('0'+uid_byte[2:]))
    curr = datetime.now().second
    while(ser.in_waiting == 0 and datetime.now().second < (curr + 2)):
        pass
    if(ser.in_waiting == 0):
        ser.write(bytes.fromhex('00'))
        print("No device visible")
        return "Sorry! This device is not visible to me."
    else:
        l = int(ser.read().decode())
        while(ser.in_waiting < l):
            pass
        ack = (ser.read()).decode()
        if(ack == 'C'):
            try:
                #print(dev_id)
                ser.write(bytes.fromhex(dev_id[2:]))
                #print(bytes.fromhex(dev_id[2:]))
            except:
                #print("Reached here")
                ser.write(bytes.fromhex('0'+dev_id[2:]))
                #print(bytes.fromhex('0'+dev_id[2:]))
                return "Connected"
    ser.flush()

def light(params):
    mode = params[0]
    dev_id = hex(int(params[1]))
    state = hex(int(params[2]))
    ser.write(bytes.fromhex('7e'))
    ser.write(mode.encode())
    for i in range(0,12):
        uid_byte = hex((U_ID >> 8*i) & 0xff)
        try:
            ser.write(bytes.fromhex(uid_byte[2:]))
        except:
            ser.write(bytes.fromhex('0'+uid_byte[2:]))
    try:
        ser.write(bytes.fromhex(dev_id[2:]))
    except:
        ser.write(bytes.fromhex('0'+dev_id[2:]))
    try:
        ser.write(bytes.fromhex(state[2:]))
    except:
        ser.write(bytes.fromhex('0'+state[2:]))
    if(mode == "L"):
        curr = datetime.now().second
        while(ser.in_waiting == 0 and datetime.now().second < (curr + 2)):
            pass
        if(ser.in_waiting == 0):
            print("Device",params[1],"disconnected.")
            return "I can't seem to be abe to talk to device "+params[1]+" right now. Try again!"
        else:
            l = int(ser.read().decode())
            while(ser.in_waiting < l):
                pass
            ack = (ser.read()).decode()
            ser.flush()
            print("Success")
            return "Voila!"
    else:
        return "Voila!"


def disconnect(params):
    mode = params[0]
    dev_id = hex(int(params[1]))
    ser.write(bytes.fromhex('7e'))
    ser.write(mode.encode())
    for i in range(0,12):
        uid_byte = hex((U_ID >> 8*i) & 0xff)
        try:
            ser.write(bytes.fromhex(uid_byte[2:]))
        except:
            ser.write(bytes.fromhex('0'+uid_byte[2:]))
    try:
        ser.write(bytes.fromhex(dev_id[2:]))
    except:
        ser.write(bytes.fromhex('0'+dev_id[2:]))
    curr = datetime.now().second
    while(ser.in_waiting == 0 and datetime.now().second < curr + 2):
        pass
    if(ser.in_waiting == 0):
        print("Device not found.")
        return "I can't find this device."
    else:
        l = int((ser.read()).decode())
        while(ser.in_waiting < l):
            pass
        data = (ser.read()).decode()
        if(data == "D"):
            return "Device disconnected"

def show(params):
    mode = params[0]
    dev_id = hex(int(params[1]))
    state = hex(int(params[2]))
    print(dev_id)
    print(state)
    ser.write(bytes.fromhex('7e'))
    ser.write(mode.encode())
    for i in range(0,12):
        uid_byte = hex((U_ID >> 8*i) & 0xff)
        try:
            ser.write(bytes.fromhex(uid_byte[2:]))
        except:
            ser.write(bytes.fromhex('0'+uid_byte[2:]))
    try:
        print(bytes.fromhex(dev_id[2:]))
        ser.write(bytes.fromhex(dev_id[2:]))
        print("senttrial")
    except:
        ser.write(bytes.fromhex('0'+dev_id[2:]))
        print("Sent except")
    try:
        ser.write(bytes.fromhex(state[2:]))
    except:
        ser.write(bytes.fromhex('0'+state[2:]))
    curr = datetime.now().second
    while(ser.in_waiting == 0 and datetime.now().second < curr + 2):
        pass
    if(ser.in_waiting == 0):
        print("Device not found.")
        return "I can't communicate with this device right now."
    else:
        l = int((ser.read()).decode())
        while(ser.in_waiting < l):
            pass
        data = (ser.read()).decode()
        if(data == "S"):
            return "Here"
