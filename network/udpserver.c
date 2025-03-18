#include "includes/networking.h"

int main(){
    fd_set readfds;
    int bytes_recu = 0, selectfd;
    char *ip = getip("eth0"); //ip of my eth0 interface
    char msg_to_send[BUFFER_SIZE + 1];
    char received_msg[BUFFER_SIZE + 1];
    struct sockaddr_in server_sa, client_sa, localhost_sa;
    socklen_t len = sizeof(client_sa);
    struct timeval timeout;
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;

    bzero(&client_sa, sizeof(struct sockaddr_in));
    bzero(msg_to_send, BUFFER_SIZE + 1);
    bzero(received_msg, BUFFER_SIZE + 1);

    int udpserverfd = udpserver(&server_sa, 8000, ip);

    localhost_sa.sin_family = AF_INET;
    localhost_sa.sin_port = htons(5500);
    localhost_sa.sin_addr.s_addr = inet_addr("127.0.0.1");

    while (1){
        
        FD_ZERO(&readfds);
        FD_SET(udpserverfd, &readfds);

        selectfd = select(udpserverfd + 1, &readfds, NULL, NULL, &timeout);
        if (selectfd == -1) {
            close(udpserverfd);
            stop("Select error : ");
        } else if (selectfd) {
            if (FD_ISSET(udpserverfd, &readfds)) {
                if(bytes_recu = recvfrom(udpserverfd, received_msg, BUFFER_SIZE - 1, MSG_DONTWAIT, (struct sockaddr *) &client_sa, sizeof(client_sa)) < 0 && errno != EAGAIN){
                    close(udpserverfd);
                    stop("Reception error : ");
                }else{
                    //if it is from the other server, send it to the other socket to send it to the python program
                    if (strcmp(inet_ntoa(client_sa.sin_addr), "127.0.0.1") != 0){
                        if ((sendto(udpserverfd, received_msg, bytes_recu, 0, (struct sockaddr *)&localhost_sa, sizeof(localhost_sa))) < 0) {
                            close(udpserverfd);
                            stop("Sending to python program failed : ");
                        }
                    }
                    else{
                        /*
                        We have to set the client sockaddr first, so we have to discuss how to get the other player ip adress and port to set it. Let do it this afternoon !
                        */
                        if ((sendto(udpserverfd, received_msg, bytes_recu, 0, (struct sockaddr *)&client_sa, sizeof(client_sa))) < 0) {
                            close(udpserverfd);
                            stop("Sending to the server failed : ");
                        }
                    }
                }
            }  
        }
    }
}