#include "includes/networking.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*udp Python -> C*/

int main() {
    struct sockaddr_in server_sa;
    int socketfd;
    socketfd = udpserver(&server_sa, LOCALHOSTPORT, LOCALHOSTIP);
    if (socketfd < 0) {
        stop("Échec de la création de socket UDP");
    }

    printf("UDP démarré. En attente de messages...\n");
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
    return 0;
}
