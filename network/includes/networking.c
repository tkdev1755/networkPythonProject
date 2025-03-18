#include "networking.h"


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


void initializeCliList(selectStruct* sStruct){
    for (int i = 0; i<MAXCLIENTS; i++){
            sStruct->cliList[i] = 0;
        }
}
void initializeMasterSocket(selectStruct* sStruct, networkStruct* ntStruct){
    sStruct->masterSocket = ntStruct->sockFd;
}
int clearFDSets(selectStruct* sStruct){
    switch (sStruct->activeSets)
    {
    case 1:
        FD_ZERO(&(sStruct->readFds));
        break;
    case 2:
        FD_ZERO(&(sStruct->readFds));
        FD_ZERO(&(sStruct->writeFds));
        break;
    case 3:
        FD_ZERO(&(sStruct->readFds));
        FD_ZERO(&(sStruct->writeFds));
        FD_ZERO(&(sStruct->errorFds));
        break;
    default:
        printf("activeSet value not in range \n");
        return -1;
        break;
    }
    FD_SET(sStruct->masterSocket, &(sStruct->readFds));
    sStruct->maxSD = sStruct->masterSocket;
    return 0;
}

int updateFDSets(selectStruct* sStruct){
    printf("Updating maxClients\n");

    for (int i = 0 ; i< MAXCLIENTS; i++){
            
            int sd = sStruct->cliList[i]; 
            if (sd > 0){
                printf("Found new Socket Descriptor\n");
                switch (sStruct->activeSets)
                {
                case 1:
                    FD_SET(sd,&(sStruct->readFds));
                    break;
                case 2:
                    FD_SET(sd,&(sStruct->readFds));
                    FD_SET(sd,&(sStruct->writeFds));
                    break;
                case 3:
                    FD_SET(sd,&(sStruct->readFds));
                    FD_SET(sd,&(sStruct->writeFds));
                    FD_SET(sd,&(sStruct->errorFds));
                    break;
                default:
                    printf("Wrong activeSets parameter \n");
                    return -1;
                    break;
                }
            }
            if (sd > sStruct->maxSD){
                printf("Max fd is updated\n");
                sStruct->maxSD = sd;
            }
    }
    return 0;
}

int checkForNewConnection(selectStruct* sStruct){
    int cliFD = 0;
    struct sockaddr_in cliAddr;
    socklen_t cliLen;
    if (FD_ISSET(sStruct->masterSocket, &(sStruct->readFds))){
            printf("read activity on Master socket\n"); 
            if ((cliFD = accept(sStruct->masterSocket, (struct sockaddr*) &cliAddr,&cliLen))<0){
                return -1;
            }
            for (int i = 0; i<MAXCLIENTS; i++){
                if (sStruct->cliList[i] == 0){
                    sStruct->cliList[i] = cliFD;
                    printf("Added new client to fdList at position %d\n", i);
                    i = MAXCLIENTS;
                    sStruct->maxSD = sStruct->maxSD>cliFD ? sStruct->maxSD : cliFD;
                }
            }
            
            printf("====== !!! New client connected : Sockfd %d, ip is %s, port is %d====== !!!\n", cliFD, inet_ntoa(cliAddr.sin_addr),ntohs(cliAddr.sin_port));
    }
    return 0;
}

int disconnectClient(selectStruct* sStruct, int cliSD, int cliPos){
    printf("Disconnecting client \n");
    if (close(cliSD) < 0){
        return -1;
    }
    sStruct->cliList[cliPos] = 0;
    return 0;
}


// int input_timeout(int fd, unsigned int seconds){
//     fd_set fdset;

//     FD_ZERO(&fdset);
//     FD_SET(fd, &fdset);

//     struct timeval timeout;
//     timeout.tv_sec = seconds;
//     timeout.tv_usec = 0;

//     return TEMP_FAILURE_RETRY(select(FD_SETSIZE, &fdset, NULL, NULL, &timeout));
// }