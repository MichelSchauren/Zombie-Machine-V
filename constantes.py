import pygame as pg
import os

# Display
LARGURA, ALTURA = 1080, 620
TITULO = "Zombie Kill Machine V"
FPS = 30

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (250, 10, 10)
VERDE = (10, 250, 10)
AZUL = (10, 10, 250)
AMARELO = (250, 250, 10)

# Direções
DIRECOES = {
    "W": [(pg.K_w, pg.K_UP), (0, -1)],
    "A": [(pg.K_a, pg.K_LEFT), (-1, 0)],
    "S": [(pg.K_s, pg.K_DOWN), (0, 1)],
    "D": [(pg.K_d, pg.K_RIGHT), (1, 0)]
}

# ARQUIVOS
DIR = os.path.dirname(__file__)
DIR_SPRITES = os.path.join(DIR, "Sprites")
DIR_SONS = os.path.join(DIR, "Sons")
DIR_INTERFACE = os.path.join(DIR_SPRITES, "Interface")
DIR_MAPAS = os.path.join(DIR_SPRITES, "Mapas")
DIR_PERSONAGENS = os.path.join(DIR_SPRITES, "Personagens")

#  mapas
MAPA = os.path.join(DIR_MAPAS, "Mapa.png")
MAPA_ESTRUTURAS = os.path.join(DIR_MAPAS, "Mapa_estruturas.png")
MAPA_DIFIENTE = os.path.join(DIR_MAPAS, "Mapa_difiente.png")

# personagens
PLAYER_SPRITESHEET = os.path.join(DIR_PERSONAGENS, "Player_spritesheet.png")
TANQUE_SPRITESHEET = os.path.join(DIR_PERSONAGENS, "Tanque_spritesheet.png")

# Interface
FUNDO_MENU = os.path.join(DIR_INTERFACE, "Fundo_menu.jpg")
FUNDO_GAMEOVER = os.path.join(DIR_INTERFACE, "Fundo_gameover.png")
BOTAO_START = os.path.join(DIR_INTERFACE, "Botão_start.png")
BOTAO_OPTIONS = os.path.join(DIR_INTERFACE, "Botão_options.png")
BOTAO_CREDITS = os.path.join(DIR_INTERFACE, "Botão_credits.png")
CREDITS = os.path.join(DIR_INTERFACE, "Créditos.jpg")

# tile map
TAM_COLISOR = 5
tile_map_caminho = os.path.join(DIR_MAPAS, "tile_map.txt")
with open(tile_map_caminho, "r") as f:
    TILE_MAP = [list(linha.strip()) for linha in f.readlines()]
    COLISORES = []
    for y, linha in enumerate(TILE_MAP):
        for x, valor in enumerate(linha):
            if valor == "1":
                COLISORES.append(pg.Rect(x * TAM_COLISOR, y * TAM_COLISOR, TAM_COLISOR, TAM_COLISOR))

# Sons
# ...

# Configurações GamePlay
PLAYER_VEL = 8
PLAYER_VEL_ATIRANDO = 5
PLAYER_VIDA = 100
TPF = 0.3  # tiros por frame
TIRO_VEL = 20
TIRO_DANO = 10

TANQUE_VEL = 5
TANQUE_VIDA = 50
