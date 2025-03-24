#ifndef NETWORKING
#define NETWORKING
// #define _WIN64
#define BUFFER_SIZE 1024
#define MAXCLIENTS 2
#define LOCALHOSTPORT 5005
#define SERVERPORT 8000
#define MAXLINE 2048
#define LOCALHOSTIP "127.0.0.1"
#define INTERFACE_NAME "Wi-Fi"

// Détection du système d'exploitation
#if defined(_WIN32) || defined(_WIN64) || defined(WIN32)
    // Inclusions Windows
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #include <windows.h>
    #include <iphlpapi.h>
    #pragma comment(lib, "iphlpapi.lib")
    #pragma comment(lib, "ws2_32.lib")
    typedef int socklen_t;
    #define bzero(b,len) (memset((b), '\0', (len)), (void) 0)
    #define close(s) closesocket(s)
#else
    // Inclusions Linux/UNIX
    #include <sys/socket.h>
    #include <sys/select.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <ifaddrs.h>
    #include <net/if.h>
    #include <sys/ioctl.h>
    #include <netdb.h>
    #include <sys/types.h>
#endif

// Inclusions communes
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <signal.h>

#ifdef _WIN32
    // Pour Windows
    #define SOCKET_ERROR_CODE WSAGetLastError()
#else
    // Pour Linux/UNIX
    #include <unistd.h>
    #include <strings.h>
    #define SOCKET_ERROR_CODE errno
#endif

extern int stdoutFD;

struct networkStruct {
    int sockFd;
    struct sockaddr_in sock_addr;
    socklen_t addrLen;
};
typedef struct networkStruct networkStruct;

// Initialisation de Winsock pour Windows
#ifdef _WIN32
static int initializeWinsock() {
    WSADATA wsaData;
    return WSAStartup(MAKEWORD(2, 2), &wsaData);
}

// Nettoyage de Winsock
static void cleanupWinsock() {
    WSACleanup();
}
#endif

int udpserver(struct sockaddr_in * server_sa, int port, char * ip);
int udpclient(struct sockaddr_in * server_sa, int port, char * ip);
// char * getip(const char * interface);
char * getip(const char * interface_name, char * ip);
int broadcast_sending(int udpserverfd, char * message, int len);


int sendingUpdate(struct sockaddr_in dstFD, int srcFD, char* msg, size_t size);
void closeAll(int *tab, int number_of_socket);

void stop(char* msg);

#endif