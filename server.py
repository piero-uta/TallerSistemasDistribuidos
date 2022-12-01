import socket
import _thread
import pickle
import random

HEADERSIZE = 10

CANTIDADLOBBY = 10
HEADERSIZE = 10

lobbies = []
#crear el diccionario con los datos del lobby vacios
SOCKETVACIO=socket.socket()

for i in range(CANTIDADLOBBY):
    lobbies.append({"turno":random.randint(1,2),"jugador1": SOCKETVACIO, "jugador2": SOCKETVACIO})

usuariosEnLobby = []
for i in range(CANTIDADLOBBY):
    usuariosEnLobby.append(0)


#crear socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((socket.gethostname(), 5000))
s.listen(CANTIDADLOBBY*2)


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

        #print(f"tamaño completo del mensaje: {msglen}")

        full_msg += msg

        print(len(full_msg))

        if len(full_msg)-HEADERSIZE == msglen:
            mensaje = pickle.loads(full_msg[HEADERSIZE:])
            print(mensaje)
            return mensaje
    raise Exception("error en recibir mensaje")

def enviar_mensaje(mensaje, conn):
    mensaje = pickle.dumps(mensaje)
    mensaje = bytes(f'{len(mensaje):<{HEADERSIZE}}', "utf-8") + mensaje
    conn.send(mensaje)

def hilo_cliente(conn,):
    conectado = False
    njugador = 0
    #lobby del cliente
    lobby = 0
    jugando = False

    while True:
        if conectado == False:
            try:
                recibir = recibir_mensaje(conn)
            except:
                print("error en recibir mensaje")
                conn.close()
                return
            if recibir["opcion"] == "refrescar":
                enviar_mensaje(usuariosEnLobby, conn)
                conn.close()
                print("conexion cerrada por refrescar")
                return
            elif recibir["opcion"] == "conectar":  
                lobby=int(recibir["lobby"])-1
                if lobbies[lobby]["jugador1"] == SOCKETVACIO:
                    print("jugador 1, lobby:"+ str(lobby) + " es: " + str(conn))
                    usuariosEnLobby[lobby]+=1
                    lobbies[lobby]["jugador1"] = conn
                    enviar_mensaje("conectado", conn)
                    lobbyJugador = lobby
                    njugador = 1
                    conectado = True
                elif lobbies[lobby]["jugador2"] == SOCKETVACIO:
                    print("jugador 2, lobby:"+ str(lobby) + " es: " + str(conn))
                    usuariosEnLobby[lobby]+=1
                    lobbies[lobby]["jugador2"] = conn
                    enviar_mensaje("conectado", conn)
                    lobbyJugador = lobby
                    njugador = 2
                    conectado = True
                else:
                    enviar_mensaje("lobby lleno", conn)
                    conn.close()
                    print("lobby lleno")
                    return
        else:
            if jugando == False:
                try:
                    recibir = recibir_mensaje(conn)
                except:
                    print("error en recibir mensaje")
                    conn.close()
                    return
                if recibir["opcion"] == "esperandoJuego":         
                    if lobbies[lobby]["jugador1"] != SOCKETVACIO and lobbies[lobby]["jugador2"] != SOCKETVACIO:
                        jugando = True
                        print("comenzar juego lobby", lobby)
                        enviar_mensaje("empezar", conn)
                    else:
                        enviar_mensaje("esperandoOtroJugador", conn)
            else:
                try:
                    recibir = recibir_mensaje(conn)
                except:
                    print("error en recibir mensaje")
                    if njugador == 1:
                        lobbies[lobbyJugador]["jugador1"] = SOCKETVACIO
                    else:
                        lobbies[lobbyJugador]["jugador2"] = SOCKETVACIO
                    usuariosEnLobby[lobbyJugador]-=1
                    conn.close()
                    return
                if recibir["opcion"] == "jugando":
                    if njugador == lobbies[lobbyJugador]["turno"]:
                        enviar_mensaje("turno", conn)
                        try:
                            recibir = recibir_mensaje(conn)
                        except:
                            print("error en recibir mensaje")
                            if njugador == 1:
                                lobbies[lobbyJugador]["jugador1"] = SOCKETVACIO
                            else:
                                lobbies[lobbyJugador]["jugador2"] = SOCKETVACIO
                            usuariosEnLobby[lobbyJugador]-=1                        
                            conn.close()
                            return
                        if recibir["opcion"] == "movimiento":
                            if njugador == 1:
                                enviar_mensaje("recibido", conn)
                                enviar_mensaje(recibir, lobbies[lobbyJugador]["jugador2"])
                            else:
                                enviar_mensaje("recibido", conn)
                                enviar_mensaje(recibir, lobbies[lobbyJugador]["jugador1"])
                            if lobbies[lobbyJugador]["turno"] == 1:
                                lobbies[lobbyJugador]["turno"] = 2
                            else:
                                lobbies[lobbyJugador]["turno"] = 1
                        elif recibir["opcion"] == "salir":
                            if njugador == 1:
                                lobbies[lobbyJugador]["jugador1"] = SOCKETVACIO
                            else:
                                lobbies[lobbyJugador]["jugador2"] = SOCKETVACIO
                            usuariosEnLobby[lobbyJugador]-=1
                            conn.close()
                            return
                    else:
                        try:
                            enviar_mensaje("esperar", conn)
                        except:
                            print("error en enviar mensaje")
                            if njugador == 1:
                                lobbies[lobbyJugador]["jugador1"] = SOCKETVACIO
                            else:
                                lobbies[lobbyJugador]["jugador2"] = SOCKETVACIO
                            usuariosEnLobby[lobbyJugador]-=1
                            conn.close()
                            return
                        recibir = recibir_mensaje(conn)
                else:
                    if njugador == 1:
                        lobbies[lobbyJugador]["jugador1"] = SOCKETVACIO
                    else:
                        lobbies[lobbyJugador]["jugador2"] = SOCKETVACIO
                    usuariosEnLobby[lobbyJugador]-=1
                    conn.close()
                    return


              

while True:
    conn, addr = s.accept()
    print(f"conexion de {addr} establecida")
    _thread.start_new_thread(hilo_cliente, (conn,))