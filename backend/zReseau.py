#fonctions permettant l'interprétation de messages "Action;ID;Data"

#"Set;ID;Data" demande la modification de l'état de l'objet d'id ID

#il faut qu'on s'accorde sur le contenu de Data







#fonction pour créer un message
def create_message(action, id, data):
    return str(action)+";"+str(id)+";"+str(data)

#fonction pour envoyer un message par réseau
def send_message(message,ip):
    pass

#fonction pour interpréter un message
def interpret_message(message):
    action, id, data=message.split(";")
    if action=="Set":
        move_by_id(id, data)

def move_by_id(id,data):

