#include "network.h"

int stdoutFD = 1;

void stop(char* msg) {
    perror(msg);
    #ifdef _WIN32
    WSACleanup();
    #endif
    exit(EXIT_FAILURE);
}

void closeAll(int *tab, int number_of_socket) {
    for(int i = 0; i < number_of_socket; i++) {
        #ifdef _WIN32
        closesocket(tab[i]);
        #else
        close(tab[i]);
        #endif
    }
}

int udpserver(struct sockaddr_in *server_sa, int port, char * ip) {
    #ifdef _WIN32
    // Initialise Winsock if not done
    static int winsock_initialized = 0;
    if (!winsock_initialized) {
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            stop("WSAStartup failed");
        }
        winsock_initialized = 1;
    }
    SOCKET socketfd = socket(AF_INET, SOCK_DGRAM, 0);
    if(socketfd == INVALID_SOCKET) {
        stop("Socket creation failed!");
    }
    #else
    int socketfd = socket(AF_INET, SOCK_DGRAM, 0);
    if(socketfd < 0) {
        stop("Socket creation failed!");
    }
    #endif

    if(ip == NULL) {
        stop("IP adress is null!");
    }

    memset(server_sa, 0, sizeof(struct sockaddr_in));
    server_sa->sin_family = AF_INET;
    server_sa->sin_port = htons(port);
    server_sa->sin_addr.s_addr = INADDR_ANY;

    if(bind(socketfd, (struct sockaddr *)server_sa, sizeof(struct sockaddr)) < 0) {
        #ifdef _WIN32
        closesocket(socketfd);
        #else
        close(socketfd);
        #endif
        stop("Binding failed!");
    }

    return socketfd;
}

#ifdef _WIN64
// Converting char* to wchar_t* used in the getip function
wchar_t* charToWChar(const char* text) {
    size_t size = strlen(text) + 1;
    wchar_t* wText = malloc(size * sizeof(wchar_t));
    mbstowcs(wText, text, size);
    return wText;
}
#endif

char * getip(const char * interface_name, char * ip) {
    #ifdef _WIN32
    wchar_t* wInterfaceName = charToWChar(interface_name);
    ULONG ulOutBufLen = 0;
    DWORD dwRetVal = 0;
    int interfaceTrouvee = 0;

    // Adapters informations variables
    PIP_ADAPTER_ADDRESSES pAddresses = NULL;
    PIP_ADAPTER_ADDRESSES pCurrAddresses = NULL;
    PIP_ADAPTER_UNICAST_ADDRESS pUnicast = NULL;

    
    //getting the buffer's size
    GetAdaptersAddresses(AF_INET, GAA_FLAG_INCLUDE_PREFIX, NULL, NULL, &ulOutBufLen);

    // allocationg memory for the buffer with the obtained size
    pAddresses = (IP_ADAPTER_ADDRESSES*) malloc(ulOutBufLen);
    if (pAddresses == NULL) {
        printf("Memory allocation failed in getip !\n");
        ip = NULL;
        return NULL;
    }

    // gathering adapters information
    dwRetVal = GetAdaptersAddresses(AF_INET, GAA_FLAG_INCLUDE_PREFIX, NULL, pAddresses, &ulOutBufLen);

    if (dwRetVal == NO_ERROR) {
        // browsing all adapters
        pCurrAddresses = pAddresses;
        while (pCurrAddresses) {
            // Comparing interface name and the given interface name
            if (wcscmp(pCurrAddresses->FriendlyName, wInterfaceName) == 0) {
                interfaceTrouvee = 1;
                printf("\nInformations pour l'interface: %ls\n", pCurrAddresses->FriendlyName);
                // getting unicast addresses for this adapter
                pUnicast = pCurrAddresses->FirstUnicastAddress;
                if (pUnicast == NULL) {
                    printf("Aucune adresse IP trouvée pour cette interface.\n");
                    ip = NULL;
                }

                while (pUnicast != NULL) {
                    // getting the IP address
                    ip[INET_ADDRSTRLEN];
                    struct sockaddr_in* sockaddr = (struct sockaddr_in*)pUnicast->Address.lpSockaddr;
                    inet_ntop(AF_INET, &(sockaddr->sin_addr), ip, INET_ADDRSTRLEN);
                    pUnicast = pUnicast->Next;
                }

                break;
            }

            pCurrAddresses = pCurrAddresses->Next;
        }

        if (!interfaceTrouvee) {
            printf("Interface '%ls' non trouvée.\n", interface_name);
            ip = NULL;
        }
    } else {
        printf("Erreur lors de l'appel à GetAdaptersAddresses: %d\n", dwRetVal);
        ip = NULL;
    }

    if (pAddresses) {
        free(pAddresses);
    }

    #else
    // For Linux
    struct ifaddrs *ifaddr, *ifa;

    // gathering @ip
    if (getifaddrs(&ifaddr) == -1) {
        perror("getifaddrs");
        return NULL;
    }

    // browse all interfaces
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL) continue;

        if (ifa->ifa_addr->sa_family == AF_INET && strcmp(ifa->ifa_name, interface_name) == 0) {
            struct sockaddr_in *sa = (struct sockaddr_in *)ifa->ifa_addr;
            inet_ntop(AF_INET, &(sa->sin_addr), ip, INET_ADDRSTRLEN);
            freeifaddrs(ifaddr);
            return ip;
        }
    }

    freeifaddrs(ifaddr);
    ip = NULL;
    return NULL;  // interface not found
    #endif
}

int sendingUpdate(struct sockaddr_in dstFD, int srcFD, char* msg, size_t size) {

    int sentBytes = sendto(srcFD, msg, size, 0, (struct sockaddr *) &dstFD, (socklen_t) sizeof(dstFD));

    if (sentBytes < 0) {
        return -1;
    }
    else {
        return 1;
    }
}

void catch(void) {
    #ifdef _WIN32
    WSACleanup();
    #endif
    exit(EXIT_SUCCESS);
}

int broadcast_sending(int udpserverfd, char * message, int len) {
    // A part of this code is written by Christian Toinard : christian.toinard(at)insa-cvl.fr

    #ifdef _WIN32
    signal(SIGINT, (void (__cdecl *)(int))catch);
    #else
    typedef void (*sighandler_t)(int);
    signal(SIGINT, (sighandler_t)catch);
    #endif
    //windows code
    #ifdef _WIN32
    // Windows broadcasting
    BOOL bOptVal = TRUE;
    int bOptLen = sizeof(BOOL);

    if (setsockopt(udpserverfd, SOL_SOCKET, SO_BROADCAST, (char*)&bOptVal, bOptLen) < 0) {
        closesocket(udpserverfd);
        stop("setsockopt failed, and broadcasting failed: ");
    }

    // Obtenir la liste des interfaces réseau
    PMIB_IPADDRTABLE pIPAddrTable;
    DWORD dwSize = 0;
    DWORD dwRetVal = 0;
    IN_ADDR IPAddr;

    pIPAddrTable = (MIB_IPADDRTABLE *) malloc(sizeof(MIB_IPADDRTABLE));
    if (pIPAddrTable == NULL) {
        stop("Memory allocation failed for GetIpAddrTable");
    }

    // Faire un premier appel pour obtenir la taille nécessaire
    if (GetIpAddrTable(pIPAddrTable, &dwSize, 0) == ERROR_INSUFFICIENT_BUFFER) {
        free(pIPAddrTable);
        pIPAddrTable = (MIB_IPADDRTABLE *) malloc(dwSize);
        if (pIPAddrTable == NULL) {
            stop("Memory allocation failed for GetIpAddrTable");
        }
    }

    // Obtenir la table d'adresses IP
    if ((dwRetVal = GetIpAddrTable(pIPAddrTable, &dwSize, 0)) == NO_ERROR) {
        for (int i = 0; i < (int) pIPAddrTable->dwNumEntries; i++) {
            // Calculer l'adresse de broadcast pour chaque interface
            IPAddr.S_un.S_addr = (pIPAddrTable->table[i].dwAddr & pIPAddrTable->table[i].dwMask)
                                | (~pIPAddrTable->table[i].dwMask);

            struct sockaddr_in dst;
            memset(&dst, 0, sizeof(dst));
            dst.sin_family = AF_INET;
            dst.sin_addr.s_addr = IPAddr.S_un.S_addr;
            dst.sin_port = htons(SERVERPORT);

            sendingUpdate(dst, udpserverfd, message, len);
        }
    }

    free(pIPAddrTable);

    #else
    // Linux code
    char buffer[BUFFER_SIZE];
    struct ifconf ifc;
    ifc.ifc_len = sizeof(buffer);
    ifc.ifc_buf = buffer;

    int on = 1;

    if (setsockopt(udpserverfd, SOL_SOCKET, SO_BROADCAST, &on, sizeof(on)) < 0) {
        close(udpserverfd);
        stop("setcokopt failed, and broadcasting failed: ");
    }

    ioctl(udpserverfd, SIOCGIFCONF, (char*)&ifc);

    struct ifreq *ifr;
    ifr = ifc.ifc_req;

    int n = ifc.ifc_len/sizeof(*ifr);
    for(; --n >= 0 ; ifr++) {
        ioctl(udpserverfd, SIOCGIFFLAGS, (char*)ifr);

        if (((ifr->ifr_flags & IFF_UP) == 0) ||
            (ifr->ifr_flags & IFF_LOOPBACK) ||
            (ifr->ifr_flags & IFF_POINTOPOINT) ||
            ((ifr->ifr_flags & IFF_BROADCAST) == 0)) {
            continue;
        }

        ioctl(udpserverfd, SIOCGIFBRDADDR, (char*)ifr);

        struct sockaddr_in dst;
        memcpy(&dst, &ifr->ifr_broadaddr, sizeof(ifr->ifr_broadaddr));
        dst.sin_family = AF_INET;
        dst.sin_port = htons(SERVERPORT);

        sendingUpdate(dst, udpserverfd, message, len);
    }
    #endif

    return 0;
}