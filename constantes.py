import pygame as pg
from pygame.locals import *

import os
import random as rand

# Display
LARGURA = 1080
ALTURA = 620
TITULO = "Zombie Kill Machine V"
FPS = 30
FONTE = "consolas"
RELOGIO = pg.time.Clock()

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (250, 10, 10)
VERDE = (10, 250, 10)
AZUL = (10, 10, 250)
AMARELO = (250, 250, 10)

# Teclas e Direções
DIRECOES = {'up': [(K_UP, K_w), 1, -1],
            'left': [(K_LEFT, K_a), 0, -1],
            'down': [(K_DOWN, K_s), 1, 1],
            'right': [(K_RIGHT, K_d), 0, 1]}

# Dimenções do mapa
MAPA_LARGURA, MAPA_ALTURA = 1875, 1875

# Arquivos
DIR = os.path.dirname(__file__)
DIR_SPRITES = os.path.join(DIR, 'Sprites')
DIR_MAPAS = os.path.join(DIR_SPRITES, 'Mapas')
DIR_PERSONAGENS = os.path.join(DIR_SPRITES, 'Personagens')
DIR_INTERFACE = os.path.join(DIR_SPRITES, 'Interface')

#  mapas
MAPA = os.path.join(DIR_MAPAS, 'Mapa.png')
MAPA_ESTRUTURAS = os.path.join(DIR_MAPAS, 'Mapa_estruturas.png')
MAPA_DIFIENTE = os.path.join(DIR_MAPAS, 'Mapa_difiente.png' )

#  spritesheets dos personagens
PLAYER_SPRITESHEET = os.path.join(DIR_PERSONAGENS, 'Player_spritesheet.png')
RAPIDO_SPRITESHEET = os.path.join(DIR_PERSONAGENS, 'Rapido_spritesheet.png')
ARQUEIRO_SPRITESHEET = os.path.join(DIR_PERSONAGENS, 'Arqueiro_spritesheet.png')
TANQUE_SPRITESHEET = os.path.join(DIR_PERSONAGENS, 'Tanque_spritesheet.png')

#  Fundos
FUNDO_MENU = os.path.join(DIR_INTERFACE, 'Fundo_menu.jpg')
FUNDO_GAMEOVER = os.path.join(DIR_INTERFACE, 'Fundo_gameover.jpg')
#  Botões
BOTAO_START = os.path.join(DIR_INTERFACE, 'Botão_start.png')
BOTAO_CREDITS = os.path.join(DIR_INTERFACE, 'Botão_credits.png')
BOTAO_OPTIONS = os.path.join(DIR_INTERFACE, 'Botão_options.png')
BOTAO_MENU = os.path.join(DIR_INTERFACE, 'Botão_menu.png')

CREDITS = os.path.join(DIR_INTERFACE, 'Créditos.jpg')

# Tile Map
TAM_RECT_MAP = 5
TILE_MAP_TXT = os.path.join(DIR_MAPAS, f'tile_map{1875//TAM_RECT_MAP}x{1875//TAM_RECT_MAP}.txt')
TILE_MAP = []
with open(TILE_MAP_TXT, 'r', encoding="utf-8") as txt:
    quebra = txt.readlines()
    TILE_MAP = [linha.strip() for linha in quebra]

# Configurações
#  player
PLAYER_VEL = 8
PLAYER_VEL_ATIRANDO = 3
PLAYER_VIDA = 200
TIRO_DANO = 3
TIRO_VEL = 20
TPF = 0.2

#  tanque
TANQUE_VEL = 3
TANQUE_VIDA = 40
TANQUE_DANO = 10
TANQUE_ALCANCE = 40
