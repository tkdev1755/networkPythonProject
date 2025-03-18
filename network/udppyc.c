#include "includes/networking.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 5005


struct sockaddr_in server_sa;
int socketfd;

socketfd = udpserver(&server_sa, SERVER_PORT, SERVER_IP);
if (socketfd < 0) {
    stop("Échec de la création du serveur UDP");
}

memset(&servaddr, 0, sizeof(servaddr));
servaddr.sin_addr.s_addr = inet_addr(ADDR_IP);
servaddr.sin_family = AF_INET;
servaddr.sin_port = htons(SERVER_PORT);
socklen_t servlen = sizeof(servaddr);

if (bind(sock_fd, (const struct sockadrr_in *)&servaddr, &servlen) < 0) {
    perror("Erreur lors du bind");
    exit(EXIT_FAILURE);
}


printf("Serveur UDP démarré. En attente de messages...\n");


while (1) {
    struct sockaddr_in client_sa;
    socklen_t client_len = sizeof(client_sa);

    char buffer[BUFFER_SIZE + 1];
    int recvLen = recvfrom(socketfd, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&client_sa, &client_len);
    if (recvLen < 0) {
        perror("Erreur lors de la réception des données");
        continue;
    }

    buffer[recvLen] = '\0';
    printf("Message reçu de la partie Python: %s\n", buffer);
}
close(socketfd);
