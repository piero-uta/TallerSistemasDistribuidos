
import pygame

# Inicializar
pygame.init()

# Medidas
ANCHO = 636
ALTO = 636

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)

# Ventana
ventana = pygame.display.set_mode((ANCHO, ALTO))
background = pygame.image.load("sprites/8860eab3-3682-404c-a830-e5a20b0cdc7a.png")
# Datos
pos_x = 65
pos_y = 45


# Bucle principal

jugando = True
while jugando:

    # Eventos

    for event in pygame.event.get():
        #print(event)
        if event.type == pygame.QUIT:
            jugando = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                jugando = False
                #PREISONAR FLECHA HACIA ABAJO PARA SOLTAR UNA FICHA
            elif event.key == pygame.K_DOWN:
                while pos_y < ALTO-75 :
                    ventana.blit(background,[0,0])
                    ventana.fill(NEGRO)
                    pygame.draw.circle(ventana, VERDE, (pos_x, pos_y),35)
                    pos_y += 10
                    ventana.blit(background,[0,0])
                    pygame.display.update()
                    
                    
                    
    # Lógica


    # Dibujosventana.fill(NEGRO)
    ventana.blit(background,[0,0])
    # Actualizar
    pygame.display.update()
    pos_y=70;
    


# Salir
pygame.quit()


