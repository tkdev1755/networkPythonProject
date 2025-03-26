#fonctions permettant l'interprétation de messages "Action;ID;Data"
import json
import random as rd

from pygame.display import update
import uuid
import time
import sys
import socket


#"Set;ID;Data" demande la modification de l'état de l'objet d'id ID


'''
    Log Modifications 
    25/03/25@tkdev1755 : Déplacé les fonctions decoupe,ptuple_to_tuple vers la classe MessageDecoder
    25/03/25@tkdev1755 : Déplacé les fonctions interpret_message du GameEngine vers la classe MessageDecoder

'''
#il faut qu'on s'accorde sur le contenu de Data

'''def decoupe(string):
    return string.split(";")

def ptuple_to_tuple(ptuple): #passe une string "(a,..,z)" en tuple (a,..,z)
    return tuple(map(str,ptuple[1:-1].split(",")))

#fonction pour créer un message
def create_message(action, id, data):
    return str(action)+";"+str(id)+";"+str(data)'''

class MessageDecoder:

    def __init__(self,gameEngine,networkEngine):
        self.gameEngine = gameEngine
        self.networkEngine = networkEngine

    @staticmethod
    def create_message(action, elementId, data):
        return str(action) + ";" + str(elementId) + ";" + str(data)

    @staticmethod
    def decoupe(string):
        return string.split(";")

    @staticmethod
    def ptuple_to_tuple(ptuple):  # passe une string "(a,..,z)" en tuple (a,..,z)
        return tuple(map(str, ptuple[1:-1].split(",")))

    def interpret_message(self,message):
        action, id, data=message.split(";")
        if action=="SetUnit":
            self.gameEngine.move_by_id(int(id),MessageDecoder.ptuple_to_tuple(data))
        elif action=="SetBuilding":
            self.gameEngine.set_building_by_id(int(id),MessageDecoder.ptuple_to_tuple(data))
        elif action=="SetResource":
            self.gameEngine.set_resource_by_position(int(id),MessageDecoder.ptuple_to_tuple(data))
        elif action=="AskSize":
            #self.gameEngine.send_world_size()
            pass
        elif action == "SetUnitHealth":
            self.gameEngine.update_unit_health(int(id), MessageDecoder.ptuple_to_tuple(data))
        elif action == "get":
            print("Someone asking for property !")
            strID = self.ptuple_to_tuple(id)
            realID = (int(strID[0]), int(strID[1]))
            if self.networkEngine.isOwner(realID):
                decodedData = self.networkEngine.decodeMessage(data)
                strPosition = self.ptuple_to_tuple(decodedData[2])
                realPosition = (int(strPosition[0]), int(strPosition[1]))
                self.networkEngine.yieldProperty(realID,decodedData[0],decodedData[1],realPosition)
                print("Yielded Property Successfully !")
            else:
                pass
        elif action == "fget":
            print("FORCE GET !!!")
            print("Data is ", data)
            strID = self.ptuple_to_tuple(id)
            realID = (int(strID[0]),int(strID[1]))
            if self.networkEngine.isOwner(realID):
                decodedData = self.networkEngine.decodeMessage(data)
                self.networkEngine.removeObject(realID,decodedData[1])
                print("Yielded Successfully the property")

        elif action == "yield":
            print("Someone is yielding a Property !")
            strID = self.ptuple_to_tuple(id)
            realID = (int(strID[0]), int(strID[1]))
            if not self.networkEngine.isOwner(realID):
                decodedData = self.networkEngine.decodeMessage(data,messageType="yield")
                print("Message decoded properly!")
                if decodedData[1] == self.networkEngine.name:
                    print("The property seems to be for me!")
                    self.networkEngine.addObject(realID,decodedData[0])
                    self.networkEngine.updateAskStatus()
                    if decodedData[2] == "Tile":
                        self.networkEngine.updateTileFromNetworkData(data)

                    print("The property was for me, yielded it successfully")

        elif action == "getRTile":
            print("Someone asked for a Resource Tile")
            if not self.gameEngine.joinNetworkGame:
                resList = self.gameEngine.map.resources["Gold"] + self.gameEngine.map.resources["Wood"]
                choice = rd.choice(resList)
                self.networkEngine.yieldProperty((choice[0],choice[1]), id, "Tile", (choice[0],choice[1]))


        else:
            print("Action inconnue pour le moment:",action)
    def getObject(self, data):

        pass




'''
#fonction pour interpréter un message 
def interpret_message(message):
    action, id, data=message.split(";")
    if action=="SetPosition":
        move_by_id(id, (data,))
'''
'''
#fonction pour déplacer un objet par son id, IL FAUDRA LA METTRE EN METHODE DE LA CLASSE GAME_ENGINE
def move_by_id(self,id,position): #juste, remplace la position de l'unité d'id id par position 
        for player in self.players: #cherche l'unité d'id id et s'arrête une fois trouvée
            for unit in player.units:
                if unit.id==id:
                    unit.position=position
                    return
            #unité non trouvée, càd nouvelle unité
            Unit.spawn_unit(None,Villager,position[0],position[1],self.players[0],self.map)
'''

class NetworkEngine:

    def __init__(self, gameEngine=None, size  = None):
        self.socket = None
        self.gameEngine = gameEngine
        self.name = f"PL-{uuid.uuid1().hex[:10]}"
        self.size = size
        self.MAXSIZE = 2048
        self.inventory = {"Resources" : [], "Tiles" : []}
        self.askQueue = []
        self.lastAskedData = None
        self.ableToAsk = True
        self.timeSinceLastQ = 0

    def initInventory(self,gameCreator=False):
        for i in self.gameEngine.map.grid:
            for k in i:
                if not(k.resource is None):
                    print(k.resource)

        if gameCreator:
            self.inventory["Resources"] = [v for v in self.gameEngine.map.resources["Gold"]] + [v for v in self.gameEngine.map.resources["Wood"]]
            for i in self.gameEngine.map.grid:
                for k in i:
                    self.inventory["Tiles"].append((k.x, k.y))
        else:
            allBuildingPositions = []
            buildingsInstances = self.gameEngine.players[0].buildings
            for i in buildingsInstances:
                allTiles = i.getAllTiles()
                for tile in allTiles:
                    allBuildingPositions.append(tile)
            for i in allBuildingPositions:
                self.inventory["Tiles"].append(i)
        print("Inventory at the end is")
        #print(self.inventory)
    #Functions which asks for all the Tiles the Game has to offer
    def askForOwnedTiles(self):
        for i in self.inventory["Tiles"]:
            self.forceProperty(i,i,"Tiles")
            time.sleep(0.2)

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("127.0.0.1", 5006))
        self.socket.setblocking(False)  # socket non bloquante

    def setSocketBlocking(self, blocking):
        self.socket.setblocking(blocking)

    def closeSocket(self):
        self.socket.close()

    def recvMessage(self):
        try:
            data,addr = self.socket.recvfrom(self.MAXSIZE)
            return data
        except BlockingIOError as e:
            raise BlockingIOError
        except ConnectionResetError as e:
            print("ERREUR CONNEXION :",e)
            raise e

    def send_message(self,message):
        try:
            self.socket.sendto(bytes(message, 'utf-8'), ("127.0.0.1", 5005))
        except BlockingIOError:
            pass

    def isOwner(self,id):
        print("[NETWORKENGINE] Seems to be the owner for id :",id)
        status = True if (id in self.inventory["Tiles"]) or (id in self.inventory["Resources"]) else False# TEMP - à venir ici condition vraie si on est bien propriétaire ou fausse si on ne l'est pas
        return status

    def updateAskStatus(self):
        self.ableToAsk = True


    def getRTile(self):
        pMessage = f"getRTile;{self.name}; "
        self.ableToAsk = False
        self.send_message(pMessage)

    def askForProperty(self, elementId,position,elementType):
        print("[NETWORKENGINE] Asking property for :",id)

        pMessage = f"get;{elementId};{{\"player\":\"{self.name}\",\"type\":\"{elementType}\",\"position\":\"{position}\"}}"
        self.ableToAsk = False
        self.timeSinceLastQ = time.time()
        self.lastAskedData = elementId
        self.send_message(pMessage)

    def removeObject(self,elementId,elementType):
        self.inventory[elementType].remove(elementId)

    def addObject(self,elementId, elementType):
        self.inventory[elementType].append(elementId)

    def forceProperty(self,elementId,position, elementType):
        pMessage = f"fget;{elementId};{{\"player\":\"{self.name}\",\"type\":\"{elementType}\",\"position\":\"{position}\"}}"
        self.send_message(pMessage)

    def yieldProperty(self,elementId,newOwner,elementType,position):
        if self.isOwner(elementId):
            encodedData = self.encodeGameObject(elementType,elementId,position)
            data = f"{{\"from\" : \"{self.name}\",\"to\":\"{newOwner}\", {encodedData} }}"
            propertyMessage = f"yield;{elementId};{data}" # Peut changer de syntaxe
            self.send_message(propertyMessage)
            realType = "Tiles" if elementType == "Tile" else "Resources"
            self.updateProperty(elementId,realType)

    def updateProperty(self, elementId,elementType):
        print("[NETWORKENGINE] Trying to update the following property : ", elementType,elementId)
        self.inventory[elementType].remove(elementId)
        pass

    # Fonction permettant vérifier si le joueur est propriétaire de l'entité
    # à lancer avant d'effectuer une modification
    def checkForProperty(self, elementId,elementPosition, elementType):
        if not self.isOwner(elementId):
            self.askForProperty(elementId, elementPosition,elementType)
        else:
            print("Already owner, so able to do modifications on")

    
    def ask_size (self):
        self.send_message(f"AskSize;;")

    def send_size (self,size):
        self.send_message(f"SizeIS;{self.name};{size}")
    
    def wait_size (self):
        try:
            data, addr = self.socket.recvfrom(1024)
            print("received message: %s" % data)
            message = data.decode('utf-8')
            action, id, data = message.split(";")
            if action == "SendSize":
                return MessageDecoder.ptuple_to_tuple(data)


        except BlockingIOError:
            pass

    def encodeGameObject(self,objType, objId, position, netName=None):
        if objType == "Tile":
            tile = self.gameEngine.map.grid[position[1]][position[0]]
            if tile.resource is None:
                print("Rien sur cette case, tuile", tile.x, tile.y)
            resEncodedString = f"\"resource\":{{\"type\":\"{tile.resource.type}\",\"amount\":{tile.resource.amount}}}" if not (tile.resource is None) else "\"resource\":\"None\""
            print("ResENc est alors : ",resEncodedString)
            unitEncodedString = "\"unit\":\"None\""
            if len(tile.unit) !=0:
                unitEncodedString = f"\"unit\":{{\"type\":\"{tile.unit[0].symbol}\",\"id\":\"{tile.unit[0].id},\"player\":\"{tile.unit[0].player.netName}\""
            encodedString = f"\"data\":{{\"type\":\"Tile\",{resEncodedString},{unitEncodedString},\"position\":\"{position}\"}}"
            return encodedString
        if objType == "Resource":
            res = self.gameEngine.map.grid[position[1]][position[0]]
            resEncodedString = f"{{\"resource\":{{\"type\":{res.type},\"amount\":{res.amount},\"position\":\"{position}\"}}}}"
            return resEncodedString
        else:
            print("Unknown Type asked")

    @staticmethod
    def decodeMessage(data,messageType="fget"):
        if messageType == "yield":
            dataDict = json.loads(data)
            print("DataDict is",dataDict)
            dataType = "Tiles" if dataDict["data"]["type"] == "Tile" else "Resources"
            return dataType,dataDict["to"],dataDict["data"]["type"]
        else:
            dataDict = json.loads(data)
            return dataDict["player"],dataDict["type"],dataDict["position"]

    def updateTileFromNetworkData(self, data):
        dataDict = json.loads(data)["data"]
        strPosition = MessageDecoder.ptuple_to_tuple(dataDict["position"])
        realPosition = (int(strPosition[0]), int(strPosition[1]))
        resource = None
        if dataDict["resource"] != "None":
            print("AMOUNT IS : ",dataDict["resource"]["amount"])
            self.gameEngine.createResource(dataDict["resource"]["type"],dataDict["resource"]["amount"],realPosition)
        if dataDict["unit"] != "None":
            formattedData = (realPosition[0], realPosition[1], dataDict["unit"]["player"])
            self.gameEngine.move_by_id(int(dataDict["unit"]["id"]),formattedData)

if __name__ == "__main__":
    print(tuple("(30.5,30.5)".split(",")))
    print(MessageDecoder.ptuple_to_tuple("(30.5,30.5)"))
    #create_message("SetUnit",id,(x,y,player,map))
    #create_message("SetUnit",3,(32,32,2))
    #Unit.spawn_unit(Villager,float(position[0]),float(position[1]),self.players[0],self.map)