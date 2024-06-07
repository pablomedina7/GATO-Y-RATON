import pygame
import numpy as np
import random

# Dimensiones del tablero
TABLERO_TAMANIO = 7
TAMANIO_CELDA = 70 
ANCHO_VENTANA = TABLERO_TAMANIO * TAMANIO_CELDA
ALTO_VENTANA = TABLERO_TAMANIO * TAMANIO_CELDA

# Colores
COLOR_FONDO = (0, 0, 0)
COLOR_LINEA = (255,255, 255)
COLOR_DESTINO = (0, 255, 0)

# Inicializamos el tablero
tablero = np.zeros((TABLERO_TAMANIO, TABLERO_TAMANIO))

# Posiciones iniciales
gato_pos = (0, 0)
raton_pos = (4, 4)

# Definir las posiciones iniciales en el tablero
tablero[gato_pos] = 1  # 1 representa al Gato
tablero[raton_pos] = 2  # 2 representa al Ratón

# Para evitar movimientos repetidos
movimientos_previos = set()

# Generar destino para el ratón
def generar_destino(raton_pos, min_distancia):
    while True:
        destino = (random.randint(0, TABLERO_TAMANIO - 1), random.randint(0, TABLERO_TAMANIO - 1))
        distancia = np.sum(np.abs(np.array(destino) - np.array(raton_pos)))
        if distancia >= min_distancia:
            return destino

destino = generar_destino(raton_pos, 4)

def mover_jugador(tablero, posicion_actual, nueva_posicion):
    if (0 <= nueva_posicion[0] < TABLERO_TAMANIO) and (0 <= nueva_posicion[1] < TABLERO_TAMANIO):
        jugador = tablero[posicion_actual]
        tablero[posicion_actual] = 0
        tablero[nueva_posicion] = jugador
        return nueva_posicion
    else:
        return posicion_actual

def evaluar(tablero):
    gato_pos = np.argwhere(tablero == 1)
    raton_pos = np.argwhere(tablero == 2)
    
    if len(gato_pos) == 0 or len(raton_pos) == 0:
        return 0

    gato_pos = gato_pos[0]
    raton_pos = raton_pos[0]
    distancia = np.sum(np.abs(gato_pos - raton_pos))
    return -distancia  # Queremos minimizar la distancia para el Gato

def minimax(tablero, profundidad, maximizando, movimientos_previos):
    if profundidad == 0 or juego_terminado(tablero):
        return evaluar(tablero)
    
    if maximizando:
        mejor_valor = -np.inf
        movimientos = generar_movimientos(tablero, 1, movimientos_previos)
        for movimiento in movimientos:
            valor = minimax(movimiento, profundidad - 1, False, movimientos_previos)
            mejor_valor = max(mejor_valor, valor)
        return mejor_valor
    else:
        mejor_valor = np.inf
        movimientos = generar_movimientos(tablero, 2, movimientos_previos)
        for movimiento in movimientos:
            valor = minimax(movimiento, profundidad - 1, True, movimientos_previos)
            mejor_valor = min(mejor_valor, valor)
        return mejor_valor

def generar_movimientos(tablero, jugador, movimientos_previos):
    movimientos = []
    posicion_actual = np.argwhere(tablero == jugador)
    
    if len(posicion_actual) == 0:
        return movimientos
    
    posicion_actual = posicion_actual[0]
    if jugador == 1:  # Movimientos del gato (incluyendo diagonales)
        posibles_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    else:  # Movimientos del ratón (no diagonales)
        posibles_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for movimiento in posibles_movimientos:
        nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
        if (0 <= nueva_posicion[0] < TABLERO_TAMANIO) and (0 <= nueva_posicion[1] < TABLERO_TAMANIO):
            nuevo_tablero = tablero.copy()
            nuevo_tablero[posicion_actual[0], posicion_actual[1]] = 0
            nuevo_tablero[nueva_posicion[0], nueva_posicion[1]] = jugador
            # Verificar si el movimiento ya se ha realizado anteriormente
            if tuple(map(tuple, nuevo_tablero)) not in movimientos_previos:
                movimientos.append(nuevo_tablero)
    return movimientos

def juego_terminado(tablero):
    gato_pos = np.argwhere(tablero == 1)
    raton_pos = np.argwhere(tablero == 2)
    if len(gato_pos) == 0 or len(raton_pos) == 0:
        return True
    gato_pos = gato_pos[0]
    raton_pos = raton_pos[0]
    if np.array_equal(gato_pos, raton_pos):
        return True
    if np.array_equal(raton_pos, destino):
        return True
    return False

def dibujar_destino(pantalla, destino):
    destino_rect = pygame.Rect(destino[1] * TAMANIO_CELDA, destino[0] * TAMANIO_CELDA, TAMANIO_CELDA, TAMANIO_CELDA)
    pygame.draw.rect(pantalla, COLOR_DESTINO, destino_rect)

def jugar():
    global gato_pos, raton_pos
    turno_gato = True
    profundidad = 4

    # Inicializar pygame
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Juego del Gato y el Ratón")
    reloj = pygame.time.Clock()

    # Cargar las imágenes de los GIFs
    imagen_gato = pygame.image.load('static.img/ENCONTRADO 9.jpg').convert_alpha()
    imagen_gato = pygame.transform.scale(imagen_gato, (TAMANIO_CELDA, TAMANIO_CELDA))

    imagen_raton = pygame.image.load('static.img/raton.webp').convert_alpha()
    imagen_raton = pygame.transform.scale(imagen_raton, (TAMANIO_CELDA, TAMANIO_CELDA))

    corriendo = True
    while corriendo and not juego_terminado(tablero):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        pantalla.fill(COLOR_FONDO)

        # Dibujar el tablero
        for x in range(TABLERO_TAMANIO):
            for y in range(TABLERO_TAMANIO):
                rect = pygame.Rect(y * TAMANIO_CELDA, x * TAMANIO_CELDA, TAMANIO_CELDA, TAMANIO_CELDA)
                pygame.draw.rect(pantalla, COLOR_LINEA, rect, 1)
                if tablero[x, y] == 1:
                    pantalla.blit(imagen_gato, rect.topleft)
                elif tablero[x, y] == 2:
                    pantalla.blit(imagen_raton, rect.topleft)
        
        # Dibujar el destino
        dibujar_destino(pantalla, destino)

        pygame.display.flip()

        if turno_gato:
            mejor_valor = -np.inf
            mejor_movimiento = None
            movimientos = generar_movimientos(tablero, 1, movimientos_previos)
            for movimiento in movimientos:
                valor = minimax(movimiento, profundidad, False, movimientos_previos)
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = movimiento
            if mejor_movimiento is not None:
                movimientos_previos.add(tuple(map(tuple, mejor_movimiento)))
                tablero[:] = mejor_movimiento
                gato_pos = np.argwhere(tablero == 1)[0]
        else:
            mejor_valor = np.inf
            mejor_movimiento = None
            movimientos = generar_movimientos(tablero, 2, movimientos_previos)
            for movimiento in movimientos:
                valor = minimax(movimiento, profundidad, True, movimientos_previos)
                if valor < mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = movimiento
            if mejor_movimiento is not None:
                movimientos_previos.add(tuple(map(tuple, mejor_movimiento)))
                tablero[:] = mejor_movimiento
                raton_pos = np.argwhere(tablero == 2)[0]

        turno_gato = not turno_gato
        reloj.tick(2)  # Controla la velocidad del juego

    # Mostrar el resultado final
    pantalla.fill(COLOR_FONDO)
    if len(gato_pos) == 0 or len(raton_pos) == 0:
        mensaje = "Error en la posición de los jugadores."
    else:
        if np.array_equal(raton_pos, destino):
            mensaje = "El Ratón ha alcanzado su destino y ha escapado!"
        else:
            mensaje = "El Gato ha atrapado al Ratón!"
    
    fuente = pygame.font.Font(None, 50)
    texto = fuente.render(mensaje, True, (255, 0, 0))
    pantalla.blit(texto, (20, ALTO_VENTANA // 2 - 37))
    pygame.display.flip()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == "__main__":
    jugar()
