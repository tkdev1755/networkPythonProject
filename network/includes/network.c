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

int udpclient(struct sockaddr_in *server_sa, int port, char * ip) {
    #ifdef _WIN32
    // Initialiser Winsock si pas déjà fait
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
    server_sa->sin_addr.s_addr = inet_addr(ip);

    return socketfd;
}

int udpserver(struct sockaddr_in *server_sa, int port, char * ip) {
    #ifdef _WIN32
    // Initialiser Winsock si pas déjà fait
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
// Fonction pour convertir une chaîne char* en wchar_t*
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

    // Variables pour stocker les informations des adaptateurs
    PIP_ADAPTER_ADDRESSES pAddresses = NULL;
    PIP_ADAPTER_ADDRESSES pCurrAddresses = NULL;
    PIP_ADAPTER_UNICAST_ADDRESS pUnicast = NULL;

    // Première appel pour obtenir la taille du buffer nécessaire
    GetAdaptersAddresses(AF_INET, GAA_FLAG_INCLUDE_PREFIX, NULL, NULL, &ulOutBufLen);
    
    // Allouer le buffer avec la taille obtenue
    pAddresses = (IP_ADAPTER_ADDRESSES*) malloc(ulOutBufLen);
    if (pAddresses == NULL) {
        printf("Erreur d'allocation de mémoire.\n");
        return NULL;
    }

    // Obtenir les informations des adaptateurs
    dwRetVal = GetAdaptersAddresses(AF_INET, GAA_FLAG_INCLUDE_PREFIX, NULL, pAddresses, &ulOutBufLen);
    
    if (dwRetVal == NO_ERROR) {
        // Parcourir la liste des adaptateurs
        pCurrAddresses = pAddresses;
        while (pCurrAddresses) {
            // Comparer le nom de l'interface avec celui recherché
            if (wcscmp(pCurrAddresses->FriendlyName, wInterfaceName) == 0) {
                interfaceTrouvee = 1;
                printf("\nInformations pour l'interface: %ls\n", pCurrAddresses->FriendlyName);
                // Obtenir les adresses unicast pour cet adaptateur
                pUnicast = pCurrAddresses->FirstUnicastAddress;
                if (pUnicast == NULL) {
                    printf("Aucune adresse IP trouvée pour cette interface.\n");
                }
                
                while (pUnicast != NULL) {
                    // Obtenir l'adresse IP
                    ip[INET_ADDRSTRLEN];
                    struct sockaddr_in* sockaddr = (struct sockaddr_in*)pUnicast->Address.lpSockaddr;
                    inet_ntop(AF_INET, &(sockaddr->sin_addr), ip, INET_ADDRSTRLEN);
                    pUnicast = pUnicast->Next;
                }
                
                // Une fois trouvée, on peut sortir de la boucle
                break;
            }
            
            pCurrAddresses = pCurrAddresses->Next;
        }
        
        if (!interfaceTrouvee) {
            printf("Interface '%ls' non trouvée.\n", interface_name);
        }
    } else {
        printf("Erreur lors de l'appel à GetAdaptersAddresses: %d\n", dwRetVal);
    }
    
    // Libérer la mémoire
    if (pAddresses) {
        free(pAddresses);
    }
    
    #else
    // Implémentation Linux originale
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
    // this code is written by Christian Toinard : christian.toinard(at)insa-cvl.fr
    // #define Message "Bonjour de Christian Toinard"

    #ifdef _WIN32
    signal(SIGINT, (void (__cdecl *)(int))catch);
    #else
    typedef void (*sighandler_t)(int);
    signal(SIGINT, (sighandler_t)catch);
    #endif

    #ifdef _WIN32
    // Implémentation Windows du broadcast
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
    // Implémentation Linux originale
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