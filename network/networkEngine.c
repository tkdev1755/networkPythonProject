#include "includes/networking.h"

int main() {
    fd_set toserverfd, tolocalhost;
    int bytes_recu = 0, selectfd;
    char *ip = getip(INTERFACE); //ip of my eth0 interface
    char received_msg[BUFFER_SIZE + 1];
    struct sockaddr_in server_sa, client_sa, localhost_sa;
    socklen_t len = sizeof(client_sa);
    struct timeval timeout;
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;

    bzero(&client_sa, sizeof(struct sockaddr_in));
    bzero(&localhost_sa, sizeof(struct sockaddr_in));
    bzero(received_msg, BUFFER_SIZE + 1);

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
        max_sd = tolocalhostfd;


        for(i = 0; i < max_client; i++){
            socket_descriptor = client_socket[i];
            if(socket_descriptor > 0){
                FD_SET(socket_descriptor, &readfds);
            }

            if(socket_descriptor > max_sd){
                max_sd = socket_descriptor;
            }
        }

        if((activity = select(max_sd + 1, &readfds, NULL, NULL, &timeout)) < 0 && errno!=EINTR){
            close(udpserverfd);
            close(tolocalhostfd);
            stop("Select error : ");
        }

        
        // Vérifie si un événement est survenu sur le descripteur udpserverfd
        if (FD_ISSET(udpserverfd, &readfds)) {
            printf("Activity detected on udpserverfd\n");

            bytes_recu = recvfrom(udpserverfd, received_msg, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *) &client_sa, (socklen_t *) &len);

            if (bytes_recu < 0 && errno != EAGAIN) {
                close(udpserverfd);
                close(tolocalhostfd);
                stop("Reception error on udpserverfd: ");
            }

            printf("%s\n", received_msg);
            printf("Sending to %s ...\n");
            if (sendingUpdate(localhost_sa, tolocalhostfd, received_msg, bytes_recu) == -1) {
                close(udpserverfd);
                close(tolocalhostfd);
                stop("Sending to python program failed : ");
            }
            printf("Sent succefully !\n");
        }

        // Vérifie si un événement est survenu sur le descripteur tolocalhostfd
        if (FD_ISSET(tolocalhostfd, &readfds)) {
            printf("Activity detected on tolocalhostfd\n");

            bytes_recu = recvfrom(tolocalhostfd, received_msg, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *) &client_sa, &len);

            if (bytes_recu < 0 && errno != EAGAIN) {
                close(tolocalhostfd);
                stop("Reception error on tolocalhostfd: ");
            }

            printf("Sending %s to the other players in broadcast...\n");

            if (broadcast_sending(udpserverfd, received_msg, bytes_recu) != 0) {
                close(udpserverfd);
                close(tolocalhostfd);
                stop("Sending to python program failed : ");
            }

            printf("Broadcast sent !\n");
        }
    }

    closeAll(client_socket, max_client);
    close(udpserverfd);
    close(tolocalhostfd);
    return 0;
}
