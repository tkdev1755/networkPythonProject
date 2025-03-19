#je veux faire des fonctions qui traduisent des messages de la forme "Action;ID;Data"
#Les messages sont de trois natures: 
#"Get;ID;" pour demander les informations d'un élément dont nous ne somme pas propriétaire
#"Set;ID;Data" la réponse du propriétaire, qui envoie les informations
#"Take;ID;" pour indiquer la prise de possession d'un élément
#Data est une chaine de caractères,
#je pense qu'elle contient toutes les infos de l'élément?

def interpret_message(message):
    message = message.split(";")
    print(message)
    action = message[0]
    ID = message[1]
    data = message[2]
    #On regarde l'action
    if action == "Get": #On nous demande des informations
        pass
    elif action == "Set": #On a reçu des informations
        pass
    elif action == "Take": #On nous indique la prise de possession d'un élément
        pass
    else: #erreur action inconnue
        pass

def create_get(action, ID, data): #quand on demande l'état d'un élément
    pass

def create_set(action, ID, data): #quand on envoie l'état d'un élément
    pass

def create_take(action, ID, data): #quand on indique une prise de possession d'un élément
    pass

def send_message(message, address):
    #fonction réseau qui permet l'envoi du message à l'autre
    pass


interpret_message("Get;ID;Data")
