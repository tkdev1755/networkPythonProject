
import socket
import random as rd
from enum import Enum
import time
from functools import partial

LOCALHOSTIP  = "127.0.0.1"
LOCALHOSTPORT = 5005

print("NetworkEngine init START")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(True)
print("Socket opened")

def split(string):
    return string.split(";")

class Actions:
        """
        
        Class which contains actions functions and 
        have the function which generates the network command 
        to send to all other instances
        
        """
        def __init__(self):
               pass
        def addAction(self,id, data, dst):
                dst[id] = data
        def modifyAction(self,id, data, dst):
                dst[id] = data
        def deleteAction(self,id, data, dst):
                if id in dst:
                       dst.pop(id)
                else:
                       pass
        
        def getNetworkAction(self,action:str,id, data):
               return f"{action.capitalize()};{id};{data}"
        
        def setAction(self,action, id, data,dst):
               FunctionsENUM[action].value(self,id,data,dst)
               networkAction = self.getNetworkAction(action,id,data)
               return networkAction
        
        def launchAction(strAction,dst):
               command,id,data = split(strAction)
               FunctionsENUM[command].value(id,data,dst) 

class FunctionsENUM(Enum):
       add = partial(Actions.addAction)
       modify = partial(Actions.modifyAction)
       delete = partial(Actions.deleteAction)




def getRandomAction(src):
        functionsLen = len(FunctionsENUM)
        randomNumberAction = rd.randint(0, functionsLen-1)
        randomID = rd.choice(list(src.keys()))
        data = src[randomID] + 50
        selectedFunction = list(FunctionsENUM)[randomNumberAction]
        if selectedFunction.name == "add":
               randomID = max(list(src.keys()))+1
        networkAction = actions.setAction(selectedFunction.name,randomID,data,src)
        return networkAction

data = {
       1 : 20,
       2 : 340,
       3 : 230
}

actions = Actions()
networkAction = getRandomAction(data)

try:
        print("network action is",networkAction)
        data = sock.sendto(bytes(networkAction, "utf-8"),(LOCALHOSTIP,LOCALHOSTPORT))
        print("Sent data : ",data)
except:
       print("Error")
while 1:
        
        try: 
                
                data, addr = sock.recvfrom(40)
                print("ADDR IS ", addr)
                tempADDR = addr
                #Actions.launchAction(data.decode("utf-8"),data)
                time.sleep(2)
                print("SENT DATA")
        except BlockingIOError as z:
               print("Waiting for data")
        except Exception as e :
                print("Error while doing script : ",e)
                



