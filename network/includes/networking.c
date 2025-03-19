#include "networking.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

int stdoutFD = 1;
void stop( char* msg ){
  perror(msg);
  exit(EXIT_FAILURE);
}

<<<<<<< HEAD
int changeSTDOut(char* filename){
    return stdoutFD;
=======
void changeSTDOut(char* filename){
    stdoutFD = open(filename,O_APPEND);
>>>>>>> 76812d3 ([WORKING] Fixing Bugs)
}

void closeAll(int *tab, int number_of_socket){
    for(int i = 0; i < number_of_socket; i++){
        close(tab[i]);
    }
}




int udpclient(struct sockaddr_in *server_sa, int port, char * ip){
    int socketfd = socket(AF_INET, SOCK_DGRAM, 0);
    if(socketfd < 0){
        stop("Socket creation failed !");
    }

    if(ip == NULL){
        stop("IP adress is null !");
    }

    bzero(server_sa, sizeof(struct sockaddr_in));
    server_sa->sin_family = AF_INET;
    server_sa->sin_port = htons(port);
    server_sa->sin_addr.s_addr = inet_addr(ip);

    return socketfd;
}

int udpserver(struct sockaddr_in *server_sa, int port, char * ip){
    int socketfd = socket(AF_INET, SOCK_DGRAM, 0);
    if(socketfd < 0){
        stop("Socket creation failed !");
    }

    if(ip == NULL){
        stop("IP adress is null !");
    }

    bzero(server_sa, sizeof(struct sockaddr_in));
    server_sa->sin_family = AF_INET;
    server_sa->sin_port = htons(port);
    server_sa->sin_addr.s_addr = inet_addr(ip);

    if(bind(socketfd, (struct sockaddr *)server_sa, sizeof(struct sockaddr)) < 0){
        close(socketfd);
        stop("Binding failed !");
    }
    
    return socketfd;
}

char * getip(const char * interface){
    struct ifaddrs *ifaddr, *ifa;
    static char ip[INET_ADDRSTRLEN];

    // gathering @ip
    if (getifaddrs(&ifaddr) == -1) {
        perror("getifaddrs");
        return NULL;
    }
    
    // browse all interfaces
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL) continue;

        if (ifa->ifa_addr->sa_family == AF_INET && strcmp(ifa->ifa_name, interface) == 0) {
            struct sockaddr_in *sa = (struct sockaddr_in *)ifa->ifa_addr;
            inet_ntop(AF_INET, &(sa->sin_addr), ip, INET_ADDRSTRLEN);
            freeifaddrs(ifaddr);
            return ip;
        }
    }

    freeifaddrs(ifaddr);
    return NULL;  // interface not found
}

networkStruct join_game(char * game_ip, unsigned int game_port){

    /*
     Attention : tout ajout dans cette fonction doit être accompagné de commentaire
     Me demander de faire tout gros changement à effectuer sur le code existant !
     Merci !
    */

    networkStruct joinning_struct = initializeListenSocket();
    struct sockaddr_in sock_to_send_srv, sock_localhost, client_sa;
    int received_bytes = 0;
    char received_msg[BUFFER_SIZE + 1];
    char * msg_to_send = "CONNECT; ; ";
    FILE * file = fopen("save", "wb");
    // printf("%s\n", joinning_struct.);

    bzero(&sock_to_send_srv, sizeof(struct sockaddr_in));
    bzero(&sock_localhost, sizeof(struct sockaddr_in));
    bzero(received_msg, BUFFER_SIZE + 1);

    sock_to_send_srv.sin_family = AF_INET;
    sock_to_send_srv.sin_port = htons(game_port);
    sock_to_send_srv.sin_addr.s_addr = inet_addr(game_ip);
    
    // sock_localhost.sin_family = AF_INET;
    // sock_localhost.sin_addr.s_addr = inet_addr(LOCALHOSTIP);
    // sock_localhost.sin_port = LOCALHOSTPORT;
    socklen_t len;


    if((received_bytes = recvfrom(joinning_struct.sockFd, received_msg, BUFFER_SIZE, 0, (struct sockaddr *) &sock_localhost, &len))<0){
        close(joinning_struct.sockFd);
        fclose(file);
        stop("Erreur lors de la reception du packet\n");
    }
    // printf("Info emeteur\nIp : %s\n", inet_ntoa(sock_localhost.sin_addr));

    // if(sendto(joinning_struct.sockFd, received_msg, received_bytes, 0, (struct sockaddr *) &sock_to_send_srv, sizeof(sock_to_send_srv)) < 0){
    if(sendto(joinning_struct.sockFd, received_msg, received_bytes, 0, (struct sockaddr *) &sock_to_send_srv, sizeof(sock_to_send_srv)) < 0){
        close(joinning_struct.sockFd);
        fclose(file);
        stop("Joinning the game failed : ");
    }
    printf("%s\n", received_msg);
    printf("Message sent too !\n");
    bzero(received_msg, received_bytes);
    // exit(0);

    // --- PARTIE TEMPORAIRE POUR SIMULER LA DESERIALIZATION REUSSIE---
    int ACK_OK = 0; // Variable temporaire simulant la copie réussie d'un fichier
    received_bytes = recvfrom(joinning_struct.sockFd, received_msg, BUFFER_SIZE, 0, (struct sockaddr *) &joinning_struct.sock_addr, &joinning_struct.addrLen);
    if (!strncmp("OK; ; ",received_msg, 7)){
        write(stdoutFD, "RECIEVED ACK SUCCESFULLY \n",27);
        ACK_OK = 1;
    }
    
    // PARTIE CHARGEMENT FICHIER PICKLE 
    /*while (ACK_OK == 0 ){
        write(stdoutFD, received_msg, received_bytes);
        
        /*if(fwrite(received_msg, sizeof(char), received_bytes, file) < 0){
            fclose(file);
            close(joinning_struct.sockFd);
            stop("Receiving the game failed : ");
        }/
    }*/

    write(stdoutFD, "SENDING ACK TO PYTHON \n",24);
    // J'envoie la commande "OK ; ; " au programme python (temporaire en attendant de remettre la sérialisation JSON/Pickle sur pied)
    int sent_bytes = sendto(joinning_struct.sockFd, received_msg, 7, 0, (struct sockaddr *) &sock_localhost, sizeof(sock_localhost));
    if (sent_bytes < 0){
        stop("Error while trying to send OK COMMAND to Python program :");
    }
    write(stdoutFD, "SENT ACK TO PYTHON \n",21);
    // Ici j'ai changé la définition car, c'est pas au C d'envoyer au programme python local qu'il faut démarrer la partie mais c'est l'inverse
    // Donc tout d'abord, j'attends de recevoir le message START_GAME du Programme python local, et ensuite je l'envoie à l'autre machine
    // --- FIN PARTIE TEMPORAIRE POUR SIMULER LA DESERIALIZATION REUSSIE---

    
    received_bytes = recvfrom(joinning_struct.sockFd, received_msg, BUFFER_SIZE, 0, (struct sockaddr *) &sock_localhost, &len);
    write(stdoutFD, "RECIEVED COMMAND FROM PYTHON\n",21);
    if (received_bytes < 0){
        stop("Error while trying to get data from python program");
    }
    else{
        // Si je reçois START_GAME de la part du python, j'envoie la commande à l'autre machine
        if (!strncmp("START_GAME; ; ",received_msg,15)){
            write(stdoutFD, "Recieved START_GAME Command \n",30);
            if(sendto(joinning_struct.sockFd, "START_GAME; ; ", 9, 0, (struct sockaddr *) &joinning_struct.sock_addr, joinning_struct.addrLen) < 0){
                fclose(file);
                close(joinning_struct.sockFd);
                stop("Informing to start the game failed : ");
            }
        }
    }

    return joinning_struct;
}

networkStruct initializeListenSocket(){
    networkStruct ntStruct;
    bzero(&(ntStruct.sock_addr), sizeof(struct sockaddr_in));
    struct sockaddr_in server_sa;
    printf("IP : %s\n", getip(INTERFACE));
    int udpserverfd = udpserver(&server_sa, SERVERPORT, getip(INTERFACE));

    ntStruct.addrLen = sizeof(server_sa);
    ntStruct.sock_addr = server_sa;
    ntStruct.sockFd = udpserverfd;  
      
    return ntStruct;
}

networkStruct initializeProgramSocket(){
    write(1,"Initializing Program socket\n",29);
    networkStruct ntStruct;
    bzero(&(ntStruct.sock_addr), sizeof(struct sockaddr_in));
    struct sockaddr_in program_sa; 
    ntStruct.addrLen = sizeof(program_sa);
    ntStruct.sock_addr = program_sa;
    ntStruct.sockFd = udpclient(&ntStruct.sock_addr, LOCALHOSTPORT, LOCALHOSTIP);
    write(1,"Finished initializing program socket \n",39);
    return ntStruct;
}

int initializeProgramConnection(networkStruct programSocket){
    write(1,"Began Program Connection\n", 26);
    char* connectRequest = "PROG_CONNECT_OK; ; ";
    int sentBytes = sendto(programSocket.sockFd,connectRequest,20, 0, (struct sockaddr *) &programSocket.sock_addr, programSocket.addrLen);
    if (sentBytes < 0){
        stop("Error while initializing program");
    }
    write(1,"Sent conn request\n", 19);
    bzero(connectRequest, BUFFER_SIZE+1);
    int recievedBytes = recvfrom(programSocket.sockFd, connectRequest,BUFFER_SIZE,0, (struct sockaddr *)&programSocket.sock_addr, &programSocket.addrLen);
    if (recievedBytes < 0){
        stop("Error while getting ACK");
    }    
    else{
        write(1,"Sent conn request\n", 19);
        printf("Successfully initialized Program connection");
    }
    return 0;
}

networkStruct createGame(struct sockaddr_in* cliAddr, int* len, networkStruct* programSocket){
    int CONNECTION_REQUEST = 0;
    int START_GAME = 0;
    networkStruct listenPort = initializeListenSocket();
    int bytesRead= 0;
    int bytesSend = 0;
    char instanceData[BUFFER_SIZE+1];

    bzero(instanceData, BUFFER_SIZE+1);
    
    while (CONNECTION_REQUEST == 0){
        bytesRead = recvfrom(listenPort.sockFd,instanceData,MSG_DONTWAIT, BUFFER_SIZE, (struct sockaddr*) cliAddr, len);
        if (bytesRead < 0 && errno != EAGAIN){
            write(stdoutFD,"Error while recieving data from instance",41);
            stop("Error while recieving data from instance");
        }
        else {
            if (bytesRead > 0 && !strncmp("CONNECT",instanceData,7)){
                write(stdoutFD,"Recieved Connection request\n",29);
                CONNECTION_REQUEST = 1;
            }
            else{
                write(stdoutFD,"Shouldn't get this command",27);
            }
        }
    }
    write(stdoutFD,"GOT OUT OF LOOP\n",17);
    // Deuxième partie de la connexion - Lecture du fichier .pkl et Envoi du monde à la deuxième instance
    // Envoi de la commande au programme python
    int sentData = sendto(programSocket->sockFd,instanceData, bytesRead, 0, (struct sockaddr*) &programSocket->sock_addr,programSocket->addrLen);
    if (sentData < 0){
        write(stdoutFD,"Error while sending command to program\n", 37);
        stop("Error while sending command to program");
    }
    write(stdoutFD,"Sent data to server\n",21);

    bzero(instanceData,BUFFER_SIZE+1);

    bytesRead = recvfrom(programSocket->sockFd, instanceData, BUFFER_SIZE, 0, (struct sockaddr*) &programSocket->sock_addr, &programSocket->addrLen);
    write(stdoutFD,"Recieved command from program \n",29);
    if (bytesRead < 0){
        write(stdoutFD,"Error while recieving data from program\n", 41);
        stop("Error while recieving data from program");
    }
    write(stdoutFD, instanceData,bytesRead);
    
    if (!strncmp("ACCEPT; ; ", instanceData,11)){
        write(stdoutFD, "COMMAND TREATED\n",17);
        char saveFile[BUFFER_SIZE+1];
        while ((bytesRead = fread(instanceData, BUFFER_SIZE,1, file)) > 0){
            bytesSend = sendto(listenPort.sockFd,instanceData, bytesRead, 0, (struct sockaddr*) cliAddr,*len);
            if (bytesSend < 0){
                write(stdoutFD,"Error while sending data to program\n", 37);
                stop("Error while sending data to program");
            }
        }
    }   
    
    write(stdoutFD, "AFTER COMMAND TREATED\n",23);
    // DATA sauvegardé, début de l'envoi vers la machine distante (autre instance)
    
    // Données envoyées vers la machine distante (autre instance)
    // Attente de la réception du message de démarrage de la partie de la part de la machine distante
    bzero(instanceData, BUFFER_SIZE+1);
    while (START_GAME == 0){
        bytesRead = recvfrom(listenPort.sockFd, instanceData, BUFFER_SIZE, MSG_DONTWAIT, (struct sockaddr*) cliAddr, len );
        if (bytesRead < 0 && errno != EAGAIN){
            write(stdoutFD,"ERRO While recieving data from instance\n", 41);
            stop("Error while recieving data from instance");
        }
        else if (bytesRead > 0 && !strncmp("START_GAME",instanceData,10)){
            write(stdoutFD,"Sent successfully the pkl FILE, time to start game\n",52);
            START_GAME = 1;
        }
    }
    // Envoi de la commande START_GAME au programme python
    bytesSend = sendto(programSocket->sockFd,instanceData, bytesRead, 0, (struct sockaddr *) &programSocket->sock_addr,programSocket->addrLen);
    if (bytesSend < 0){
        stop("Error while sending command to program");
    }
    bzero(instanceData, BUFFER_SIZE+1);
    return listenPort;
    /*
    // Reception de la réponse du programme python
    bytesRead = recvfrom(programSocket->sockFd, instanceData, BUFFER_SIZE, 0,&programSocket->sock_addr, &programSocket->addrLen);
    
    if (bytesRead < 0){
        stop("Error while receiving response from program");
    }
    // Envoie cette même commande à la machine distante (autre instance)
    
    bytesSend = sendto(listenPort.sockFd,saveFile, BUFFER_SIZE, 0, cliAddr,len);
    
    if (bytesSend < 0){
        stop("Error while sending response to localmachine");
    }
    */
    return listenPort;
}

networkStruct createClientNetworkStruct(struct sockaddr_in cliSa,  socklen_t cliLen, int listenFD){
    networkStruct cliStruct;
    cliStruct.sockFd = listenFD;
    cliStruct.sock_addr = cliSa;
    cliStruct.addrLen = cliLen;
    return cliStruct;
}

int sendingUpdate(networkStruct* dst,networkStruct* src, char* msg, size_t size){

    int sentBytes = sendto(src->sockFd,msg, size, 0, &dst->sock_addr, dst->addrLen);

    if (sentBytes < 0){
        return -1;
    }
    else{
        return 1;
    }
}