#include "includes/networking.h"
#include <fcntl.h>


/*
    LOG MODIFICATIONS : 
    18/03/2025@tahakhetib - Merged amadou's code from udpserver.c to networkEngine.c
                          - Added some functions to make the code more readable
                                initalizeClientConnection : intialize the connection with the client if there is one;
                                initialize
                          - Added programRead functionnality
*/


/*
    Plan de démarrage du programme
    ** Ce plan de démarrage prends en compte que 2 instances du jeu pour le moment **
        Démarrage du programme python d'abord, demande si on veut démarrer une partie multijoueurs, solo, ou rejoindre une partie multijoueurs

        Si démarrer une partie multijoueurs -> 
            Avant tout, Démarrage du canal de communication au niveau du programme python
            Lancement du programme c avec un argument -n (Indique au programme de démarrer en mode écoute pour attendre une partie)
            Au démarrage du programme C, avant toute chose, établissement de la connexion avec le programme principal
            Ensuite lancement du initializeServer();
            Si réception d'une string "CONNECT; IP_ADDR; PORT" -> Début du "handshake", avec envoi du monde complet, transmission de la commande au programme python, qui lui engage l'envoi de la séquence de bits .pkl au networkEngine;
            Une fois la réception des bits du fichier .pkl par le networkEngine, début de l'envoi
            --Attente de l'envoi--
            Si envoi réussi -> réception d'une STRING "START_GAME;IP_ADDR;PORT" de la part de l'instance ayant rejoint la partie
            Sinon -> Si TIMEOUT -> Arrêt de la connexion ; Sinon si "ERROR_CODE;TRACE;..." -> Retente d'envoyer/Gestion erreur
            --Envoi terminé, envoi réussi---
            Transmission du message au programme python qui lance la partie et envoie le message "GAME_STARTED;SERVER_IP;PORT"
            Fin du démarrage d'une partie

        Si rejoindre une partie multijoueur ->
            Avant tout, Démarrage du canal de communication au niveau du programme python
            Lancement du programme c avec les argument -r IP PORT (Indique au programme de se connecter à IP sur le port PORT)
            Au démarrage du programme C, avant toute chose, établissement de la connexion avec le programme principal
            Ensuite lancement du initializeClientConnectionIP(char* ip,port);
            Envoi du "CONNECT; IP_ADDR; PORT" où IP_ADDR est l'ip de l'instance envoyant la string et PORT son port
            --Attente de la réception des données sur le monde--
            Si réception finie -> Transmission du monde au programme python; Si deserialisation réussie -> Envoi de la commande "START_GAME;IP_ADDR;PORT" au créateur de la partie; Sinon envoyer "ERROR_CODE;TRACE;..." au créateur de la partie
            Sinon si TIMEOUT -> Arrêt de la connexion et envoi de l'erreur "ERROR_CODE;TRACE;" au programme python; Sinon envoyer "ERROR_CODE;TRACE;"
            --Fin de récepetion des données sur le monde, réception réussie--
            A la réception de la commande "GAME_STARTED;SERVER_IP;PORT", transmission au programme python et lancement de la boucle de jeu;
            Fin du démarrage de la partie
        
        Si nouvelle partie classique ->
            Lancement d'une partie classique comme avant,sans faire appel au networkEngine


    ?? Questions pour plus tard ??
        Si nous avons plus d'une instance voulant rejoindre le jeu, devons-nous lancer la partie et accepter les arrivées de nouveau joueurs à la volée, ou faire un mode "attente" pour connecter tout les clients puis lancer la partie ?

*/




int main(int argc, char *argv[]){
    write(1,"[NetworkEngine] Starting Network Engine \n",42);
    //char *ip = getip("eth0"); //ip of my eth0 interface
    struct sockaddr_in client_sa, localhost_sa;
    //socklen_t len = sizeof(client_sa);
    int clientBytes = 0;
    // int clientStatus = 0; // Représente si le client est en train de transmettre des bytes ou en train d'en recevoir, n'est pas utilisé pour le moment
    int programBytes = 0;
    char cliMSG[BUFFER_SIZE+1];
    char programMSG[BUFFER_SIZE+1];
    networkStruct serverSocket;
    networkStruct programSocket = initializeProgramSocket();
    write(1,"[NetworkEngine] Ended Program socket init, starting handshake with PythonProgram\n ",83);
    // initializeProgramConnection(programSocket);
    if (argc < 2) {
        printf("Usage: %s <options>\n", argv[0]);
        return 1;
    }

    char *option = argv[1];

    switch (option[0]) {
        case 'n':
            // printf("Option n sélectionnée\n");
            serverSocket = createGame(&client_sa, &len, &programSocket);
            break;
        case 'j':
            // printf("Option j sélectionnée\n");
            serverSocket = join_game("192.168.167.111", 8000);
            break;
        default:
            printf("Option inconnue : %s\n", option);
            break;
        }
    }

    while (1)
    {
        // Attente d'une commande de la part d'un autre client;
        clientBytes = recvfrom(serverSocket.sockFd, cliMSG, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *)&client_sa, &len);

        // Gestion de la reception d'une commande de la part d'une autre instance
        if (clientBytes < 0 && errno != EAGAIN)
        {
            stop("error while recieving data from client");
        }
        else if (clientBytes > 0)
        {
            // clientStatus = 2; // indique que le client à écrit dans la socket
            // programBytes = ;
            if (sendto(programSocket.sockFd, cliMSG, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *)&programSocket.sock_addr, programSocket.addrLen) < 0)
            {
                stop("Error while sending data to python program");
            }
            bzero(cliMSG, BUFFER_SIZE + 1);
        }
        // Gestion de la réception de commandes de la part du programme python
        programBytes = recvfrom(programSocket.sockFd, programMSG, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *)&programSocket.sock_addr, &programSocket.addrLen);
        if (programBytes < 0 && errno != EAGAIN)
        {
            stop("error while recieving data from program");
        }
        else
        {
            // clientStatus = 1;
            if (sendto(serverSocket.sockFd, programMSG, BUFFER_SIZE - 1, 0, (struct sockaddr *)&client_sa, len) < 0)
            {
                stop("Error while sending data to instance");
            }
            bzero(programMSG, BUFFER_SIZE + 1);
        }
    }
    
    return EXIT_SUCCESS;
}