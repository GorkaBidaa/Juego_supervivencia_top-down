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
    3: (130, 130, 130),  # Gris (Roca)
    4: (143, 151, 121)     #Verde caqui (pantano)
}
game_over = False

def generar_mapa():
    num_seeds = 220
    nodos = np.column_stack((np.random.randint(0, COLS, num_seeds),
                             np.random.randint(0, ROWS, num_seeds)))
    bioma = np.random.randint(0, 5, num_seeds)

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
        self.inventory = {"Madera": 4, "Hierro": 2}

    def morir(self):
        global game_over
        game_over= True

class zombie:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def mover(self,jugador):
        if abs(self.x - jugador.x) < abs(self.y - jugador.y):
            if self.y < jugador.y:
                self.y += 1
            else:
                self.y -= 1
        else:
            if self.x < jugador.x:
                self.x += 1
            else:
                self.x -= 1

        if(self.x == jugador.x and self.y == jugador.y):
            jugador.morir()




def main():
    global game_over
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("KNN Survival")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    matriz = generar_mapa()
    mapas = []
    paso_COLS = COLS // 3  # 80
    paso_ROWS = ROWS // 3  # 50

    construir_barco = False
    construir_espada = False
    barco = False
    espada = False
    espadazos = []
    tiempo_espadazo = 0

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
        repetida = False
        mx = random.randint(0, COLS - 1)
        my = random.randint(0, ROWS - 1)
        if matriz[my][mx] == 1 or matriz[my][mx] == 2 or matriz[my][mx] == 4:
            for m in maderas:
                if m.get('x') == mx and m.get('y') == my:
                    repetida = True
            if not repetida:
                maderas.append({'x': mx, 'y': my})
                cont_madera += 1

    hierros = []
    cont_hierro = 0
    cantidad_hierro = random.randint(5, 9)
    while cont_hierro < cantidad_hierro:
        repetida = False
        mx = random.randint(0, COLS - 1)
        my = random.randint(0, ROWS - 1)
        if matriz[my][mx] == 3:
            for h in hierros:
                if h.get('x') == mx and h.get('y') == my:
                    repetida = True
            if not repetida:
                hierros.append({'x': mx, 'y': my})
                cont_hierro += 1


    enemigos = []
    contador_enemigos = 0
    tiempo_enemigo = random.randint(30, 60)
    mov_enemigos = 0

    running = True
    while running:

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

        for hierro in hierros:
            cuad_x = hierro['x'] // paso_COLS
            cuad_y = hierro['y'] // paso_ROWS
            cuadrante_hierro = cuad_y * 3 + cuad_x

            if cuadrante_hierro == cuadrante_actual:
                tile_x = (hierro['x'] % paso_COLS) * TILE_SIZE
                tile_y = (hierro['y'] % paso_ROWS) * TILE_SIZE

                rect_hierro = (tile_x + 3, tile_y + 3, 9, 9)

                pygame.draw.rect(screen, (180, 180, 180), rect_hierro)  # Gris claro (centro)
                pygame.draw.rect(screen, (100, 100, 100), rect_hierro, 1)  # Gris oscuro (borde)

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

        #Dibujar Espadazos
        if tiempo_espadazo > 0:
            for ex, ey in espadazos:
                cuad_x = ex // paso_COLS
                cuad_y = ey // paso_ROWS
                cuadrante_espadazo = cuad_y * 3 + cuad_x

                if cuadrante_espadazo == cuadrante_actual:
                    tile_local_x = (ex % paso_COLS) * TILE_SIZE
                    tile_local_y = (ey % paso_ROWS) * TILE_SIZE

                    rect_ataque = (tile_local_x, tile_local_y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, (150, 200, 255), rect_ataque, 2)

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

        screen.blit(minimapa, (WIDTH - (tam_cuadrito * 3) - margen_derecho, margen_superior))

        y_mensaje = 35

        if jugador.inventory["Madera"] >= 5:
            texto_mensaje = "Pulsa la letra 'Q' para construir_barco un barco"
            mensaje_render = font.render(texto_mensaje, True, (200, 200, 200))
            screen.blit(mensaje_render, (10, y_mensaje))
            construir_barco = True

            y_mensaje += 25

        if jugador.inventory["Hierro"] >= 3:
            texto_mensaje = "Pulsa la letra 'E' para construir_barco una Espada"
            mensaje_render = font.render(texto_mensaje, True, (200, 200, 200))
            screen.blit(mensaje_render, (10, y_mensaje))
            construir_espada = True

        if mov_enemigos >= 5:
            for enemigo in enemigos:
                enemigo.mover(jugador)
            mov_enemigos = 0
        mov_enemigos += 1



        # 1. CAPTURAR EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not game_over:
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
            elif keys[pygame.K_q] and construir_barco:
                jugador.inventory["Madera"] -= 5
                construir_barco = False
                barco = True
            elif keys[pygame.K_e] and construir_espada:
                jugador.inventory["Hierro"] -= 3
                construir_espada = False
                espada = True
            elif keys[pygame.K_SPACE] and espada and tiempo_espadazo == 0:
                ex = jugador.x
                ey = jugador.y
                espadazos.clear()
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if abs(dx) != 2 or abs(dy) != 2:
                            nx = ex + dx
                            ny = ey + dy
                            if 0 <= nx < COLS and 0 <= ny < ROWS:
                                espadazos.append([nx, ny])
                tiempo_espadazo = 7



            for enemigo in enemigos:
                if jugador.x == enemigo.x and jugador.y == enemigo.y:
                    game_over= True

            # Recolectar madera
            for madera in maderas:
                if jugador.x == madera['x'] and jugador.y == madera['y']:
                    maderas.remove(madera)
                    jugador.inventory["Madera"] += 1
                    break

            # Recolectar Hierro
            for hierro in hierros:
                if jugador.x == hierro['x'] and jugador.y == hierro['y']:
                    hierros.remove(hierro)
                    jugador.inventory["Hierro"] += 1
                    break

            if contador_enemigos > tiempo_enemigo:
                if len(enemigos) >= 10:
                    enemigos.pop(0)
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

            if tiempo_espadazo > 0:
                for espadazo in espadazos:
                    for enemigo in enemigos[:]:
                        if enemigo.x == espadazo[0] and enemigo.y == espadazo[1]:
                            enemigos.remove(enemigo)

                tiempo_espadazo -= 1

                if tiempo_espadazo == 0:
                    espadazos.clear()
        else:
            screen.fill((0, 0, 0))

            texto_perder = font.render("¡GAME OVER!", True, (255, 0, 0))
            rect_texto = texto_perder.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(texto_perder, rect_texto)



        pygame.display.flip()
        clock.tick(15)





if __name__ == "__main__":
    main()