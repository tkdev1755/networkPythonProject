
import socket

LOCALHOSTIP  = "127.0.0.1"
LOCALHOSTPORT = 5005

print("NetworkEngine init START")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LOCALHOSTIP,LOCALHOSTPORT))
sock.setblocking(True)
print("Socket opened")




try: 
        data, addr = sock.recvfrom(40)
        print("ADDR IS ", addr)
        tempADDR = addr
        print("RECIEVED DATA")
        print(data.decode("utf-8"))
        sock.sendto(bytes("ACCEPT; ; ",'utf-8'),addr) #cPort

except:
        PRINT("ERRROR")
        



