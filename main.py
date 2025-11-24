import pygame as pg
from pygame.locals import *

from constantes import *
from spr import *
import _Modulos.ecras as ecras
import _Modulos.PGutilitarios as PGutilitarios

import os
import random as rand

class Main(ecras.Jogo):
    def __init__(self) -> None:
        super().__init__(TITULO, LARGURA, ALTURA, 1, FPS)
        
        self.ecras = {
            "menu": Menu(self),
            "gameplay": GamePlay(self),
            "gameover": GameOver(self),
            "options": Options(self),
            "credits": Credits(self)
        }
        self.ecra_atual = self.ecras["menu"]

class Menu(ecras.Ecra):
    def criar_sprites(self) -> None:
        super().criar_sprites()
        self.botoes = pg.sprite.Group()

        grupos = [self.todas_sprites, self.botoes]
        self.botao_start = PGutilitarios.Botao(lambda: self.jogo.mudar_ecra("gameplay"),
        (self.largura//2, self.altura//2 - 340), BOTAO_START,
        aumt_select=True, escala=0.4, groups=grupos) # START
        self.botao_options = PGutilitarios.Botao(lambda: self.jogo.mudar_ecra("options"),
        (self.largura//2 +60, self.altura//2 + 20), BOTAO_OPTIONS,
        aumt_select=True, escala=0.2, groups=grupos) # OPTIONS
        self.botao_credits = PGutilitarios.Botao(lambda: self.jogo.mudar_ecra("credits"),
        (self.largura//2 +60, self.altura//2 + 146), BOTAO_CREDITS,
        aumt_select=True, escala=0.2, groups=grupos) # CREDITS

    def eventos(self) -> None:
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            for botao in self.botoes:
                botao.eventos(event)

    def desenhar(self) -> None:
        PGutilitarios.mostrar_imagem(self.tela, FUNDO_MENU, self.largura//2, self.altura//2,
                                     escala=self.jogo.escala)
        self.todas_sprites.draw(self.tela)

class GamePlay(ecras.Ecra):
    def criar_sprites(self) -> None:
        super().criar_sprites()
        self.centro_mapa = pg.Vector2(self.largura//2, self.altura//2)

        self.mapas = pg.sprite.Group()
        self.tiros = pg.sprite.Group()
        self.personagens = pg.sprite.Group()
        self.inimigos = pg.sprite.Group()
        self.difientes = pg.sprite.Group()

        self.mapa = Mapa(self, MAPA, self.mapas)
        self.mapa_estruturas = Mapa(self, MAPA_ESTRUTURAS, self.mapas)
        self.mapa_difiente = Mapa(self, MAPA_DIFIENTE, self.difientes)
        
        # Colisores
        self.colisores = []
        for l, linha in enumerate(TILE_MAP):
            for c, caractere in enumerate(linha):
                if caractere == '1':
                    rect = pg.Rect(self.mapa.rect.x + c*TAM_RECT_MAP, self.mapa.rect.y + l*TAM_RECT_MAP,
                                   TAM_RECT_MAP, TAM_RECT_MAP)
                    self.colisores.append(rect)
        self.COLISORES = self.colisores

        self.player = Player(self, (0, 0))
        self.tanque = Tanque(self, (200, 200))

    def eventos(self):
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.jogo.mudar_ecra("menu")

    def atualizar(self) -> None:
        # Atirar
        if self.player.atirando:
            self.tiros_atirar += TPF
            if self.tiros_atirar >= 1:
                self.tiros_atirar -= 1

                if self.player.direcao == 'direita':
                    pos = (self.player.rect.right -12, self.player.rect.centery +8)
                else:
                    pos = (self.player.rect.left +12, self.player.rect.centery +8)

                Tiro(self, pos, pg.mouse.get_pos(), self.tiros, self.todas_sprites)

        # Spawnar Monstros
        if len(self.inimigos) < 10:
            Tanque(self, TANQUE_SPRITESHEET, (80, 80, 18),
                             {'parado': (0, 1), 'caminhando': (1, 6), 'atacando': (6, 14),
                               'morrendo': (14, 18)},
                               self.gerar_spawn_aleatorio(self.player.desl), TANQUE_VIDA)

        # Mover
        precionados = pg.key.get_pressed()
        vel = (VEL_ATIRANDO if self.player.atirando else VEL_PLAYER)
        vel_diagonal = int(vel*0.707 +0.5)

        velx, vely = 0, 0
        for direcao in DIRECOES.values():
            if any([precionados[tecla] for tecla in direcao[0]]):
                velx += direcao[2] if direcao[1] == 0 else 0
                vely += direcao[2] if direcao[1] == 1 else 0

        velx *= (vel_diagonal if abs(velx)+abs(vely) == 2 else vel)
        vely *= (vel_diagonal if abs(velx)+abs(vely) == 2 else vel)

        # Detectar colisões
        player_rect = pg.Rect(0, 0, self.player.rect.width//2, self.player.rect.height//4)
        player_rect.bottomleft = (self.player.rect.left +20, self.player.rect.bottom -20)
        if self.player.estado != 'morrendo':
            player_rect.x += velx
            player_rect.y += vely

        if not any([player_rect.colliderect(rect) for rect in self.colisores]):
            limx = (1875 - self.largura)//2
            limy = (1875 - self.altura)//2
            
            if self.mapa_centro[0] -937 -velx <= 0 and \
             self.mapa_centro[0] +937 -velx >= self.largura and \
             -limx <= self.player.desl[0] <= limx:
                self.mapa_centro[0] -= velx
                for rect in self.colisores: rect.x -= velx
                
            if self.mapa_centro[1] -937 -vely <= 0 and \
             self.mapa_centro[1] +937 -vely >= self.altura and \
             -limy <= self.player.desl[1] <= limy:
                self.mapa_centro[1] -= vely
                for rect in self.colisores: rect.y -= vely

            if -900 <= self.player.desl[0] + velx <= 900: self.player.desl[0] += velx
            if -900 <= self.player.desl[1] + vely <= 900: self.player.desl[1] += vely
            
            self.mapa.rect.center = self.mapa_centro
            self.mapa_estruturas.rect.center = self.mapa_centro
            self.mapa_difiente.rect.center = self.mapa_centro

        super().atualizar()

    def desenhar(self) -> None:
        self.tela.fill(PRETO)
        self.mapas.draw(self.tela)
        self.tiros.draw(self.tela)
        for colisor in self.colisores:
            pg.draw.rect(self.tela, VERMELHO, colisor)
        self.personagens.draw(self.tela)
        self.difientes.draw(self.tela)
        
    def gerar_spawn_aleatorio(self, player_desl: list) -> None:
        spawnX = rand.choice([n for n in range(-937, 937) 
                                    if not player_desl[0]-300 <= n <= player_desl[0]+300])
        spawnY = rand.choice([n for n in range(-937, 937) 
                                    if not player_desl[1]-300 <= n <= player_desl[1]+300])
        return (spawnX, spawnY)

class GameOver(ecras.Ecra):
    def criar_sprites(self):
        super().criar_sprites()
        self.botoes = pg.sprite.Group()

        self.menu = PGutilitarios.Botao(lambda: self.jogo.mudar_ecra("menu"),
        (self.largura//2, self.altura//2 + 100), BOTAO_START, escala=0.3,
        groups=[self.todas_sprites, self.botoes]) # MENU

    def eventos(self):
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.jogo.mudar_ecra("menu")

            for botao in self.botoes:
                botao.eventos(event)

    def desenhar(self) -> None:
        PGutilitarios.mostrar_imagem(self.tela, FUNDO_GAMEOVER, self.largura//2, self.altura//2,
                                     escala=self.jogo.escala)
        self.todas_sprites.draw(self.tela)

class Options(ecras.Ecra):
    def eventos(self):
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.jogo.mudar_ecra("menu")

class Credits(ecras.Ecra):
    def __init__(self, jogo):
        super().__init__(jogo)

        self.altura_credits = self.altura + 781

    def eventos(self):
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.jogo.mudar_ecra("menu")

    def atualizar(self):
        self.altura_credits -= 2
        if self.altura_credits < -781:
            self.altura_credits = self.altura + 781

    def desenhar(self):
        super().desenhar()
        PGutilitarios.mostrar_imagem(self.tela, CREDITS, self.largura//2, self.altura_credits,
                                     self.jogo.escala)
        
jogo = Main()
jogo.loop()
pg.quit()

# ATUALIZAÇÕES:
# - tanque
# - vida dos personagens
# - colisões
# - fim do mapa