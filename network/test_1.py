import socket
import time

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

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
#MESSAGE = b"Hello, World!"
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP

tab = [1,0,0,0]

def deplacer(i): 
    if i+1 >3 :
        tab[i] = 0
        tab[0] = 1
    else :
        tab[i] = 0 
        tab[i+1]=1

while True :
    time.sleep(1)
    i = tab.index(1)
    deplacer(i)
    print(tab)
    
    
    sock.sendto(f"deplacer;{i}", (UDP_IP, UDP_PORT))
    

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)


