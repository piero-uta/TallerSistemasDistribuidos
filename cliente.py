import socket
import pickle
import pygame 
import sys
import time

pygame.init()
pygame.display.set_caption("El gato!!")
 

HEADERSIZE = 10
conectado = False
s =socket.socket()
empezarJuego=False
board = []
FONT = pygame.font.Font("assets/Roboto-Regular.ttf", 32)
COLOR_TEXTO = (6, 26, 64)


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

def verificar_ganador():
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != "":
            ganador = board[i][0]
            #actualizar graphical_board
            for j in range(3):
                graphical_board[i][j][0] = pygame.image.load(f"assets/Winning {ganador}.png")
                        

            return ganador
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != "":
            ganador = board[0][i]
            #actualizar graphical_board
            for j in range(3):
                graphical_board[j][i][0] = pygame.image.load(f"assets/Winning {ganador}.png")
            return ganador 
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != "":
        ganador = board[0][0]
        #actualizar graphical_board
        for i in range(3):
            graphical_board[i][i][0] = pygame.image.load(f"assets/Winning {ganador}.png")
        return ganador
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != "":
        ganador = board[0][2]
        #actualizar graphical_board
        for i in range(3):
            graphical_board[i][2-i][0] = pygame.image.load(f"assets/Winning {ganador}.png")
        return ganador
    return ""
    
def crear_board():
    for i in range(3):
        board.append([])
        for j in range(3):
            board[i].append("")
   
def reiniciar_board():
    for i in range(3):
        for j in range(3):
            board[i][j] = ""

crear_board()

WIDTH, HEIGHT = 900, 900
 
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe!")

BOARD = pygame.image.load("assets/Board.png")
X_IMG = pygame.image.load("assets/X.png")
O_IMG = pygame.image.load("assets/O.png")

BG_COLOR = (214, 201, 227)


graphical_board = [[[None, None], [None, None], [None, None]], 
                    [[None, None], [None, None], [None, None]], 
                    [[None, None], [None, None], [None, None]]]

SCREEN.fill(BG_COLOR)
SCREEN.blit(BOARD, (64, 64))

pygame.display.update()

def render_board(board, ximg, oimg):
    global graphical_board
    for i in range(3):
        for j in range(3):
            if board[i][j] == "X":
                # Create an X image and rect
                graphical_board[i][j][0] = ximg
                graphical_board[i][j][1] = ximg.get_rect(center=(j*300+150, i*300+150))
            elif board[i][j] == "O":
                graphical_board[i][j][0] = oimg
                graphical_board[i][j][1] = oimg.get_rect(center=(j*300+150, i*300+150))
    for i in range(3):
        for j in range(3):
            if graphical_board[i][j][0] is not None:
                SCREEN.blit(graphical_board[i][j][0], graphical_board[i][j][1])

def registrar_click():
    current_pos = pygame.mouse.get_pos()
    converted_x = (current_pos[0]-65)/835*2
    converted_y = current_pos[1]/835*2
    return [converted_x, converted_y]


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
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
            #verificar si alguien gano
            ganador = verificar_ganador()
            if ganador != "":
                reiniciar_board()
                #reiniciar graphical_board
                for i in range(3):
                    for j in range(3):
                        graphical_board[i][j][0] = None
                        graphical_board[i][j][1] = None

                
                time.sleep(2)
                print("gano", ganador)
                if ganador == "X":
                    ganadorText = FONT.render("Ganaste!!", True, COLOR_TEXTO, BG_COLOR)
                else:
                    ganadorText = FONT.render("Perdiste!!", True, COLOR_TEXTO, BG_COLOR)
                textRect = ganadorText.get_rect()
                textRect.center = (WIDTH // 2, HEIGHT//2)
                SCREEN.blit(ganadorText, textRect)
                #esperar 3 segundos
                pygame.display.update()
                time.sleep(3)
                SCREEN.fill(BG_COLOR)
                SCREEN.blit(BOARD, (64, 64))
                pygame.display.update()

            try:
                recibir = enviar_mensaje({"opcion": "jugando"}, s)
                
            except:
                print("error en recibir resultado")
                conectado = False
                s.close()

            if recibir == "turno":
                print("Es tu turno")
                ingresandoInput = True
                while ingresandoInput:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = registrar_click()
                            pos[0]=round(pos[0])
                            pos[1]=round(pos[1])
                            if pos[0] < 0 or pos[0] > 2 or pos[1] < 0 or pos[1] > 2:
                                print("Posicion invalida")
                                continue
                            if board[int(pos[1])][int(pos[0])] != "":
                                print("Posicion ocupada")
                                continue                            
                            board[int(pos[1])][int(pos[0])] = "X"
                            render_board(board, X_IMG, O_IMG)
                            pygame.display.update()
                            ingresandoInput = False
                            break
                try:
                    recibir = enviar_mensaje({"opcion":"movimiento","movimiento":pos}, s)
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
                print(recibir)
                #actualizar board con x e y
                x = int(recibir["movimiento"][1])
                y = int(recibir["movimiento"][0])
                board[x][y] = "O"
                render_board(board, X_IMG, O_IMG)
                pygame.display.update()

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
        
