#fonctions permettant l'interprétation de messages "Action;ID;Data"

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
            pass
            #self.gameEngine.send_world_size()
        else:
            print("Action inconnue pour le moment:",action)





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

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

    def send_message(self,message):
        try:
            self.socket.sendto(bytes(message, 'utf-8'), ("127.0.0.1", 5005))
        except BlockingIOError:
            pass

    def isOwner(self,id):
        status = False # TEMP - à venir ici condition vraie si on est bien propriétaire ou fausse si on ne l'est pas
        return status

    def askForProperty(self, id):
        pMessage = f"get;{id};{self.name}"
        self.send_message(pMessage)

    # À Voir si on doit céder la propriété immédiatement dès qu'elle est demandée
    # où envoyer un message "yield;id;{data}"
    def yieldProperty(self,elementId,newOwner):
        if self.isOwner(elementId):
            data = f"{newOwner}"
            propertyMessage = f"yield;{self.name};{data}" # Peut changer de syntaxe
            self.send_message(propertyMessage)
            self.updateProperty(elementId)

    def updateProperty(self, id):

        pass

    # Fonction permettant vérifier si le joueur est propriétaire de l'entité
    # à lancer avant d'effectuer une modification
    def checkForProperty(self, id):
        if not self.isOwner(id):
            self.askForProperty(id)
        else:
            print("Already owner, so able to do modifications on")

    
    def ask_size (self):
        self.send_message(f"AskSize;;")

    def send_size (self,size):
        self.send_message(f"SizeIS;{self.name};{size}")
    
    def wait_size (self,t):
        now = time.time()
        while now - t < 10 :
            try:
                data, addr = self.socket.recvfrom(1024)
                print("received message: %s" % data)
                message = message.decode('utf-8')
                action, id, data = message.split(";")
                if action == "SendSize":
                    return MessageDecoder.ptuple_to_tuple(data)


            except BlockingIOError:
                pass
        
        sys.exit()

if __name__ == "__main__":
    print(tuple("(30.5,30.5)".split(",")))
    print(MessageDecoder.ptuple_to_tuple("(30.5,30.5)"))
    #create_message("SetUnit",id,(x,y,player,map))
    #create_message("SetUnit",3,(32,32,2))
    #Unit.spawn_unit(Villager,float(position[0]),float(position[1]),self.players[0],self.map)