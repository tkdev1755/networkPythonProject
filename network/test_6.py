import socket 
import time

mat = [1,0,0,0]
count = len(mat)

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.setblocking(0) #socket non bloquante

sock.bind((UDP_IP,UDP_PORT))

while True:

    if count:
        mat=[0,0,0,0]
        count-=1
        mat[count]=1
    else:
        count=len(mat)-1
        mat=[0,0,0,1]

    try:
        data, addr = sock.recvfrom(1024)
        print("received message: %s" % data)
    except BlockingIOError:
        pass

    print(mat)
    time.sleep(1)