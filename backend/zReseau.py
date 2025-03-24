#fonctions permettant l'interprétation de messages "Action;ID;Data"
from pygame.display import update
import uuid
import time
import sys

#"Set;ID;Data" demande la modification de l'état de l'objet d'id ID

#il faut qu'on s'accorde sur le contenu de Data

def decoupe(string):
    return string.split(";")

def ptuple_to_tuple(ptuple): #passe une string "(a,..,z)" en tuple (a,..,z)
    return tuple(map(float,ptuple[1:-1].split(",")))

#fonction pour créer un message
def create_message(action, id, data):
    return str(action)+";"+str(id)+";"+str(data)

#fonction pour envoyer un message par réseau
def send_message(message,sock):
    try:
        sock.sendto(bytes(message,'utf-8'),("127.0.0.1", 5005))
    except BlockingIOError:
        pass

#fonction pour recevoir un message par réseau ?
def receive_message(): #peut être qu'il faudra mettre un argument pour l'ip ?
    pass

import socket

def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1",5006))
    sock.setblocking(0) #socket non bloquante
    return sock

if __name__ == "__main__":
    print(tuple("(30.5,30.5)".split(",")))
    print(ptuple_to_tuple("(30.5,30.5)"))
    #create_message("SetUnit",id,(x,y,player,map))
    #create_message("SetUnit",3,(32,32,2))
    #Unit.spawn_unit(Villager,float(position[0]),float(position[1]),self.players[0],self.map)

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

    def __init__(self,sendSocket, gameEngine=None, size  = None):
        self.socket = sendSocket
        self.gameEngine = gameEngine
        self.name = f"PL-{uuid.uuid1().hex[:10]}"
        self.size = size

    def isOwner(self,id):
        status = False # TEMP - à venir ici condition vraie si on est bien propriétaire ou fausse si on ne l'est pas
        return status

    def askForProperty(self, id):
        pMessage = f"get;{id};{self.name}"
        send_message(pMessage, self.socket)

    # À Voir si on doit céder la propriété immédiatement dès qu'elle est demandée
    # où envoyer un message "yield;id;{data}"
    def yieldProperty(self,id):
        if self.isOwner(id):
            data = ""
            propertyMessage = f"yield;{self.name};{data}" # Peut changer de syntaxe
            send_message(propertyMessage, self.socket)
            self.updateProperty(id)

    def updateProperty(self, id):

        pass

    # Fonction permettant vérifier si le joueur est propriétaire de l'entité
    # A lancer avant d'effectuer une modification
    def checkForProperty(self, id):
        if not self.isOwner(id):
            self.askForProperty(id)
        else:
            print("Already owner, so able to do modifications on")

    
    def ask_size (self):
        send_message(f"AskSize;;",self.socket)

    def send_size (self,size):
        send_message(f"SendSize;0;{size}",self.socket)
    
    def wait_size (self,t):
        now = time.time 
        while now - t < 10 :
            try:
                data, addr = self.socket.recvfrom(1024)
                print("received message: %s" % data)
                message = message.decode('utf-8')
                action, id, data = message.split(";")
                if action == "SendSize":
                    return ptuple_to_tuple(data)


            except BlockingIOError:
                pass
        
        sys.quit()

