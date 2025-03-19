import socket
import time
import pickle
import os
import subprocess
import utils
import asyncio
from utils import NetworkEngine
LOCALHOSTIP  = "127.0.0.1"
LOCALHOSTPORT = 5005

def intializeProgramSocket():
    print("NetworkEngine init START")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCALHOSTIP,LOCALHOSTPORT))
    sock.setblocking(True)
    print("Socket opened")
    return sock

def programHandshake(programSocket):
    print("Started Handshake")
    try: 
            data, addr = programSocket.recvfrom(20)
            print("ADDR IS ", addr)
            tempADDR = addr
            print(data)
            print("RECIEVED SOMETHING !")
            recievedData = data.decode('utf-8')
            command,id,port = decoupe(recievedData)
            if (command == "PROG_CONNECT_OK"):
                print("PROGINIT OK")
                try:
                    programSocket.sendto(bytes(f"OK_200; ; ",'utf-8'),addr)
                    print("Network init END")
                    print("ADDR IS ", tempADDR)
                    return addr
                except Exception as e :
                    print("ERREUR ?")
                    return -1
                    pass
    except BlockingIOError as e:
        print("Waiting to recieve DATA")
        pass
    except Exception as e:
        print("ERROR !! : ",e)
        
        
def ajouter(i):
    global compteur
    compteur = compteur + i 

def decoupe(string):
    return string.split(";")

def deplacer(i): 
    if i+1 >3 :
        tab[i] = 0
        tab[0] = 1
    else :
        tab[i] = 0 
        tab[i+1] = 1

def get_file_size(file_path):
    """Retourne la taille du fichier en octets."""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"Taille du fichier '{file_path}': {size} octets")
        return size
    else:
        print("Le fichier n'existe pas.")
        return None
    
##### BOUCLE INITIALISATION #####

print("Créer une partie 'n' ou  rejoindre une partie 'j' \n")

norj = input()
DEST_IP = "NONE"
DEST_PORT = -1
if norj == 'j' :
    print("Entrez une adresse IP à join\n")
    DEST_IP = input()
    print("Entrez un port \n")
    DEST_PORT = input()

else :
    print("Entrez un port \n")
    port = input()


programSocket = intializeProgramSocket()


networkEngine = NetworkEngine()

process = networkEngine.launch_c_program("./network/networkEngine",["j",f"{DEST_IP}", f"{DEST_PORT}"])

programADDR = programHandshake(programSocket)


print("Ended Program Handshake")
if programADDR == -1: 
    print("ERREUR lors de la récéption du message de la part du C")

##########################
## FIN INIT
##########################

    #pas thread non blockan

"""UDP_IP_NOT_ME = "192.168.128.250" #192.168.128.254
UDP_PORT = 5005
UDP_IP_ME = "192.168.128.254" #192.168.128.250"""


compteur = 0
tab = [1,0,0,0]


# LANCEMENT PROGRAMME C


try:
    data, addr = programSocket.recvfrom(1024)
    global cPort 
    cPort = addr[1]
    print("received message: %s" % data)
    print(addr)
    fun,ip,port = decoupe(data.decode('utf-8'))
    
    if fun == "CONNECT" :
        start = 1

except BlockingIOError:
    pass

# Envoie size tab au prog c

file = open('save','wb')
pickle.dump(tab,file)
file.close

file = open('save','rb')
"""
message = file.read(get_file_size('save'))
programSocket.sendto(message,(LOCALHOSTIP, cPort)) #cPort
"""

# Envoie taille save pickle
programSocket.sendto(bytes("ACCEPT; ; ",'utf-8'),(LOCALHOSTIP, cPort)) #cPort


# attendre de recevoir le GAME_STARTED

try:
    data, addr = programSocket.recvfrom(1024)
    print("received message: %s" % data)
    fun,ip,port = decoupe(data.decode('utf-8'))
                
    if fun == "START_GAME" :
        start = 1
        #programSocket.sendto(bytes(f"GAME_STARTED;;",'utf-8'), (LOCALHOSTIP,  cPort)) #cPort

    else :
        print("ERROR WHILE STARTING THE GAME")
        raise Exception ("Problème à l'allumage")
                

except BlockingIOError:
    pass


programSocket.setblocking(0)
while True :
    
    time.sleep(1)
    i = tab.index(1)
    deplacer(i)
    print(tab)
    programSocket.sendto(bytes(f"deplacer;{i}",'utf-8'), (LOCALHOSTIP, cPort))

    try:
        data, addr = programSocket.recvfrom(1024)
        print("received message: %s" % data)
        fun,val = decoupe(data.decode('utf-8'))
        
        if fun == "ajouter" and val.isdigit():
            ajouter(int(val))


    except BlockingIOError:
        pass
    print(compteur)
    
"""
if norj == n : 
    #envoie la map

else :
    #reçois la map 
    #construit le monde
"""