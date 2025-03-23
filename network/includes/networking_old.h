#ifndef NETWORKING
#define NETWORKING
#define BUFFER_SIZE 1024
#define MAXCLIENTS 2
#define LOCALHOSTPORT 5005
#define SERVERPORT 8000
#define MAXLINE 2048
#define LOCALHOSTIP "127.0.0.1"
#define INTERFACE "eth0"
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
};
typedef struct networkStruct networkStruct;

int changeSTDOut(char* filename);

int udpserver(struct sockaddr_in * server_sa, int port, char * ip);
int udpclient(struct sockaddr_in * server_sa, int port, char * ip);
char * getip(const char * interface);
networkStruct join_game(char * game_ip, unsigned int game_port);
int broadcast_sending(int udpserverfd, char * message, int len);

networkStruct initializeListenSocket();
networkStruct initializeProgramSocket();
networkStruct createGame(struct sockaddr_in* cliAddr, int* len, networkStruct* programSocket);
int initializeProgramConnection(networkStruct programSocket);

int sendingUpdate(struct sockaddr_in dstFD, int srcFD, char* msg, size_t size);
networkStruct createClientNetworkStruct(struct sockaddr_in cliSa,  socklen_t cliLen, int listenFD);

void closeAll(int *tab, int number_of_socket);

void stop( char* msg );

#endif