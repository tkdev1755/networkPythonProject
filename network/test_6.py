import socket 
import time

tab=[1,0,0,0]

def deplacer(i):
    global tab
    tab=[0,0,0,0]
    tab[i]=1

def decoupe(string):
    return string.split(";")

count=0

UDP_IP = "192.168.128.254"
UDP_PORT = 5005

IP_ETAN = "192.168.128.250"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.setblocking(0) #socket non bloquante

sock.bind((UDP_IP,UDP_PORT))

while True:
    sock.sendto(b"ajouter;1", (IP_ETAN, UDP_PORT))

    try:
        data, addr = sock.recvfrom(1024)
        print("received message: %s" % data)
        fun,val = decoupe(data.decode('utf-8'))
        
        if fun == "deplacer" and val.isdigit():
            deplacer(int(val))

    except BlockingIOError:
        pass

    print("count:",count,end=" ")
    count+=1
    print(tab)
    time.sleep(1)