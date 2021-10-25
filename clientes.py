import socket
import time
from threading import Thread,Semaphore
import timeit

semaforo = Semaphore(1)

n = 5 #NUMERO DE CLIENTES
clientes= []

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

#############################################################################################################################

def doSutff(id, udpcsocket, i, msg, sap, bfsz): #region critica, aqui se realiza la comunicacion con el servidor
    perdidas = 0
    envios = 0
    while True:
        try:  ## SI ES CORRUPTO Y NO LLEGA ACK O EL ACK NO LLEGA A TIEMPO O EL ACK NO COINCIDE CON EL ESPERADO -> OCURRE UN TIMEOUT Y SE REENVIA EL PAQUETE
            udpcsocket.sendto(str.encode(msg), sap) #se envia letra del nombre y direccion
            envios += 1
            while True:
                msgFromServer = udpcsocket.recvfrom(bfsz) # se recibe la confirmacion del mensaje
                msg2 = "ACK: " + (format(msgFromServer[0]))[2] #se decodifica
                #print(msg2) #se imprime la confirmacion en el bash
                if int(msg2[5]) == i: #mientras no se reciba el ack correcto, se seguira en escucha hasta que ocurra un timeout, en caso contrario se sale del loop
                    break
                print(bcolors.FAIL + "Cliente " + str(id) + " recibio ACK Incorrecto" + bcolors.ENDC)
        except socket.timeout:
            perdidas += 1 
            print(bcolors.FAIL + "Cliente " + str(id) + " Sin confirmación, reenviando [Timeout 2s]" + bcolors.ENDC) # si no hay confirmacion imprimimos el error en el bash
            continue #si pasan los 2000ms se reenvia de nuevo el mensaje -> vuelve al try
        else:
            print(bcolors.OKGREEN + "Cliente " + str(id) + " mensaje enviado!" + bcolors.ENDC)
            break #si ahora llega la confirmacion no entra al except y tiene el index correcto -> pasamos al siguiente caracter
    return (envios, perdidas)
        
#############################################################################################################################

class Cliente(Thread):
    def __init__(self,id): #Constructor de la clase
        Thread.__init__(self)
        self.id=id
    def run(self): #Metodo que se ejecutara con la llamada start
        start = timeit.default_timer()
        enviados = 0
        perdidos = 0
        ##########################################################################
        serverAddressPort   = ("127.0.0.1", 20001)
        bufferSize          = 1024
        # ENVIANDO EL NOMBRE
        name = ['F','R', 'A', 'N', 'C', 'O']
        index = 0 # vamos a usar un sistema de 2 bits
        # Create a UDP socket at client side
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # configuramos un tiempo maximo para timeout de 2000ms
        UDPClientSocket.settimeout(2)
        for i in name: #recorremos el nombre a enviar caracter por caracter
            print("Cliente " + str(self.id) + " Esta Intentando enviar")
            #añadimos una cabecera al mensaje
            if index >= 2:
                index = 0
            msg = str(self.id) + str(index) + i
            semaforo.acquire()
            e, p = doSutff(self.id, UDPClientSocket, index, msg, serverAddressPort, bufferSize) # region critica, para no saturar la cola se han usado semaforos para indicar cuando el servidor esta ocupado
            semaforo.release()
            enviados += e #metrica de perdida de paquetes x cliente
            perdidos += p
            index += 1 #de 0 pasamos a 1 y de 1 a 2
        #metricas de tiempo de envio y perdida
        stop = timeit.default_timer()
        tiempo = stop-start
        t = "%.1f" % tiempo
        tasa = (perdidos/enviados) * 100
        rate = "%.2f" % tasa
        print(bcolors.WARNING + "A Cliente " + str(self.id) + " le tomo: " + t + " segundos enviar su mensaje con una tasa de perdida del " + rate + "%" + bcolors.ENDC)

        ##########################################################################

#############################################################################################################################

#inicializacion de clientes

for x in range(n):
    clientes.append(Cliente(x+1))

for c in clientes: 
     c.start()