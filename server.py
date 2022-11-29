import socket
import _thread
import pickle


HEADERSIZE = 10

CANTIDADLOBBY = 10
HEADERSIZE = 10

ncliente=0

lobbies = []

#crear el diccionario con los datos del lobby vacios
socketJugador=socket.socket()

print(socketJugador)

for i in range(CANTIDADLOBBY):
    lobbies.append({"jugador1": socketJugador, "jugador2": socketJugador})

usuariosEnLobby = []
for i in range(CANTIDADLOBBY):
    usuariosEnLobby.append(0)

#crear socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 5555))
s.listen(5)

def recibir_mensaje(conn):
    full_msg = b''
    new_msg = True
    while True:
        try:
            msg = conn.recv(16)
        except:
            print("error en recibir mensaje")
            break
        if new_msg:
            print("nuevo mensaje:",msg[:HEADERSIZE])
            msglen = int(msg[:HEADERSIZE])
            new_msg = False

        print(f"tamaño completo del mensaje: {msglen}")

        full_msg += msg

        print(len(full_msg))

        if len(full_msg)-HEADERSIZE == msglen:
            mensaje = pickle.loads(full_msg[HEADERSIZE:])
            print(mensaje)
            return mensaje

def enviar_mensaje(mensaje, conn):
    mensaje = pickle.dumps(mensaje)
    mensaje = bytes(f'{len(mensaje):<{HEADERSIZE}}', "utf-8") + mensaje
    conn.send(mensaje)

#funcion hilo cliente
def hilo_cliente(conn, ncliente):
    lobby=-1
    jugador="no hay jugador"
    njugador=0
    conectado = False
    while True:
        #verificar conexion
        try:
            recibir = recibir_mensaje(conn)
        except:
            print("error en recibir mensaje")
            break

        if conectado == False:
            if recibir["opcion"] == "refrescar":
                enviar_mensaje(usuariosEnLobby, conn)
                conn.close()
                print("conexion cerrada por refrescar")
                break            
            elif recibir["opcion"] == "conectar":
                lobby=int(recibir["lobby"])-1
                jugador = conn
                if lobbies[lobby]["jugador1"] == socketJugador:
                    print("jugador1")
                    usuariosEnLobby[lobby]+=1
                    njugador=1
                    lobbies[lobby]["jugador1"] = conn
                    conectado = True
                elif lobbies[lobby]["jugador2"] == socketJugador:
                    print("jugador2")
                    usuariosEnLobby[lobby]+=1
                    njugador=2
                    lobbies[lobby]["jugador2"] = conn
                    conectado = True
                else:
                    enviar_mensaje("lobby lleno", conn)
                    conn.close()
                    print("lobby lleno")
                    break 
                enviar_mensaje("conectado", conn)
        else:
            print(recibir)
            #reenviar a todos los jugadores del lobby            
            if njugador == 1:
                #verificar si el jugador 2 esta conectado
                if lobbies[lobby]["jugador2"] != socketJugador:
                    print(lobbies[lobby]["jugador2"])
                    enviar_mensaje(recibir, lobbies[lobby]["jugador2"])
                #confirmar a jugador
                enviar_mensaje("confirmar", conn)
            elif njugador == 2:
                #verificar si el jugador 1 esta conectado
                if lobbies[lobby]["jugador1"] != socketJugador:
                    print(lobbies[lobby]["jugador1"])
                    enviar_mensaje(recibir, lobbies[lobby]["jugador1"])
                enviar_mensaje("confirmar", conn)
            else:
                print("error en enviar mensaje")
            
    if lobby != -1:
        if jugador == socketJugador:
            print("error en el jugador")
        else:
            if njugador == 1:
                usuariosEnLobby[lobby]-=1
                lobbies[lobby]["jugador1"] = socketJugador
            elif njugador == 2:
                usuariosEnLobby[lobby]-=1
                lobbies[lobby]["jugador2"] = socketJugador

    print("conexion cerrada")
    

ncliente = 0

while True:
    #recibe una conexion
    clientsocket, address = s.accept()
    print(f"Conexion de {address} establecida.")
    print(clientsocket)
    ncliente += 1
    #crea un hilo para el cliente
    _thread.start_new_thread(hilo_cliente, (clientsocket, ncliente))
    



    
    