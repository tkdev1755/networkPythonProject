#fonctions permettant l'interprétation de messages "Action;ID;Data"

#"Set;ID;Data" demande la modification de l'état de l'objet d'id ID

#il faut qu'on s'accorde sur le contenu de Data







#fonction pour créer un message
def create_message(action, id, data):
    return str(action)+";"+str(id)+";"+str(data)

#fonction pour envoyer un message par réseau
def send_message(message,ip):
    pass

#fonction pour recevoir un message par réseau ?
def receive_message(): #peut être qu'il faudra mettre un argument pour l'ip ?
    pass

#fonction pour interpréter un message 
def interpret_message(message):
    action, id, data=message.split(";")
    if action=="Set":
        move_by_id(id, data)

#fonction pour déplacer un objet par son id, IL FAUDRA LA METTRE EN METHODE DE LA CLASSE GAME_ENGINE
def move_by_id(id,position): #juste, remplace la position de l'unité d'id id par position 
    for player in self.players: #cherche l'unité d'id id et s'arrête une fois trouvée
        for unit in player.units:
            if unit.id==id:
                unit.position=position
                return
