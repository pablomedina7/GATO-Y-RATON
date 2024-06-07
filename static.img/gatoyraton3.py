import pygame #juegos 
import numpy as np  #matrices y operaciones numericas 
import random  # random en este caso se utiliza para las aleatoriedades 
import heapq    # esta biblioteca se utiliza para manejas las colas de propiedad 
#dimensiones 
TABLERO_TAMANIO = 9
TAMANIO_CELDA = 70
ANCHO_VENTANA = TABLERO_TAMANIO * TAMANIO_CELDA
ALTO_VENTANA = TABLERO_TAMANIO * TAMANIO_CELDA
# Colores       R   G    B
COLOR_FONDO = ( 0,  0 ,  0 )
COLOR_LINEA = ( 255,255, 255)
# Inicializamos el tablero
tablero = np.zeros((TABLERO_TAMANIO, TABLERO_TAMANIO))
# Se utiliza numpy para crear una matriz de ceros 
gato_pos = (0, 0)
raton_pos = (4, 4)
# Esta matriz se usa para almacenar las posiciones.
# Posiciones iniciales de los jugadores, en este caso el gato y el ratón. 
tablero[gato_pos] = 1  # 1 representa al Gato
tablero[raton_pos] = 2  # 2 representa al Ratón

# Para evitar movimientos repetidos
# Aquí se guardan los movientos para evitar en lo posible que sean repetidos 
movimientos_previos = set() 

def generar_destino(raton_pos, min_distancia):
    while True:
        destino = (random.randint(0, TABLERO_TAMANIO - 1), random.randint(0, TABLERO_TAMANIO - 1))
        distancia = np.sum(np.abs(np.array(destino) - np.array(raton_pos)))
        # La heurística del A* usa numpy para calcular la distancia de Manhattan entre dos puntos, 
        # lo que ayuda a determinar el costo de mover desde una posición a otra en el tablero.

        if distancia >= min_distancia:
            return destino
destino = generar_destino(raton_pos, 4)

# Función para Mover Jugadores
def mover_jugador(tablero, posicion_actual, nueva_posicion):
    if (0 <= nueva_posicion[0] < TABLERO_TAMANIO) and (0 <= nueva_posicion[1] < TABLERO_TAMANIO):
        jugador = tablero[posicion_actual]
        tablero[posicion_actual] = 0
        tablero[nueva_posicion] = jugador
        return nueva_posicion
    else:
        return posicion_actual
    
# Función para Evaluar el Tablero

def evaluar(tablero):
    gato_pos = np.argwhere(tablero == 1)
    raton_pos = np.argwhere(tablero == 2)
    
    if len(gato_pos) == 0 or len(raton_pos) == 0:
        return 0

    gato_pos = gato_pos[0]
    raton_pos = raton_pos[0]
    distancia = np.sum(np.abs(gato_pos - raton_pos))

    return -distancia  # Queremos minimizar la distancia para el Gato
# Función Minimax
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
        mejor_valor = np.inf #INFERIOR buscar xq min en min 
        movimientos = generar_movimientos(tablero, 2, movimientos_previos)
        for movimiento in movimientos:
            valor = minimax(movimiento, profundidad - 1, True, movimientos_previos)
            mejor_valor = min(mejor_valor, valor)
        return mejor_valor
    
# Generar Movimientos

def generar_movimientos(tablero, jugador, movimientos_previos):
    movimientos = []
    posicion_actual = np.argwhere(tablero == jugador)
    
    if len(posicion_actual) == 0:
        return movimientos
    
    posicion_actual = posicion_actual[0]
    posibles_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    
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
# Algoritmo A* para el Ratón

def a_star(tablero, inicio, destino):
    def heuristic(a, b):
        return np.sum(np.abs(np.array(a) - np.array(b)))

    posibles_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    cola = []
    heapq.heappush(cola, (0 + heuristic(inicio, destino), 0, inicio, None))
    visitados = set()
    came_from = {}
    
    while cola:
        _, costo, actual, anterior = heapq.heappop(cola)
        
        if actual in visitados:
            continue
        
        visitados.add(actual)
        came_from[actual] = anterior
        
        if actual == destino:
            break
        
        for movimiento in posibles_movimientos:
            vecino = (actual[0] + movimiento[0], actual[1] + movimiento[1])
            if 0 <= vecino[0] < TABLERO_TAMANIO and 0 <= vecino[1] < TABLERO_TAMANIO and vecino not in visitados:
                if tablero[vecino[0], vecino[1]] == 0 or tablero[vecino[0], vecino[1]] == 2:
                    heapq.heappush(cola, (costo + 1 + heuristic(vecino, destino), costo + 1, vecino, actual))
    
    # Reconstruir el camino
    camino = []
    actual = destino
    while actual:
        camino.append(actual)
        actual = came_from[actual]
    camino.reverse()
    return camino

# Comprueba si el juego ha terminado (el gato ha atrapado al ratón o el ratón ha llegado al destino).
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
# Función dibujar_destino:
# Dibuja la imagen del destino en la posición correspondiente del tablero.
def dibujar_destino(pantalla, imagen_destino, destino):
    destino_rect = pygame.Rect(destino[1] * TAMANIO_CELDA, destino[0] * TAMANIO_CELDA, TAMANIO_CELDA, TAMANIO_CELDA)
    pantalla.blit(imagen_destino, destino_rect.topleft)

# Función Principal del Juego
def jugar():
    global gato_pos, raton_pos
    turno_gato = True
    profundidad = 3

    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Juego del Gato y el Ratón")
    reloj = pygame.time.Clock()

    imagen_gato = pygame.image.load('static.img/ENCONTRADO 9.jpg')
    imagen_raton = pygame.image.load('static.img/raton.webp')
    imagen_destino = pygame.image.load('static.img/PUERTA.jpeg')
    imagen_gato = pygame.transform.scale(imagen_gato, (TAMANIO_CELDA, TAMANIO_CELDA))
    imagen_raton = pygame.transform.scale(imagen_raton, (TAMANIO_CELDA, TAMANIO_CELDA))
    imagen_destino = pygame.transform.scale(imagen_destino, (TAMANIO_CELDA, TAMANIO_CELDA))
    pygame.mixer.music.load('AC-DC - Back In Black (Official 4K Video).mp3')
    pygame.mixer.music.play(-1)  # -1 hace que la música se reproduzca en bucle

    corriendo = True
    while corriendo and not juego_terminado(tablero):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
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

        dibujar_destino(pantalla, imagen_destino, destino)

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
            camino = a_star(tablero, tuple(raton_pos), destino)
            if len(camino) > 1:
                nueva_posicion = camino[1]
                tablero[raton_pos[0], raton_pos[1]] = 0
                raton_pos = nueva_posicion
                tablero[raton_pos[0], raton_pos[1]] = 2
            movimientos_previos.add(tuple(map(tuple, tablero)))

        turno_gato = not turno_gato
        reloj.tick(0.5)  # Controla la velocidad del juego

    # Mostrar el resultado final
    pantalla.fill(COLOR_FONDO)
    if len(gato_pos) == 0 or len(raton_pos) == 0:
        mensaje = "Error en la posición de los jugadores."
    else:
        if np.array_equal(raton_pos, destino):
            mensaje = "El Ratón RAJÓ!"
        else:
            mensaje = "El Gato ha atrapado al Ratón!"
    
    fuente = pygame.font.Font(None, 40)
    texto = fuente.render(mensaje, True, (255, 0 , 0))
    pantalla.blit(texto, (10, ALTO_VENTANA // 2 - 37))
    pygame.display.flip()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == "__main__":
    jugar()
