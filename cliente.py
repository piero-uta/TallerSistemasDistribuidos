import socket
import pickle

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

def refrescar_lobbies():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 5555))
    enviar = pickle.dumps({"opcion": "refrescar"})
    enviar = bytes(f'{len(enviar):<{HEADERSIZE}}', "utf-8") + enviar
    s.send(enviar)
    lobbies = recibir_mensaje(s)
    print("N lobbby| jugador1| jugador2")
    for i in range(len(lobbies)):
        print(i+1, lobbies[i],"/", 2)
    s.close()

def conectar_lobby(lobby):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 5555))
    enviar = {"opcion": "conectar", "lobby": lobby}
    enviar = pickle.dumps(enviar)
    enviar = bytes(f'{len(enviar):<{HEADERSIZE}}', "utf-8") + enviar
    s.send(enviar)
    mensaje = recibir_mensaje(s)
    print(mensaje)
    if mensaje == "lobby lleno":
        s.close()
        return False
    else:
        return s
    
def enviar_mensaje(mensaje, conn):
    mensaje = pickle.dumps(mensaje)
    mensaje = bytes(f'{len(mensaje):<{HEADERSIZE}}', "utf-8") + mensaje
    conn.send(mensaje)

while True:
    opcion = input("Elije opcion: (-1 salir, 0 refrescar, 1 conectar a lobby): ")
    if opcion == "-1":
        break
    elif opcion == "0":
        refrescar_lobbies()
    elif opcion == "1":
        lobby = input("Elije lobby: ")
        conn = conectar_lobby(lobby)
        if conn == False:
            print("Lobby lleno")
        else:
            print("Conectado")
            while True:
                mensaje = input("Mensaje: ")
                enviar_mensaje(mensaje, conn)
                mensaje = recibir_mensaje(conn)
                print(mensaje)
                
                
            
            
        
        
        
    