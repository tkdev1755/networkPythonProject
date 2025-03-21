from backend.Players import Player

playerA = Player("joueurA", "Means", None, 1, "blue") #modifiable
entities = {} #un dict avec toute les entités du playerA
for i in range(len(playerA.buildings)):
    entities[f"{playerA.buildings[i].symbol}{i}"] = playerA.buildings[i]
#for i in range(len(player1.buildings) + len(player1.units)):
 #   entities[player1.units[i].position] = []
for i in range(len(playerA.units)):
    entities[f"{playerA.units[i].symbol}{i}"] =playerA.units[i]
print(entities)
def process_packet(packet):
    try:
        parts = packet.split(';')
        if len(parts) != 3:
            raise ValueError("Format du paquet incorrect. Attendu : 'action;paramètres;id'.")
        
        function_name, parameters_str, entity_id = parts
        function_name = function_name.strip()
        parameters_str = parameters_str.strip()
        entity_id = entity_id.strip()
        
        parameters = parameters_str.split()
        print(f"Traitement du paquet : Fonction={function_name}, Paramètres={parameters}, ID={entity_id}")

        if entity_id not in entities:
            raise ValueError(f"L'entité avec l'ID \"{entity_id}\" n'existe pas.")
        
        entity = entities[entity_id]
        
        if not hasattr(entity, function_name):
            raise ValueError(f"La fonction '{function_name}' n'existe pas pour l'entité '{entity_id}'.")
        function_method = getattr(entity, function_name)
        function_method(*parameters)
        

    except ValueError as ve:
        print(f"Erreur de traitement du paquet : {ve}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")



def generate_packet(Action, entity_id, *parameters):
    packet = f"{Action};{' '.join(parameters)};{entity_id}"
    return packet

