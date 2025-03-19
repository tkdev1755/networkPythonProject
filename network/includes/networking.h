#ifndef NETWORKING
#define NETWORKING
#define BUFFER_SIZE 1024
#define MAXCLIENTS 2
#define LOCALHOSTPORT 5005
#define SERVERPORT 8000
#define MAXLINE 2048
#define LOCALHOSTIP "127.0.0.1"
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>

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

int udpserver(struct sockaddr_in * server_sa, int port, char * ip);
int udpclient(struct sockaddr_in * server_sa, int port, char * ip);
char * getip(const char * interface);
networkStruct join_game(char * game_ip, unsigned int game_port);



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
int initializeProgramConnection();



//select
// int input_timeout(int fd, unsigned int seconds);
void closeAll(int *tab, int number_of_socket);

void stop( char* msg );

#endif