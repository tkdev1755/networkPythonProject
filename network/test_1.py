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

    #pas thread non blockan

UDP_IP_NOT_ME = "192.168.128.254" #192.168.128.254
UDP_PORT = 5005
UDP_IP_ME = "192.168.128.250" #192.168.128.250


#MESSAGE = b"Hello, World!"
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP_ME,UDP_PORT))
sock.setblocking(0) #socket non bloquante

global compteur
compteur = 0
tab = [1,0,0,0]

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
    
# LANCEMENT PROGRAMME C

subprocess.run(["./network/networkEngine", "n"])
start = 0
while not(start) : 
    try:
            data, addr = sock.recvfrom(1024)
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

message = get_file_size('save')
sock.sendto(message,(UDP_IP_NOT_ME, UDP_PORT)) #cPort


# attendre de recevoir le GAME_STARTED

start = 0
while not(start) : 
    try:
            data, addr = sock.recvfrom(1024)
            print("received message: %s" % data)
            fun,ip,port = decoupe(data.decode('utf-8'))
            
            if fun == "START_GAME" :
                start = 1
                sock.sendto(bytes(f"GAME_STARTED;;",'utf-8'), (UDP_IP_NOT_ME,  UDP_PORT)) #cPort



    except BlockingIOError:
        pass


"""
while True :
    time.sleep(1)
    i = tab.index(1)
    deplacer(i)
    print(tab)
    sock.sendto(bytes(f"deplacer;{i}",'utf-8'), (UDP_IP_NOT_ME, UDP_PORT))

    try:
        data, addr = sock.recvfrom(1024)
        print("received message: %s" % data)
        fun,val = decoupe(data.decode('utf-8'))
        
        if fun == "ajouter" and val.isdigit():
            ajouter(int(val))


    except BlockingIOError:
        pass
    print(compteur)
    

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)


"""