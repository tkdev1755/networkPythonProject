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

// int tcpserver(struct sockaddr_in * server_sa, int port, char * ip, struct linger* so_linger_opt){
    
//     int socketfd = socket(AF_INET, SOCK_STREAM, 0);
//     int option = 1;
//     if(socketfd < 0){
//         stop("Socket creation failed !");
//     }
//     so_linger_opt->l_onoff = 1;  // Activer SO_LINGER
//     so_linger_opt->l_linger = 0; // Temps de délai = 0 secondes
//     if(setsockopt(socketfd, SOL_SOCKET, SO_LINGER, so_linger_opt, sizeof(struct linger)) < 0){
//         close(socketfd);
//         stop("Setting options failed !");
//     }
//     if(setsockopt(socketfd, SOL_SOCKET, SO_REUSEADDR, (char *)&option, sizeof(option)) < 0){
//         close(socketfd);
//         stop("Setting options failed !");
//     }
//     bzero(server_sa, sizeof(struct sockaddr_in));
//     server_sa->sin_family = AF_INET;
//     server_sa->sin_port = htons(port);
//     server_sa->sin_addr.s_addr = (strncmp(ip, "any", 3) == 0) ? INADDR_ANY : inet_addr(ip);


//     if(bind(socketfd, (struct sockaddr *)server_sa, sizeof(struct sockaddr)) < 0){
//         close(socketfd);  
//         stop("Binding failed !");
//     }
//     return socketfd;
// }

// int tcpclient(struct sockaddr_in * server_sa, int port, char * ip, struct linger* so_linger_opt){
//     int socketfd = socket(AF_INET, SOCK_STREAM, 0);
//     if(socketfd < 0){
//         stop("Socket creation failed !");
//     }

//     so_linger_opt->l_onoff = 1;  // Activer SO_LINGER
//     so_linger_opt->l_linger = 0; // Temps de délai = 0 secondes
//     if(setsockopt(socketfd, SOL_SOCKET, SO_LINGER, so_linger_opt, sizeof(struct linger)) < 0){
//         close(socketfd);
//         stop("Setting options failed !");
//     }

//     bzero(server_sa, sizeof(struct sockaddr_in));
//     server_sa->sin_family = AF_INET;
//     server_sa->sin_port = htons(port);
//     server_sa->sin_addr.s_addr = inet_addr(ip);

//     if(connect(socketfd,(struct sockaddr *)server_sa, sizeof(struct sockaddr)) < 0){
//         close(socketfd);
//         stop("Connection failed !");
//     }
//     return socketfd;
// }


int udpclient(struct sockaddr_in *server_sa, int port, char * ip){
    int socketfd = socket(AF_INET, SOCK_DGRAM, 0);
    if(socketfd < 0){
        stop("Socket creation failed !");
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
    // printf("%d\n",socketfd);
    bzero(server_sa, sizeof(struct sockaddr_in));
    server_sa->sin_family = AF_INET;
    server_sa->sin_port = htons(port);
    server_sa->sin_addr.s_addr = inet_addr(ip);

    if(bind(socketfd, (struct sockaddr *)server_sa, sizeof(struct sockaddr)) < 0){
        close(socketfd);
        perror("Binding failed : ");
        stop("Binding failed !");
    }
    
    return socketfd;
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