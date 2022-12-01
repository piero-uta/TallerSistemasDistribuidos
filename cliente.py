import socket
import pickle
import sys
import select

HEADERSIZE = 10




#funcion recibir mensajes
def recibir_mensaje(conn):
    full_msg = b''
    new_msg = True
    while True:
        msg = conn.recv(16)
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
    return recibir_mensaje(conn)

def refrescar_lobbies():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 5000))
    enviar = {"opcion": "refrescar"}
    lobbies = enviar_mensaje(enviar, s)
    print("N lobbby| usuarios")
    for i in range(len(lobbies)):
        print(i+1, lobbies[i],"/", 2)
    s.close()


conectado = False
s =socket.socket()
empezarJuego=False

while True:
    if conectado == False:
        opcion = input("Elije opcion: (-1 salir, 0 refrescar, 1 conectar a lobby): ")
        if opcion == "-1":
            break
        elif opcion == "0":
            refrescar_lobbies()
        elif opcion == "1":
            lobby = input("Elije lobby: ")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((socket.gethostname(), 5000))
            enviar = {"opcion": "conectar", "lobby": lobby}
            try:                 
                recibir = enviar_mensaje(enviar, s)                
            except:
                print("error en conectar")
                s.close()
                continue

            print("conectado")
            if recibir == "lobby lleno":
                print("lobby lleno")
            else:
                print("conectado")
                conectado = True
                print("esperando a otro jugador")
    else:
        if empezarJuego == False:
            try:
                recibir = enviar_mensaje({"opcion": "esperandoJuego"}, s)              
            except:
                print("error el recibir empezar juego") 
                conectado = False
                s.close()
            if recibir == "empezar":
                    print("Comienza juego")
                    empezarJuego=True
        else:
            try:
                recibir = enviar_mensaje({"opcion": "jugando"}, s)
                
            except:
                print("error en recibir resultado")
                conectado = False
                s.close()

            if recibir == "turno":
                print("Es tu turno")
                movimiento = input("Elije movimiento: ")
                try:
                    recibir = enviar_mensaje({"opcion":"movimiento","movimiento":movimiento}, s)
                except:
                    print("error en enviar movimiento")
                    conectado = False
                    empezarJuego=True
                    s.close()
            elif recibir == "esperar":
                print("Esperando a otro jugador")
                try:
                    recibir = enviar_mensaje({"opcion":"esperandoJugador"}, s)                       
                except:
                    print("error en recibir movimiento")
                    conectado = False
                    empezarJuego=True
                    s.close()
                print("El otro jugador hizo", recibir["movimiento"])
            elif recibir == "ganaste":
                print("ganaste")
                conectado = False
                s.close()
            elif recibir == "perdiste":
                print("perdiste")
                conectado = False
                s.close()
            elif recibir == "empate":
                print("empate")
                conectado = False
                s.close()

