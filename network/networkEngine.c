#include "includes/networking.h"
#define MAXLINE 2048



int clientMode(char* ip, int port){
    struct sockaddr_in *clientSocket;

    int fd = udpclient(clientSocket, port, ip);
    char* data = calloc(MAXLINE, sizeof(char));
    int rcvFromResult = 0;
    struct sockaddr_in cliAddr;
    socklen_t cliLen = 0;
    while (1){
        int rcvFromResult = recvfrom(fd, data,MAXLINE, MSG_DONTWAIT, (struct sockaddr*) &cliAddr, &cliLen);
        if (rcvFromResult > 0 || errno == EAGAIN){
            stop("Error while reading message");
        }
    }
    return 0;
}


int main(){
    return 0;
}