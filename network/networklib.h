#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <sys/select.h>
#include <arpa/inet.h>
#define MAXLINE 1024
#define SA struct sockaddr
#define MAXCLIENTS 5

struct networkStruct {
    int sockFd;
    struct sockaddr_in addr;
    socklen_t addrLen;
    struct hostent* hostInfo;
};
typedef struct networkStruct networkStruct;

struct selectStruct{
    int masterSocket;
    int cliList[MAXCLIENTS];
    int maxSD;
    int activeSets;
    fd_set readFds;
    fd_set writeFds;
    fd_set errorFds;
};
typedef struct selectStruct selectStruct;

void createTcpSocket(networkStruct* ntStruct,int family);

void createUdpSocket(networkStruct* ntStruct, int family);

void fillSockAddr(networkStruct* ntStruct,char* ip, int port, int family);

int connectTCPServer(networkStruct* ntStruct);

void getHostInfoByName(networkStruct* ntStruct, char* hostName, int port);

int bindTCPSocket(networkStruct* ntStruct);

void initializeCliList(selectStruct* sStruct);

void initializeMasterSocket(selectStruct* sStruct, networkStruct* ntStruct);


int clearFDSets(selectStruct* sStruct);

int updateFDSets(selectStruct* sStruct);

int checkForNewConnection(selectStruct* sStruct);

int disconnectClient(selectStruct* sStruct, int cliSD,int cliPos);
