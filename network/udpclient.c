#include <sys/socket.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>

#define BUFFSIZE 100

void stop( char* msg ){
  printf("%s\n", msg);
  exit(EXIT_FAILURE);
}

void main(){
    int port = 8000, len, bytes;
    char *ip = "172.21.146.126";
    char buffer[BUFFSIZE];
    char message[] = "CONNECT; ; ";
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if(sockfd < 0){
        stop("Erreur lors de la création de la socket");
    }
    struct sockaddr_in sAddress, cAddress;
    bzero(&sAddress, sizeof(sAddress));
    sAddress.sin_family = AF_INET;
    sAddress.sin_port = htons(port);
    sAddress.sin_addr.s_addr = inet_addr(ip);
    strncpy(buffer, "PONG", 5);
    
    size_t buff_size = BUFFSIZE - 1;
    while (1){
        if(sendto(sockfd, message, sizeof(message), MSG_CONFIRM, (const struct sockaddr *)&sAddress, sizeof(sAddress)) < 0){
            close(sockfd);  
            stop("Erreur lors de l'envoi du message\n");
        }
        printf("Message sent !\n");
        if(bytes = recvfrom(sockfd, buffer, buff_size, 0, (struct sockaddr *) &cAddress, (socklen_t *)&len)<0){
            close(sockfd);  
            stop("Erreur lors de la reception du packet\n");
        }
        printf("%s\n", buffer);
        printf("Info emeteur\nIp : %s\n", inet_ntoa(sAddress.sin_addr));
        sleep(1);
    }
    close(sockfd);
}