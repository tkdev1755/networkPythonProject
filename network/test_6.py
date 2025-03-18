import socket 
import time
import pickle

tab=[1,0,0,0]

def deplacer(i):
    global tab
    tab=[0,0,0,0]
    tab[i]=1

def decoupe(string):
    return string.split(";")

count=0

UDP_IP = "192.168.128.254" #ip de moi
UDP_PORT = 5005

IP_ETAN = "192.168.128.250" #ip de etan

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.setblocking(0) #socket non bloquante
sock.bind((UDP_IP,UDP_PORT))

while True:
    sock.sendto(b"ajouter;1", (IP_ETAN, UDP_PORT))

    try:
        '''data, addr = sock.recvfrom(1024)
        print("received message: %s" % data)
        fun,val = decoupe(data.decode('utf-8'))
        
        if fun == "deplacer" and val.isdigit():
            deplacer(int(val))'''

        data, addr = sock.recvfrom(1024)
        received_data = pickle.loads(data)
        print("Received message:", received_data)

        if received_data[0] == "deplacer":
            deplacer(int(received_data[1]))

    except BlockingIOError:
        pass

    print("count:",count,end=" ")
    count+=1
    print(tab)
    time.sleep(1)