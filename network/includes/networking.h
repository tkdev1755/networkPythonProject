#ifndef NETWORKING
#define NETWORKING
#define BUFFER_SIZE 1024
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

typedef struct
{
    char message[BUFFER_SIZE + 1];
    char id_destination[3];
    char id[10];
} packet_s;


// int tcpserver(struct sockaddr_in * sa, int port, char * ip, struct linger* so_linger_opt);
// int tcpclient(struct sockaddr_in * server_sa, int port, char * ip, struct linger* so_linger_opt);

int udpserver(struct sockaddr_in * server_sa, int port, char * ip);
int udpclient(struct sockaddr_in * server_sa, int port, char * ip);

//select
// int input_timeout(int fd, unsigned int seconds);
void closeAll(int *tab, int number_of_socket);

void stop( char* msg );

#endif