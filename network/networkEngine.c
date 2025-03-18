#include "includes/networking.h"
#define MAXLINE 2048


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
int sendToProgram(){
    return 0;
}


networkStruct initializeListenSocket(){
    networkStruct ntStruct;
    bzero(&(ntStruct.addr), sizeof(struct sockaddr_in));
    ntStruct.sockFd = 0;
    struct sockaddr_in server_sa;
    char *ip = getip("eth0");
    socklen_t len = sizeof(server_sa);
    bzero(&server_sa, sizeof(struct sockaddr_in));
    int udpserverfd = udpserver(&server_sa, SERVERPORT, ip);
    ntStruct.addr = server_sa;
    ntStruct.sockFd = udpserverfd;    
    return ntStruct;
}

networkStruct initializeProgramSocket(){
    networkStruct ntStruct;
    bzero(&(ntStruct.addr), sizeof(struct sockaddr_in));
    struct sockaddr_in program_sa; 
    socklen_t len = sizeof(program_sa);
    ntStruct.addr = program_sa;
    ntStruct.sockFd = udpclient(&program_sa,PROGRAM_PORT,PROGRAM_IP);
    return ntStruct;
}

int initializeProgramConnection(){
    // Insérer ici le code d'initialisation de la communication avec le programme python
    
}
int clientMode(char* ip, int port){
    struct sockaddr_in *clientSocket;

    int fd = udpclient(clientSocket, port, ip);
    char* data = calloc(MAXLINE, sizeof(char));
    int rcvFromResult = 0;
    struct sockaddr_in cliAddr;
    socklen_t cliLen = 0;
    while (1){
        int rcvFromResult = recvfrom(fd, data,MAXLINE, MSG_DONTWAIT, (struct sockaddr*) &cliAddr, &cliLen);
        if (rcvFromResult > 0 && errno == EAGAIN){
            sendToProgram();
        }
        else{
            stop("Error while reading message");
        }
    }
    return 0;
}


int main(int argc, char *argv[]){
    fd_set readfds;
    int bytes_recu = 0, selectfd;
    char *ip = getip("eth0"); //ip of my eth0 interface
    char msg_to_send[BUFFER_SIZE + 1];
    char received_msg[BUFFER_SIZE + 1];
    struct sockaddr_in server_sa, client_sa, localhost_sa;
    socklen_t len = sizeof(client_sa);
    struct timeval timeout;
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;

    bzero(&client_sa, sizeof(struct sockaddr_in));
    bzero(msg_to_send, BUFFER_SIZE + 1);
    bzero(received_msg, BUFFER_SIZE + 1);

    int udpserverfd = udpserver(&server_sa, 8000, ip);
    
    localhost_sa.sin_family = AF_INET;
    localhost_sa.sin_port = htons(5500);
    localhost_sa.sin_addr.s_addr = inet_addr("127.0.0.1");

    

    while (1){
        
        FD_ZERO(&readfds);
        FD_SET(udpserverfd, &readfds);
        
        selectfd = select(udpserverfd + 1, &readfds, NULL, NULL, &timeout);
        if (selectfd == -1) {
            close(udpserverfd);
            stop("Select error : ");
        } else if (selectfd) {
            if (FD_ISSET(udpserverfd, &readfds)) {
                if(bytes_recu = recvfrom(udpserverfd, received_msg, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *) &client_sa, sizeof(client_sa)) < 0 && errno != EAGAIN){
                    close(udpserverfd);
                    stop("Reception error : ");
                }else{
                    //if it is from the other server, send it to the other socket to send it to the python program
                    if (strcmp(inet_ntoa(client_sa.sin_addr), "127.0.0.1") != 0){
                        if ((sendto(udpserverfd, received_msg, bytes_recu, 0, (struct sockaddr *)&localhost_sa, sizeof(localhost_sa))) < 0) {
                            close(udpserverfd);
                            stop("Sending to python program failed : ");
                        }
                    }
                    else{
                        /*
                        We have to set the client sockaddr first, so we have to discuss how to get the other player ip adress and port to set it. Let do it this afternoon !
                        */
                        if ((sendto(udpserverfd, received_msg, bytes_recu, 0, (struct sockaddr *)&client_sa, sizeof(client_sa))) < 0) {
                            close(udpserverfd);
                            stop("Sending to the server failed : ");
                        }
                    }
                }
            }  
        }
    }

    // New initialization code
    if (argc > 3){
        // future gestion des arguments
    }

    networkStruct programSocket = initializeProgramSocket();
    networkStruct serverSocket = initializeListenSocket();
    int clientBytes = 0;
    int clientStatus = 0; // Représente si le client est en train de transmettre des bytes ou en train d'en recevoir, n'est pas utilisé pour le moment 
    int programBytes = 0;
    char* cliMSG[BUFFER_SIZE+1];
    char  programMSG[BUFFER_SIZE+1];
    while (1){
        //Attente d'une commande de la part d'un autre client;
        clientBytes = recvfrom(serverSocket.sockFd, cliMSG,BUFFER_SIZE-1,MSG_DONTWAIT,&client_sa,&len);
        programBytes = recvfrom(programSocket.sockFd, programMSG,BUFFER_SIZE-1,MSG_DONTWAIT,&programSocket.addr,&programSocket.addrLen);
        // Gestion de la reception d'une commande de la part d'une autre instance
        if (clientBytes < 0 && errno != EAGAIN){
            stop("error while recieving data from client");
        }
        else if (clientBytes > 0){
            clientStatus = 2; // indique que le client à écrit dans la socket
            programBytes = sendto(programSocket.sockFd, cliMSG, BUFFER_SIZE-1, MSG_DONTWAIT,&programSocket.addr, programSocket.addrLen);
            if (programBytes < 0 || errno != EAGAIN){
                stop("Error while sending data to python program");
            }
            if (programBytes > 0){
                bzero(cliMSG, BUFFER_SIZE+1);
                programBytes = 0;
            }
        }
        // Gestion de la réception de commandes de la part du programme python
        if (programBytes < 0 && errno != EAGAIN){
            stop("error while recieving data from program");
        }
        else if (programBytes > 0){
            clientBytes = sendto(serverSocket.sockFd, programMSG, BUFFER_SIZE-1, MSG_DONTWAIT,&client_sa, len);
            clientStatus = 1;
            if (clientBytes < 0 || errno != EAGAIN){
                stop("Error while sending data to instance");
            }
            if (clientBytes > 0){
                clientBytes = 0;
            }
        }
    }
    return EXIT_SUCCESS;
}