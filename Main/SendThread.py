#!/usr/bin/env python
import threading
import time
import json

import pycurl
from io import BytesIO

#Networking
serverURL = 'http://127.0.0.1/ServerJSONThreadModel.php' #PHP Server address (local host when using XAMPP)
alarmID = '255' #Alarm Unit registration number

#File IO
logFilename = "TriggerLog.txt"

#Delays
delay_IFS = 0.1
delay_backoff = 1

class sendThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.alive = False
    def run(self):
        global buffer
        global bufferEmpty
        #Define States
        IDLE = 1
        SEND = 2
        DISCONNECTED = 3
        
        currentState = IDLE
        response = [False,""]
        k = 0
        while self.alive:
            time.sleep(delay_IFS)
            if currentState == IDLE:
                if not bufferEmpty:
                    currentState = SEND
                    response = transmit()
                    k = 0
            if currentState == SEND:
                if (response[0] == True) and (bufferEmpty):
                    currentState = IDLE
                if (response[0] == True) and (not bufferEmpty):
                    response = transmit()
                    k = 0
                if response[0] == False:
                    response = transmit()
                    k = k + 1
                if k >= 3:
                    print("LCD Output:\nOffline\nError: " + str(response[1]))
                    response = transmit()
                    currentState = DISCONNECTED
            if currentState == DISCONNECTED:
                time.sleep(delay_backoff)
                if response[0] == True:
                    currentState = IDLE
                    print("LCD Output:Reconnected")
                if response[0] == False:
                    #print("LCD Output:\nOffline\nError No.: " + str(response[1]))
                    response = transmit()

def transmit():
    """Transmit the following tuple to server:
    (AlarmID,Timestamp1,Timestamp2...)"""
    global buffer
    global bufferEmpty
    try:
        threadLock.acquire()
        post_data = {'alarmID': alarmID,'timestamps':buffer}
            
        jsonEncoder = json.JSONEncoder()
        recieveBuffer = BytesIO() #Captures reply from Server
        c = pycurl.Curl() #Create Curl Object
        c.setopt(c.URL, serverURL)
        c.setopt(c.POSTFIELDS,jsonEncoder.encode(post_data))
        c.setopt(c.WRITEDATA, recieveBuffer)


        c.perform() #Make transfer and recieve URL information
        c.close()
        if os.path.isfile(logFilename):
            os.remove(logFilename)
        body = recieveBuffer.getvalue()
        print(body.decode('iso-8859-1')) #Decode bytes to string
        buffer = []
        bufferEmpty = True
        threadLock.release()
        return [True,""]
    except pycurl.error as e:
        c.close()
        #print("Connection Failed")
        with open(logFilename,'w') as f:
            json.dump(buffer,f)

        try:
            threadLock.release()
        except:
            pass

        return [False,str(e.args[0])]##########Error No.
    
