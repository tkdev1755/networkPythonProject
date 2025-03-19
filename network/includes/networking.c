#include "networking.h"
#include <stdlib.h>
#include <stdio.h>

void stop( char* msg ){
  perror(msg);
  exit(EXIT_FAILURE);
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
    networkStruct joinning_struct = initializeListenSocket();
    struct sockaddr_in sock_to_send_srv, sock_localhost;
    int received_bytes = 0;
    char received_msg[BUFFER_SIZE + 1];
    char * msg_to_send = "CONNECT; ; ";
    FILE * file = fopen("save", "wb");

    bzero(&sock_to_send_srv, sizeof(struct sockaddr_in));
    bzero(&sock_localhost, sizeof(struct sockaddr_in));
    bzero(received_msg, BUFFER_SIZE + 1);

    sock_to_send_srv.sin_family = AF_INET;
    sock_to_send_srv.sin_port = htons(game_port);
    sock_to_send_srv.sin_addr.s_addr = inet_addr(game_ip);

    sock_localhost.sin_family = AF_INET;
    sock_localhost.sin_addr.s_addr = inet_addr("127.0.0.1");
    sock_localhost.sin_port = 5005;

    if(sendto(joinning_struct.sockFd, msg_to_send, 11, 0, (struct sockaddr *) &sock_to_send_srv, sizeof(sock_to_send_srv)) < 0){
        close(joinning_struct.sockFd);
        fclose(file);
        stop("Joinning the game failed : ");
    }

    while ((received_bytes = recvfrom(joinning_struct.sockFd, received_msg, BUFFER_SIZE, 0, (struct sockaddr *) &joinning_struct.sock_addr, &joinning_struct.addrLen)) > 0){
        if(fwrite(received_msg, sizeof(char), received_bytes, file) < 0){
            fclose(file);
            close(joinning_struct.sockFd);
            stop("Receiving the game failed : ");
        }
    }

    if(sendto(joinning_struct.sockFd, "PLAY; ; ", 8, 0, (struct sockaddr *) &sock_localhost, sizeof(sock_localhost)) < 0){
        fclose(file);
        close(joinning_struct.sockFd);
        stop("Informing to start the game failed : ");
    }

    return joinning_struct;
}

networkStruct initializeListenSocket(){
    networkStruct ntStruct;
    bzero(&(ntStruct.sock_addr), sizeof(struct sockaddr_in));
    struct sockaddr_in server_sa;
    int udpserverfd = udpserver(&server_sa, SERVERPORT, getip("eth0"));

    ntStruct.addrLen = sizeof(server_sa);
    ntStruct.sock_addr = server_sa;
    ntStruct.sockFd = udpserverfd;  
      
    return ntStruct;
}

networkStruct initializeProgramSocket(){
    networkStruct ntStruct;
    bzero(&(ntStruct.sock_addr), sizeof(struct sockaddr_in));
    struct sockaddr_in program_sa; 

    ntStruct.addrLen = sizeof(program_sa);
    ntStruct.sock_addr = program_sa;
    ntStruct.sockFd = udpclient(&program_sa, LOCALHOSTPORT, LOCALHOSTIP);

    return ntStruct;
}

int initializeProgramConnection(){
    // Insérer ici le code d'initialisation de la communication avec le programme python
    
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
            stop("Error while recieving data from instance");
        }
        else {
            if (bytesRead > 0 && !strncmp("CONNECT",instanceData,7)){
                printf("Recieved Connection request");
                CONNECTION_REQUEST = 1;
            }
            else{
                printf("Shouldn't get this command");
            }
        }
    }
    // Deuxième partie de la connexion - Lecture du fichier .pkl et Envoi du monde à la deuxième instance
    // Envoi de la commande au programme python
    int sentData = sendto(programSocket->sockFd,instanceData, bytesRead, 0, (struct sockaddr*) &programSocket->sock_addr,&programSocket->addrLen);
    if (sentData < 0){
        stop("Error while sending command to program");
    }

    bzero(instanceData,BUFFER_SIZE+1);

    bytesRead = recvfrom(programSocket->sockFd, instanceData, BUFFER_SIZE, 0, (struct sockaddr*) &programSocket->sock_addr, &programSocket->addrLen);
    if (bytesRead < 0){
        stop("Error while recieving data from program");
    }
    if (!stnrcmp("ACCEPT", instanceData,6)){
        FILE* file = fopen("save","rb");
        char saveFile[BUFFER_SIZE+1];
        while ((bytesRead = (instanceData, BUFFER_SIZE,1, file)) > 0){
            bytesSend = sendto(listenPort.sockFd,instanceData, bytesRead, 0, (struct sockaddr*) cliAddr,len);
            if (bytesSend < 0){
                stop("Error while sending data to program");
            }
        }
    }
    // DATA sauvegardé, début de l'envoi vers la machine distante (autre instance)
    
    // Données envoyées vers la machine distante (autre instance)

    bzero(instanceData, BUFFER_SIZE+1);
    while (START_GAME == 0){
        bytesRead = recvfrom(listenPort.sockFd, instanceData, BUFFER_SIZE, MSG_DONTWAIT, (struct sockaddr*) cliAddr, len );
        if (bytesRead < 0 && errno != EAGAIN){
            stop("Error while recieving data from instance");
        }
        else if (bytesRead > 0 && !strncmp("START_GAME",instanceData,10)){
            printf("Sent successfully the pkl FILE, time to start game");
            START_GAME = 1;
        }
    }
    // Envoi de la commande START_GAME au programme python
    int bytesSend = sendto(programSocket->sockFd,instanceData, bytesRead, 0, &programSocket->sock_addr,&programSocket->addrLen);
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