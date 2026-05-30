import pygame
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import random

TILE_SIZE = 15
COLS, ROWS = 240, 150
WIDTH, HEIGHT = (COLS // 3) * TILE_SIZE, (ROWS // 3) * TILE_SIZE

# Biomas (0: Agua, 1: Arena, 2: Hierba, 3: Roca)
COLORS = {
    0: (50, 150, 200),  # Azul (Agua)
    1: (210, 190, 130),  # Amarillo (Arena)
    2: (100, 200, 100),  # Verde (Hierba)
    3: (130, 130, 130)  # Gris (Roca)
}


def generar_mapa():
    num_seeds = 220
    nodos = np.column_stack((np.random.randint(0, COLS, num_seeds),
                             np.random.randint(0, ROWS, num_seeds)))
    bioma = np.random.randint(0, 4, num_seeds)

    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(nodos, bioma)

    # Predecimos la matriz completa
    xx, yy = np.meshgrid(np.arange(COLS), np.arange(ROWS))
    X_test = np.column_stack((xx.ravel(), yy.ravel()))
    Z = knn.predict(X_test)
    matriz = Z.reshape(ROWS, COLS)
    return matriz


class player:
    def __init__(self, px, py):
        self.x = px
        self.y = py
        self.inventory = {"Madera": 4, "Hierro": 0}

class zombie:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("KNN Survival")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    matriz = generar_mapa()
    mapas = []
    paso_COLS = COLS // 3  # 80
    paso_ROWS = ROWS // 3  # 50

    construir = False
    barco = False

    for i in range(3):
        for j in range(3):
            inicio_fila = i * paso_ROWS
            fin_fila = (i + 1) * paso_ROWS

            inicio_col = j * paso_COLS
            fin_col = (j + 1) * paso_COLS

            cuadrante = [fila[inicio_col:fin_col] for fila in matriz[inicio_fila:fin_fila]]
            mapas.append(cuadrante)

    px = random.randint(0, COLS - 1)
    py = random.randint(0, ROWS - 1)

    while matriz[py][px] == 0:
        px = random.randint(0, COLS - 1)
        py = random.randint(0, ROWS - 1)

    jugador = player(px, py)

    maderas = []
    cont_madera = 0
    cantidad_maderas = random.randint(7, 12)
    while cont_madera < cantidad_maderas:
        mx = random.randint(0, COLS - 1)
        my = random.randint(0, ROWS - 1)
        if matriz[my][mx] == 1 or matriz[my][mx] == 2:
            maderas.append({'x': mx, 'y': my})
            cont_madera += 1


    enemigos = []
    contador_enemigos = 0
    tiempo_enemigo = random.randint(30, 60)

    running = True
    while running:
        cuadrante_actual = 0

        # Dibujar Mapa
        # Calcular en qué cuadrante está el jugador
        if jugador.x < COLS // 3 and jugador.y < ROWS // 3:
            cuadrante_actual = 0
        elif jugador.x >= COLS // 3 and jugador.x < (COLS // 3) * 2 and jugador.y < ROWS // 3:
            cuadrante_actual = 1
        elif jugador.x >= (COLS // 3) * 2 and jugador.y < ROWS // 3:
            cuadrante_actual = 2
        elif jugador.x < COLS // 3 and jugador.y >= ROWS // 3 and jugador.y < (ROWS // 3) * 2:
            cuadrante_actual = 3
        elif jugador.x >= COLS // 3 and jugador.x < (COLS // 3) * 2 and jugador.y >= ROWS // 3 and jugador.y < (ROWS // 3) * 2:
            cuadrante_actual = 4
        elif jugador.x >= (COLS // 3) * 2 and jugador.y >= ROWS // 3 and jugador.y < (ROWS // 3) * 2:
            cuadrante_actual = 5
        elif jugador.x < COLS // 3 and jugador.y >= (ROWS // 3) * 2:
            cuadrante_actual = 6
        elif jugador.x >= COLS // 3 and jugador.x < (COLS // 3) * 2 and jugador.y >= (ROWS // 3) * 2:
            cuadrante_actual = 7
        elif jugador.x >= (COLS // 3) * 2 and jugador.y >= (ROWS // 3) * 2:
            cuadrante_actual = 8

        # Dibujar Mapa
        for y in range(ROWS // 3):
            for x in range(COLS // 3):
                pygame.draw.rect(screen, COLORS[mapas[cuadrante_actual][y][x]],(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Dibujar Maderas
        for madera in maderas:
            cuad_x = madera['x'] // paso_COLS
            cuad_y = madera['y'] // paso_ROWS
            cuadrante_madera = cuad_y * 3 + cuad_x

            if cuadrante_madera == cuadrante_actual:
                tile_x = (madera['x'] % paso_COLS) * TILE_SIZE
                tile_y = (madera['y'] % paso_ROWS) * TILE_SIZE

                rect_tronco = (tile_x + 1, tile_y + 4, 13, 7)

                pygame.draw.rect(screen, (139, 69, 19), rect_tronco)

                pygame.draw.rect(screen, (70, 35, 10), rect_tronco, 1)

        # Dibujar enemigos
        for enemigo in enemigos:
            cuad_x = enemigo.x // paso_COLS
            cuad_y = enemigo.y // paso_ROWS
            cuadrante_enemigo = cuad_y * 3 + cuad_x

            if cuadrante_enemigo == cuadrante_actual:
                tile_local_x = (enemigo.x % paso_COLS) * TILE_SIZE
                tile_local_y = (enemigo.y % paso_ROWS) * TILE_SIZE

                dibujo_x = tile_local_x + TILE_SIZE // 2
                dibujo_y = tile_local_y + TILE_SIZE // 2

                pygame.draw.circle(screen, (255, 0, 0), (dibujo_x, dibujo_y), 8)

        # Dibujar Jugador
        tile_local_x = (jugador.x % paso_COLS) * TILE_SIZE
        tile_local_y = (jugador.y % paso_ROWS) * TILE_SIZE

        dibujo_x = tile_local_x + TILE_SIZE // 2
        dibujo_y = tile_local_y + TILE_SIZE // 2

        if barco and matriz[jugador.y][jugador.x] == 0:
            rect_barco = (tile_local_x + 1, tile_local_y + 1, 13, 13)

            pygame.draw.rect(screen, (139, 69, 19), rect_barco)
            pygame.draw.rect(screen, (70, 35, 10), rect_barco, 1)

        pygame.draw.circle(screen, (255, 255, 255), (dibujo_x, dibujo_y), 8)

        # Interfaz de Inventario
        inv_text = font.render(f"Madera: {jugador.inventory['Madera']} | Hierro: {jugador.inventory['Hierro']}", True,(255, 255, 255))
        screen.blit(inv_text, (10, 10))

        # MINIMAPA
        tam_cuadrito = 15
        margen_derecho = 20
        margen_superior = 20
        minimapa = pygame.Surface((tam_cuadrito * 3, tam_cuadrito * 3), pygame.SRCALPHA)

        idx = 0
        for my in range(3):
            for mx in range(3):
                rect = pygame.Rect(mx * tam_cuadrito, my * tam_cuadrito, tam_cuadrito, tam_cuadrito)
                # Si el índice coincide con nuestro cuadrante actual, lo pintamos más opaco y de otro color
                if idx == cuadrante_actual:
                    pygame.draw.rect(minimapa, (255, 100, 100, 200), rect)  # Rojo semitransparente
                else:
                    pygame.draw.rect(minimapa, (0, 0, 0, 100), rect)  # Negro semitransparente

                # Borde blanco
                pygame.draw.rect(minimapa, (255, 255, 255, 150), rect, 1)
                idx += 1

        # Dibujamos el minimapa en la pantalla principal (arriba a la derecha)
        screen.blit(minimapa, (WIDTH - (tam_cuadrito * 3) - margen_derecho, margen_superior))

        if jugador.inventory["Madera"] >= 5:
            texto_mensaje = "Pulsa la letra 'Q' para construir un barco"  # Puedes cambiar esto por una variable
            mensaje_render = font.render(texto_mensaje, True, (200, 200, 200))  # Gris clarito
            screen.blit(mensaje_render, (10, 35))

            construir = True

        pygame.display.flip()
        clock.tick(15)

        # 1. CAPTURAR EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if jugador.x > 0 and (matriz[jugador.y][jugador.x - 1] != 0 or barco):
                jugador.x -= 1
        elif keys[pygame.K_RIGHT]:
            if jugador.x < COLS - 1 and (matriz[jugador.y][jugador.x + 1] != 0 or barco):
                jugador.x += 1
        elif keys[pygame.K_UP]:
            if jugador.y > 0 and (matriz[jugador.y - 1][jugador.x] != 0 or barco):
                jugador.y -= 1
        elif keys[pygame.K_DOWN]:
            if jugador.y < ROWS - 1 and (matriz[jugador.y + 1][jugador.x] != 0 or barco):
                jugador.y += 1
        elif keys[pygame.K_q] and construir:
            jugador.inventory["Madera"] -= 5
            construir = False
            barco = True

        # Recolectar madera
        for madera in maderas:
            if jugador.x == madera['x'] and jugador.y == madera['y']:
                maderas.remove(madera)
                jugador.inventory["Madera"] += 1
                break

        if contador_enemigos > tiempo_enemigo:
            if len(enemigos) < 10:
                distancia_min = 3
                distancia_max = 12
                x1 = random.randrange(jugador.x + distancia_min, jugador.x + distancia_max)
                x2 = random.randrange(jugador.x - distancia_max, jugador.x - distancia_min)
                y1 = random.randrange(jugador.y + distancia_min, jugador.y + distancia_max)
                y2 = random.randrange(jugador.y - distancia_max, jugador.y - distancia_min)
                r = random.randrange(0, 2)
                if r == 0:
                    x = min(x1, COLS - 1)
                    y = min(y1, ROWS - 1)
                else:
                    x = min(x2, COLS - 1)
                    y = min(y2, ROWS - 1)
                if not(x == jugador.x and y == jugador.y):
                    enemigos.append(zombie(x,y))
                contador_enemigos = 0
                tiempo_enemigo = random.randint(30, 60)

        contador_enemigos += 1





if __name__ == "__main__":
    main()