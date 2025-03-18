import socket
import time
import pickle
import os
import subprocess

"""
print("Créer une partie 'c' ou  rejoindre une partie 'r' \n")
corj = input()

if corj == 'r' :
    print("Entrée une adresse IP à join\n")
    ip = input()
    print("Entrée un port \n")
    port = input()

else :
    print("Entrée un port \n")
    port = input()




"""

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
"""
try:
    subprocess.run(["./network/networkEngine", "j"], check=True)
except FileNotFoundError:
    print("Erreur : 'networkEngine' introuvable.")
except subprocess.CalledProcessError as e:
    print(f"Erreur lors de l'exécution de 'networkEngine' : {e}")
"""
request = 0
while not(request) :
    UDP_IP_ETAN = input("Entrez l'IP du créateur de la partie:")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP_MAX,UDP_PORT))
    sock.setblocking(0) #socket non bloquante

    try:
        #sock.sendto(b"coucou", (UDP_IP_ETAN, UDP_PORT))
        sock.sendto(bytes(f"CONNECT;{UDP_IP_MAX};{UDP_PORT}",'utf-8'), (UDP_IP_ETAN, UDP_PORT))
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
while not(receive) : 
    try:
            data,addr = sock.recvfrom(1024)
            message = pickle.loads(data)
            print("received message: %s" % message)
            if message:
                receive = 1

            sock.sendto(bytes(f"START_GAME;;",'utf-8'), (UDP_IP_ETAN, UDP_PORT))

    except BlockingIOError:
        pass

#ATTENDRE LE GAME_STARTED

start = 0
while not(start) : 
    try:
            data, addr = sock.recvfrom(1024)
            print("received message: %s" % data)
            fun,ip,port = decoupe(data.decode('utf-8'))
            
            if fun == "GAME_STARTED" :
                start = 1
                print("Game started!! apatsu apatsu")

    except BlockingIOError:
        pass


count=0
while True:
    sock.sendto(b"ajouter;1", (UDP_IP_ETAN, UDP_PORT))

    try:
        '''data, addr = sock.recvfrom(1024)
        print("received message: %s" % data)
        fun,val = decoupe(data.decode('utf-8'))
        
        if fun == "deplacer" and val.isdigit():
            deplacer(int(val))'''

        data, addr = sock.recvfrom(1024)
        try:
            data = pickle.loads(data)
        except:
            pass
        print("Received message:", data)

        try:
            if data[0] == "deplacer":
                deplacer(int(data[1]))
        except IndexError:
            print("message not indexable")

    except BlockingIOError:
        pass

    print("count:",count,end=" ")
    print(message)
    count+=1
    time.sleep(1)
    

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)
