#include "networkLib.h"

void createTcpSocket(networkStruct* ntStruct, int family){
    ntStruct->sockFd = socket(family, SOCK_STREAM, 0);
}
void createUdpSocket(networkStruct* ntStruct, int family){
        ntStruct->sockFd = socket(family, SOCK_DGRAM, 0);
}

void fillSockAddr(networkStruct* ntStruct,char* ip, int port, int family){
    bzero(&(ntStruct->addr), sizeof(struct sockaddr_in));
    ntStruct->addr.sin_family = AF_INET;
    ntStruct->addr.sin_addr.s_addr = inet_addr(ip);
    ntStruct->addr.sin_port = htons(port);
}

int connectTCPServer(networkStruct* ntStruct){
    return connect(ntStruct->sockFd, (SA*) &(ntStruct->addr), sizeof(ntStruct->addr));
}

void getHostInfoByName(networkStruct* ntStruct, char* hostName, int port){
    (ntStruct->hostInfo) = gethostbyname(hostName);
    if (ntStruct->hostInfo != NULL){
        bcopy((char*)ntStruct->hostInfo, &(ntStruct->addr).sin_addr.s_addr, ntStruct->hostInfo->h_length);
        ntStruct->addr.sin_port = port;
    }
}

int bindTCPSocket(networkStruct* ntStruct){
    return bind(ntStruct->sockFd, (SA*) &(ntStruct->addr), sizeof(ntStruct->addr));
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

