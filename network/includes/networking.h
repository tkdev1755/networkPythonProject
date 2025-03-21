#ifndef NETWORKING
#define NETWORKING
#define BUFFER_SIZE 1024
#define MAXCLIENTS 2
#define LOCALHOSTPORT 5005
#define SERVERPORT 8000
#define MAXLINE 2048
#define LOCALHOSTIP "127.0.0.1"
#define INTERFACE "en0"
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/errno.h>
#include <signal.h>
#include <net/if.h>
#include <netdb.h>
#include <sys/ioctl.h>


extern int stdoutFD;

struct networkStruct {
    int sockFd;
    struct sockaddr_in sock_addr;
    socklen_t addrLen;
    // struct hostent* hostInfo;
};
typedef struct networkStruct networkStruct;

// typedef struct selectStruct{
//     int masterSocket;
//     int cliList[MAXCLIENTS];
//     int maxSD;
//     int activeSets;
//     fd_set readFds;
//     fd_set writeFds;
//     fd_set errorFds;
// }selectStruct;

// typedef struct
// {
//     char message[BUFFER_SIZE + 1];
//     char id_destination[3];
//     char id[10];
// } packet_s;


// int tcpserver(struct sockaddr_in * sa, int port, char * ip, struct linger* so_linger_opt);
// int tcpclient(struct sockaddr_in * server_sa, int port, char * ip, struct linger* so_linger_opt);
int changeSTDOut(char* filename);

int udpserver(struct sockaddr_in * server_sa, int port, char * ip);
int udpclient(struct sockaddr_in * server_sa, int port, char * ip);
char * getip(const char * interface);
networkStruct join_game(char * game_ip, unsigned int game_port);
int broadcast_sending(int udpserverfd, char * message, int len);



// void initializeCliList(selectStruct* sStruct);

// void initializeMasterSocket(selectStruct* sStruct, networkStruct* ntStruct);

// int clearFDSets(selectStruct* sStruct);

// int updateFDSets(selectStruct* sStruct);

// int checkForNewConnection(selectStruct* sStruct);

// void initializeCliList(selectStruct* sStruct);

// void initializeMasterSocket(selectStruct* sStruct, networkStruct* ntStruct);

// int clearFDSets(selectStruct* sStruct);

// int updateFDSets(selectStruct* sStruct);

// int checkForNewConnection(selectStruct* sStruct);

// int disconnectClient(selectStruct* sStruct, int cliSD,int cliPos);

networkStruct initializeListenSocket();
networkStruct initializeProgramSocket();
networkStruct createGame(struct sockaddr_in* cliAddr, int* len, networkStruct* programSocket);
int initializeProgramConnection(networkStruct programSocket);

int sendingUpdate(struct sockaddr_in dstFD, int srcFD, char* msg, size_t size);
networkStruct createClientNetworkStruct(struct sockaddr_in cliSa,  socklen_t cliLen, int listenFD);

void closeAll(int *tab, int number_of_socket);

void stop( char* msg );

#endif