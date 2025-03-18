#include "networking.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PYTHON_IP "127.0.0.1"
#define PYTHON_PORT 5005

struct sockaddr_in python_sa;
int socketfd;

socketfd = udpclient(&python_sa, PYTHON_PORT, PYTHON_IP);
if (socketfd < 0) {
    stop("Échec de la création du client UDP");
}

printf("Client UDP démarré. Préparation à envoyer un message...\n");

char message[BUFFER_SIZE] = "unit_move|playerA|10,20";  // Exemple d'événement réseau

socklen_t python_len = sizeof(python_sa);
int sentLen = sendto(socketfd, message, strlen(message), 0, (struct sockaddr *)&python_sa, python_len);
if (sentLen < 0) {
    perror("Erreur lors de l'envoi des données");
    close(socketfd);
    exit(EXIT_FAILURE);
}

printf("Message envoyé à la partie Python: %s\n", message);
close(socketfd);
