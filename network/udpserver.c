#include "includes/networking.h"

int main(){
    fd_set readfds, writefds;
    int bytes_recu = 0, selectfd;
    char *ip = "127.0.0.1";
    char msg_to_send[BUFFER_SIZE + 1];
    char received_msg[BUFFER_SIZE + 1];
    socklen_t len;
    struct sockaddr_in server_sa, client_sa;
    struct timeval timeout;
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;

    bzero(&client_sa, sizeof(struct sockaddr_in));
    bzero(msg_to_send, BUFFER_SIZE + 1);
    bzero(received_msg, BUFFER_SIZE + 1);

    int udpserverfd = udpserver(&server_sa, 8000, ip);

    FD_ZERO(&readfds);
    FD_ZERO(&writefds);
    FD_SET(udpserverfd, &readfds);
    FD_SET(udpserverfd, &writefds);


    selectfd = select(udpserverfd + 1, &readfds, &writefds, NULL, &timeout);
    if (selectfd == -1) {
        perror("select");
        close(udpserverfd);
        exit(EXIT_FAILURE);
    } else if (selectfd) {
        if (FD_ISSET(udpserverfd, &readfds)) {
            printf("Données disponibles en lecture sur la socket.\n");
            // Ajoutez ici le code pour lire les données
        }
        if (FD_ISSET(udpserverfd, &writefds)) {
            printf("La socket est prête pour l'écriture.\n");
            // Ajoutez ici le code pour écrire des données
        }
    } else {
        printf("Aucune activité détectée dans les 5 secondes.\n");
    }




}