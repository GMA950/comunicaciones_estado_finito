import socket
import time
import random
import timeit

localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print(bcolors.OKGREEN + "Link Available" + bcolors.ENDC)

perdidas = 0 #conteo de paquetes perdidos
exitosos = 0 #conteo de paquetes recibidos con exito
## DICCIONARIO DE HASTA N CLIENTES SIMULTANEOS 
buffer = {}   #{"address":"buffer"}
#MENSAJE FINAL X CLIENTE
mensajes = {"cliente":"mensaje"}

# Listen for incoming datagrams
while(True):
    ###############################
    # se recibe el mensaje mediante el socket, pero aun no se determina si el "servidor" lo recibe
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    ###############################
    print(bcolors.WARNING + "Link bussy" + bcolors.ENDC)
    ###############################
    #ESPERA 500ms <= t <= 3000ms
    t = random.randrange(5,30)/10
    #print(t)
    time.sleep(t)
    ###############################
    #SIMULACION ERROR 0.3 si el paquete esta corrupto o no "llega" simplemente no se envia confirmacion y se espera que el emisor envie nuevamente el paquete
    if random.random() > 0.3:
        clientMsg = format(message)
        #print(clientMsg)
        ################################
        #SI NO HAY BUFFER PREVIO PARA UN CLIENTE, SE AGREGA AL DICCIONARIO
        saddress = clientMsg[2]
        if not saddress in buffer:
            buffer[saddress] = ""
        ################################
        #DETECCION DE DUPLICADOS
        if clientMsg == buffer[saddress]:
            print(bcolors.FAIL + "DUPLICADO DETECTADO" + bcolors.ENDC) #enviamos nuevamente una confirmacion en caso de que se haya perdido el ack y se desecha el paquete
        else:
            buffer[saddress] = clientMsg    #guardamos el paquete de ese cliente en el diccionario del buffer
            #print(clientMsg[3])
            if not saddress in mensajes:
                mensajes[saddress] = clientMsg[4]
            else:
                mensajes[saddress] = mensajes[saddress] + clientMsg[4] #vamos guardando el mensaje
            print(mensajes)
            exitosos += 1 #metrica para tasa de perdidas
            #print(buffer)
        #########################################
        time.sleep(0.2)
        # Se envia el ack correspondiente
        bytesToSend = str.encode(clientMsg[3])
        UDPServerSocket.sendto(bytesToSend, address)
    else: #vamos contabilizando las perdidas de paquetes 
        perdidas += 1 #metrica para tasa de perdidas
        print(bcolors.FAIL + "Perdidas: " + str(perdidas) + bcolors.ENDC)

    ###########################################################
    print(bcolors.OKGREEN + "Link Available" + bcolors.ENDC)
    tasa = (perdidas/(perdidas+exitosos)) * 100
    rateloss = "%.1f" % tasa
    print("Tasa Perdidas segun servidor = " + rateloss + "%")
    ###########################################################