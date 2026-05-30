import pygame
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import random

TILE_SIZE = 20
COLS, ROWS = 40, 30
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE

# Biomas (0: Agua, 1: Arena, 2: Hierba, 3: Roca)
COLORS = {
    0: (50, 150, 200),  # Azul (Agua)
    1: (210, 190, 130), # Amarillo (Arena)
    2: (100, 200, 100), # Verde (Hierba)
    3: (130, 130, 130)  # Gris (Roca)
}

def generar_mapa():
    num_seeds = 25
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
    print(matriz)
    return matriz


class player:
    def __init__(self, px, py):
        self.x = px
        self.y = py
        self.inventory = {"Madera": 0, "Hierro": 0}


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("KNN Survival")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    mapa = generar_mapa()

    # CORRECCIÓN 1: Spawn seguro y lectura [y][x]
    px = random.randint(0, COLS - 1)
    py = random.randint(0, ROWS - 1)
    while mapa[py][px] == 0:
        px = random.randint(0, COLS - 1)
        py = random.randint(0, ROWS - 1)

    jugador = player(px, py)

    running = True
    while running:
        # Dibujar Mapa
        for y in range(ROWS):
            for x in range(COLS):
                pygame.draw.rect(screen, COLORS[mapa[y][x]], (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Dibujar Jugador
        pygame.draw.circle(screen, (255, 255, 255),
                           (jugador.x * TILE_SIZE + TILE_SIZE // 2, jugador.y * TILE_SIZE + TILE_SIZE // 2), 8)

        # Interfaz de Inventario
        inv_text = font.render(f"Madera: {jugador.inventory['Madera']} | Hierro: {jugador.inventory['Hierro']}", True,
                               (255, 255, 255))
        screen.blit(inv_text, (10, 10))

        pygame.display.flip()
        clock.tick(15)

        # 1. CAPTURAR EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # CORRECCIÓN 2: Lectura [y][x] y control de bordes
                if event.key == pygame.K_LEFT:
                    if jugador.x > 0 and mapa[jugador.y][jugador.x - 1] != 0:
                        jugador.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if jugador.x < COLS - 1 and mapa[jugador.y][jugador.x + 1] != 0:
                        jugador.x += 1
                elif event.key == pygame.K_UP:
                    if jugador.y > 0 and mapa[jugador.y - 1][jugador.x] != 0:
                        jugador.y -= 1
                elif event.key == pygame.K_DOWN:
                    if jugador.y < ROWS - 1 and mapa[jugador.y + 1][jugador.x] != 0:
                        jugador.y += 1





if __name__ == "__main__":
    main()