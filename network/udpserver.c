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
    bzero(msg_to_send, BUFFER_SIZE + 1);
    bzero(received_msg, BUFFER_SIZE + 1);

    int udpserverfd = udpserver(&server_sa, 8000, ip);
    int tolocalhostfd = udpserver(&localhost_sa, 5000, LOCALHOSTIP);

    localhost_sa.sin_family = AF_INET;
    localhost_sa.sin_port = htons(5005);
    localhost_sa.sin_addr.s_addr = inet_addr("127.0.0.1");

    while (1) {
        FD_ZERO(&tolocalhost);
        FD_ZERO(&toserverfd);

        FD_SET(udpserverfd, &toserverfd);
        FD_SET(tolocalhostfd, &tolocalhost);

        // select
        selectfd = select((udpserverfd > tolocalhostfd ? udpserverfd : tolocalhostfd) + 1, &tolocalhost, &toserverfd, NULL, &timeout);
        if (selectfd == -1) {
            close(udpserverfd);
            close(tolocalhostfd);
            stop("Select error : ");
        } else if (selectfd) {
            // check whether an activity occured on the server socket
            if (FD_ISSET(udpserverfd, &toserverfd)) {
                printf("Activity detected on udpserverfd\n");

                if ((bytes_recu = recvfrom(udpserverfd, received_msg, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *) &client_sa, sizeof(client_sa))) < 0 && errno != EAGAIN) {
                    close(udpserverfd);
                    close(tolocalhostfd);
                    stop("Reception error on udpserverfd: ");
                }
                
                
                if(sendingUpdate(localhost_sa, tolocalhostfd, received_msg, bytes_recu) == -1){
                    close(udpserverfd);
                    close(tolocalhostfd);
                    stop("Sending to python program failed : ");
                }
            }

            // check whether an activity occured on the server socket
            if (FD_ISSET(tolocalhostfd, &tolocalhost)) {
                printf("Activity detected on tolocalhostfd\n");

                if ((bytes_recu = recvfrom(tolocalhostfd, received_msg, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *) &client_sa, &len)) < 0 && errno != EAGAIN) {
                    close(tolocalhostfd);
                    close(tolocalhostfd);
                    stop("Reception error on tolocalhostfd: ");
                }
                printf("Sending %s to the other players in broadcast...\n");
                if(broadcast_sending(udpserverfd, received_msg, bytes_recu) != 0){
                    close(udpserverfd);
                    close(tolocalhostfd);
                    stop("Sending to python program failed : ");
                }
                printf("Broadcast sent !\n");
            }
        }
    }

    
    close(udpserverfd);
    close(tolocalhostfd);
    return 0;
}
