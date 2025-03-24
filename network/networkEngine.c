#include "includes/network.h"




int main() {
    fd_set toserverfd, tolocalhost;
    int bytes_recu = 0, selectfd;
    char ip[INET_ADDRSTRLEN];
    char received_msg[BUFFER_SIZE + 1];
    struct sockaddr_in server_sa, client_sa, localhost_sa, python_sa;
    socklen_t len = sizeof(client_sa);
    struct timeval timeout;
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;

    #ifdef _WIN32
    // Initialisation de Winsock pour Windows
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        stop("WSAStartup failed");
    }
    #endif

    // Obtenir l'adresse IP
    getip(INTERFACE_NAME, ip);
    // printf("My ip address :%s\n", ip);
    // exit(0);
    if (ip == NULL) {
        #ifdef _WIN32
        WSACleanup();
        #endif
        stop("Failed to get IP address");
    }

    // Initialisation des structures
    memset(&client_sa, 0, sizeof(struct sockaddr_in));
    memset(&localhost_sa, 0, sizeof(struct sockaddr_in));
    memset(&python_sa, 0, sizeof(struct sockaddr_in));
    memset(received_msg, 0, BUFFER_SIZE + 1);
    

    python_sa.sin_family = AF_INET;
    python_sa.sin_addr.s_addr = inet_addr(LOCALHOSTIP);
    python_sa.sin_port = htons(5006);

    int udpserverfd = udpserver(&server_sa, SERVERPORT, ip);
    int tolocalhostfd = udpserver(&localhost_sa, LOCALHOSTPORT, LOCALHOSTIP);

    int client_socket[3], max_client = 3, max_sd, socket_descriptor, activity, i, read_bytes = 0;
    for(int i = 0; i < max_client; i++){
        client_socket[i] = 0;
    }
    fd_set readfds;
    printf("Waiting for an update...\n");
    while (1) {
        FD_ZERO(&readfds);

        FD_SET(udpserverfd, &readfds); 
        FD_SET(tolocalhostfd, &readfds);
        max_sd = tolocalhostfd > udpserverfd ? tolocalhostfd : udpserverfd;

        for(i = 0; i < max_client; i++){
            socket_descriptor = client_socket[i];
            if(socket_descriptor > 0){
                FD_SET(socket_descriptor, &readfds);
            }

            if(socket_descriptor > max_sd){
                max_sd = socket_descriptor;
            }
        }

        #ifdef _WIN32
        // Windows : select n'a pas besoin de +1
        if((activity = select(max_sd, &readfds, NULL, NULL, &timeout)) == SOCKET_ERROR) {
            closesocket(udpserverfd);
            closesocket(tolocalhostfd);
            WSACleanup();
            stop("Select error: ");
        }
        #else
        // Linux : select a besoin de max_sd + 1
        if((activity = select(max_sd + 1, &readfds, NULL, NULL, &timeout)) < 0 && errno != EINTR){
            close(udpserverfd);
            close(tolocalhostfd);
            stop("Select error: ");
        }
        #endif

        // Vérifie si un événement est survenu sur le descripteur udpserverfd
        if (FD_ISSET(udpserverfd, &readfds)) {
            printf("Activity detected on udpserverfd\n");

            #ifdef _WIN32
            bytes_recu = recvfrom(udpserverfd, received_msg, BUFFER_SIZE - 1, 0, (struct sockaddr *) &client_sa, (int *) &len);
            if (bytes_recu == SOCKET_ERROR) {
                if (WSAGetLastError() != WSAEWOULDBLOCK) {
                    closesocket(udpserverfd);
                    closesocket(tolocalhostfd);
                    WSACleanup();
                    stop("Reception error on udpserverfd: ");
                }
            }
            #else
            bytes_recu = recvfrom(udpserverfd, received_msg, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *) &client_sa, (socklen_t *) &len);
            if (bytes_recu < 0 && errno != EAGAIN) {
                close(udpserverfd);
                close(tolocalhostfd);
                stop("Reception error on udpserverfd: ");
            }
            #endif

            if(strncmp(inet_ntoa(client_sa.sin_addr), ip, strlen(inet_ntoa(client_sa.sin_addr))) != 0){
                
                if (bytes_recu > 0) {
                    received_msg[bytes_recu] = '\0';
                    printf("%s\n", received_msg);
                    
                    printf("Sending to localhost ...\n");
                    if (sendingUpdate(python_sa, tolocalhostfd, received_msg, bytes_recu) == -1) {
                        #ifdef _WIN32
                        closesocket(udpserverfd);
                        closesocket(tolocalhostfd);
                        WSACleanup();
                        #else
                        close(udpserverfd);
                        close(tolocalhostfd);
                        #endif
                        stop("Sending to python program failed: ");
                    }
                    printf("Sent successfully!\n");
                }
            }
        }
            
            // Vérifie si un événement est survenu sur le descripteur tolocalhostfd
        if (FD_ISSET(tolocalhostfd, &readfds)) {
            printf("Activity detected on tolocalhostfd\n");

            #ifdef _WIN32
            bytes_recu = recvfrom(tolocalhostfd, received_msg, BUFFER_SIZE - 1, 0, (struct sockaddr *) &client_sa, (int *) &len);
            if (bytes_recu == SOCKET_ERROR) {
                if (WSAGetLastError() != WSAEWOULDBLOCK) {
                    closesocket(tolocalhostfd);
                    WSACleanup();
                    stop("Reception error on tolocalhostfd: ");
                }
            }
            #else
            bytes_recu = recvfrom(tolocalhostfd, received_msg, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *) &client_sa, &len);
            if (bytes_recu < 0 && errno != EAGAIN) {
                close(tolocalhostfd);
                stop("Reception error on tolocalhostfd: ");
            }
            #endif

            if (bytes_recu > 0) {
                received_msg[bytes_recu] = '\0';
                printf("Sending %s to the other players in broadcast...\n", received_msg);

                if (broadcast_sending(udpserverfd, received_msg, bytes_recu) != 0) {
                    #ifdef _WIN32
                    closesocket(udpserverfd);
                    closesocket(tolocalhostfd);
                    WSACleanup();
                    #else
                    close(udpserverfd);
                    close(tolocalhostfd);
                    #endif
                    stop("Sending to python program failed: ");
                }

                printf("Broadcast sent!\n");
            }
        }
    }

    // Nettoyage
    #ifdef _WIN32
    for(i = 0; i < max_client; i++) {
        if(client_socket[i] > 0) {
            closesocket(client_socket[i]);
        }
    }
    closesocket(udpserverfd);
    closesocket(tolocalhostfd);
    WSACleanup();
    #else
    closeAll(client_socket, max_client);
    close(udpserverfd);
    close(tolocalhostfd);
    #endif
    return 0;
}