import pygame as pg
from pygame.locals import *

from constantes import *
from spr import *
import _Modulos.ecras as ecras
import _Modulos.PGutilitarios as PGutilitarios

import os
import random

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
        self.colisores = COLISORES

        self.mapas = pg.sprite.Group()
        self.tiros = pg.sprite.Group()
        self.personagens = pg.sprite.Group()
        self.inimigos = pg.sprite.Group()
        self.difientes = pg.sprite.Group()

        self.mapa = Mapa(self, MAPA, self.mapas)
        self.mapa_estruturas = Mapa(self, MAPA_ESTRUTURAS, self.mapas)
        self.mapa_difiente = Mapa(self, MAPA_DIFIENTE, self.difientes)

        self.player = Player(self, (0, 0))
        self.tanque = Tanque(self, (200, 200))

    def eventos(self):
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.jogo.mudar_ecra("menu")

    def atualizar(self) -> None:
        self.todas_sprites.update()

    def desenhar(self) -> None:
        self.tela.fill(PRETO)
        self.mapas.draw(self.tela)
        self.tiros.draw(self.tela)
        for colisor in self.colisores:
            pg.draw.rect(self.tela, VERMELHO, colisor)
        self.personagens.draw(self.tela)
        self.difientes.draw(self.tela)

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