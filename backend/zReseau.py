#fonctions permettant d'interpréter des messages "Action;ID;Data" et de modifier le monde
#les messages sont de trois formes;
#"Set;ID;Data" modifie les datas de l'élément d'id ID
#"Get;ID" réclame les datas de l'élément d'id ID
#"Take;ID" réclame la propriété de l'élément d'id ID
#les dates seront de la forme je ne sais pas






#fonction pour créer un message
def create_message(action, ID, data):
    pass #faire les strings
    return action+";"+ID+";"+data

#fonction pour envoyer un message
def send_message(message):
    pass #partie réseau pour envoyer