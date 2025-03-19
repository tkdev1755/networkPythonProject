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
            print("RECIEVED SOMETHING !")
            if (data == "PROG_CONNECT_OK; ; "):
                try:
                    programSocket.sendto(bytes(f"OK_200; ; ",'utf-8'),(addr[0],addr[1]))
                    print("Network init END")
                    print(addr)
                    return addr
                except Exception as e :
                    print("ERREUR ?")
                    return -1
                    pass
    except BlockingIOError as e:
        print("Waiting to recieve DATA")
        pass
        



##### BOUCLE INITIALISATION #####

print("Créer une partie 'n' ou  rejoindre une partie 'j' \n")

corj = input()
DEST_IP = "NONE"
DEST_PORT = -1
if corj == 'j' :
    print("Entrez une adresse IP à join\n")
    DEST_IP = input()
    print("Entrez un port \n")
    DEST_PORT = input()

else :
    print("Entrez un port \n")
    port = input()


programSocket = intializeProgramSocket()



networkEngine = NetworkEngine()
process = networkEngine.launch_c_program("./networkEngine",["j",f"{DEST_IP}", f"{DEST_PORT}"])

programADDR = programHandshake(programSocket)


print("Ended Program Handshake")
if programADDR == -1 or programADDR == None:
    print("ERREUR lors de la récéption du message de la part du C")
##### FIN BOUCLE INITIALISATION #####



UDP_IP_MAX = "192.168.128.250" #192.168.128.254
UDP_PORT = 5005
UDP_IP_ETAN = "192.168.128.250" #192.168.128.250




#MESSAGE = b"Hello, World!"

global compteur
compteur = 0

def ajouter(i):
    global compteur
    compteur = compteur + i 

def decoupe(string):
    return string.split(";")

def deplacer(i): 
    global message
    if i+1 >3 :
        message[i] = 0
        message[0] = 1
    else :
        message[i] = 0 
        message[i+1] = 1

def get_file_size(file_path):
    """Retourne la taille du fichier en octets."""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        #print(f"Taille du fichier '{file_path}': {size} octets")
        return size
    else:
        print("Le fichier n'existe pas.")
        return None
    
# ENVOI DE LA REQUETE DE CONNEXION AU CREATEUR DE LA PARTIE


request = 0
while not(request) :
    try:
        #sock.sendto(b"coucou", (UDP_IP_ETAN, UDP_PORT))
        programSocket.sendto(bytes(f"CONNECT; ; ",'utf-8'), programADDR)
        request = 1
    except BlockingIOError:
        pass

    '''
    try:
            data, addr = sock.recvfrom(1024)
            print("received message: %s" % data)
            fun,ip,port = decoupe(data.decode('utf-8'))
            if fun == "CONNECT" :
                start = 1
    except BlockingIOError:
        pass'''
    
# RECEVOIR LE FICHIER CONTENANT LE MONDE

receive = 0
message = ""
try:
    data,addr = programSocket.recvfrom(9)
    print("received message: %s" % message)
    if message == "PLAY ; ; " :

        try:
            with open("save", "wb") as f:
                pickle.load(data, f)
        except Exception as e:
            print("ERROR while trying to open/load pickle file", e)
            receive = -1
        receive = 1
    programSocket.sendto(bytes(f"START_GAME; ; ",'utf-8'), (UDP_IP_ETAN, UDP_PORT))
except BlockingIOError:
    pass

if receive == -1:
    raise Exception("RECIEVE FAILED")

#ATTENDRE LE GAME_STARTED

start = 0
try:
        data, addr = programSocket.recvfrom(1024)
        print("received message: %s" % data)
        fun,ip,port = decoupe(data.decode('utf-8'))

        if fun == "GAME_STARTED" :
            start = 1
            print("Game started!! apatsu apatsu")

except BlockingIOError:
    pass


count=0
while True:
    programSocket.sendto(b"ajouter;1", programADDR)

    try:
        '''data, addr = sock.recvfrom(1024)
        print("received message: %s" % data)
        '''

        data, addr = programSocket.recvfrom(1024)
        fun,val = decoupe(data.decode('utf-8'))
        
        if fun == "deplacer" and val.isdigit():
            deplacer(int(val))
    except BlockingIOError:
        pass

    print("count:",count,end=" ")
    print(message)
    count+=1
    time.sleep(1)
    

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)
