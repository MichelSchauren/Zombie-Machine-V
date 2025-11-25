import pygame as pg
from pygame.locals import *

import os
import random as rand

# Display
LARGURA = 1080
ALTURA = 620
TITULO = "Zombies"
FPS = 30
FONTE = "consolas"
RELOGIO = pg.time.Clock()

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (250, 10, 10)
VERDE = (10, 250, 10)
AZUL = (10, 10, 250)

# Teclas e Direções
DIRECOES = {'up': [(K_UP, K_w), 1, -1],
            'left': [(K_LEFT, K_a), 0, -1],
            'down': [(K_DOWN, K_s), 1, 1],
            'right': [(K_RIGHT, K_d), 0, 1]}

# Funções úteis
def calc_movimento(pos_inicial: tuple, pos_final: tuple, mov: float) -> None:
    dx = pos_final[0] - pos_inicial[0]
    dy = pos_final[1] - pos_inicial[1]
    dist_total = (dx**2 + dy**2)**0.5

    mx = int((dx / dist_total)*mov + (0.5 if dx >= 0 else -0.5))
    my = int((dy / dist_total)*mov + (0.5 if dy >= 0 else -0.5))

    return mx, my

def calc_dist(pos_inicial: tuple, pos_final: tuple) -> None:
    dx = pos_final[0] - pos_inicial[0]
    dy = pos_final[1] - pos_inicial[1]
    dist_total = (dx**2 + dy**2)**0.5
    return dist_total

def gerar_spawn_aleatorio(player_desl: list) -> None:
    spawnX = rand.choice([n for n in range(-937, 937) 
                                if not player_desl[0]-300 <= n <= player_desl[0]+300])
    spawnY = rand.choice([n for n in range(-937, 937) 
                                if not player_desl[1]-300 <= n <= player_desl[1]+300])
    return (spawnX, spawnY)

# Arquivos
DIR = os.path.dirname(__file__)
DIR_SPRITES = os.path.join(DIR, 'Sprites')
DIR_MAPAS = os.path.join(DIR_SPRITES, 'Mapas')
DIR_PERSONAGENS = os.path.join(DIR_SPRITES, 'Personagens')
DIR_MENU = os.path.join(DIR_SPRITES, 'Menu')

#  mapas
MAPA_IMG = os.path.join(DIR_MAPAS, 'Mapa.png')
MAPA_ESTRUTURAS = os.path.join(DIR_MAPAS, 'Mapa_estruturas.png')
MAPA_DIFIENTE = os.path.join(DIR_MAPAS, 'Mapa_difiente.png' )

#  spritesheets dos personagens
SPRITESHEET_PLAYER = os.path.join(DIR_PERSONAGENS, 'Player.png')
SPRITESHEET_RAPIDO = os.path.join(DIR_PERSONAGENS, 'Rapido.png')
SPRITESHEET_ARQUEIRO = os.path.join(DIR_PERSONAGENS, 'Arqueiro.png')
SPRITESHEET_TANQUE = os.path.join(DIR_PERSONAGENS, 'Tanque.png')

#  Fundos
FUNDO_MENU = os.path.join(DIR_MENU, 'Fundo_menu.jpg')
FUNDO_GAMEOVER = os.path.join(DIR_MENU, 'Fundo_gameover.jpg')
#  Botões
BOTAO_START = os.path.join(DIR_MENU, 'Botão_start.png')
BOTAO_CREDITS = os.path.join(DIR_MENU, 'Botão_credits.png')
BOTAO_OPTIONS = os.path.join(DIR_MENU, 'Botão_options.png')
BOTAO_MENU = os.path.join(DIR_MENU, 'Botão_menu.png')

# Tile Map
TAM_RECT_MAP = 5
TILE_MAP_TXT = os.path.join(DIR_SPRITES, f'tile_map{1875//TAM_RECT_MAP}x{1875//TAM_RECT_MAP}.txt')
TILE_MAP = []
with open(TILE_MAP_TXT, 'r', encoding="utf-8") as txt:
    quebra = txt.readlines()
    TILE_MAP = [linha.strip() for linha in quebra]

# Configurações
#  player
VEL_PLAYER = 8
VEL_ATIRANDO = 3
VIDA_PLAYER = 200
DANO_TIRO = 3
VEL_TIRO = 20
TPF = 0.2

#  tanque
VEL_TANQUE = 3
VIDA_TANQUE = 40
DANO_TANQUE = 10


if __name__ == '__main__':
    print(calc_movimento((0, 0), (-20, 10), 5))
