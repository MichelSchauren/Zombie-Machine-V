import pygame as pg
from pygame.locals import *

from constantes import *
from spr import *
from _Modulos import ecras
from _Modulos import PGutilitarios

import random as rand

class Zombies(ecras.Jogo):
    def __init__(self):
        super().__init__(TITULO, LARGURA, ALTURA, 1, FPS, FONTE)

        self.telas = {
            "menu": Menu(self),
            "gameplay": GamePlay(self),
            "gameover": GameOver(self)
        }
        self.tela_atual = self.telas["menu"]

class Menu(ecras.Ecra):
    def __init__(self, jogo, *flags):
        super().__init__(jogo, *flags)

    def criar_sprites(self):
        super().criar_sprites()
        self.botoes = pg.sprite.Group()

        self.start = PGutilitarios.Botao((self.largura//2 -10, self.altura//2 -380), BOTAO_START, (540, 360), lambda : self.jogo.mudar_tela("gameplay"),
                           self.botoes, self.todas_sprites)
        self.options = PGutilitarios.Botao((self.largura//2 +80, self.altura//2 +15), BOTAO_OPTIONS, (216, 144), lambda : print("Opções"),
                             self.botoes, self.todas_sprites)
        self.credits = PGutilitarios.Botao((self.largura//2 +80, self.altura//2 +135), BOTAO_CREDITS, (216, 144), lambda : print("Créditos"),
                             self.botoes, self.todas_sprites)

    def eventos(self):
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key in (K_KP_ENTER, K_RETURN):
                    self.start.funcionar()

            for botao in self.botoes:
                botao.eventos(event)

    def desenhar(self):
        self.tela.fill(self.jogo.fundo)
        self.mostrar_imagem(FUNDO_MENU, self.largura//2, self.altura//2)
        self.todas_sprites.draw(self.tela)
    
class GamePlay(ecras.Ecra):
    def __init__(self, jogo, *flags) -> None:
        self.mapa_centro = [jogo.largura//2, jogo.altura//2]
        self.tiros_atirar = 0

        super().__init__(jogo, *flags)

        self.gameover = GameOver(self)

    def criar_sprites(self) -> None:
        self.todas_sprites = pg.sprite.Group()
        self.mapas = pg.sprite.Group()
        self.tiros = pg.sprite.Group()
        self.personagens = pg.sprite.Group()
        self.inimigos = pg.sprite.Group()
        self.difientes = pg.sprite.Group()
        
        self.mapa = Mapa(self.mapa_centro, MAPA, self.todas_sprites, self.mapas)
        self.mapa_estruturas = Mapa(self.mapa_centro, MAPA_ESTRUTURAS, self.todas_sprites, self.mapas)

        self.player = Player(self, PLAYER_SPRITESHEET, (80, 80, 26),
                             {'correndo': (0, 11), 'caminhando': (11, 19), 'morrendo': (19,24),
                              'atacando': (24, 25), 'parado': (25, 26)},
                                (0, 0), PLAYER_VIDA)

        self.mapa_difiente = Mapa(self.mapa_centro, MAPA_DIFIENTE, self.todas_sprites, self.difientes)

        # Colisores
        self.colisores = []
        for l, linha in enumerate(TILE_MAP):
            for c, caractere in enumerate(linha):
                if caractere == '1':
                    rect = pg.Rect(self.mapa.rect.x + c*TAM_RECT_MAP, self.mapa.rect.y + l*TAM_RECT_MAP,
                                   TAM_RECT_MAP, TAM_RECT_MAP)
                    self.colisores.append(rect)

    def eventos(self) -> None:
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

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
        vel = (PLAYER_VEL_ATIRANDO if self.player.atirando else PLAYER_VEL)
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

            if self.player.estado != 'morrendo':
                if -900 <= self.player.desl[0] + velx <= 900: self.player.desl[0] += velx
                if -900 <= self.player.desl[1] + vely <= 900: self.player.desl[1] += vely
            
            self.mapa.rect.center = self.mapa_centro
            self.mapa_estruturas.rect.center = self.mapa_centro
            self.mapa_difiente.rect.center = self.mapa_centro

        super().atualizar()

    def desenhar(self) -> None:
        self.mapas.draw(self.tela)
        self.tiros.draw(self.tela)
        self.personagens.draw(self.tela)
        self.difientes.draw(self.tela)

        # Barra de vida do player
        pg.draw.rect(self.tela, VERMELHO, pg.Rect(15, 15, PLAYER_VIDA*(self.largura//300), 50))
        pg.draw.rect(self.tela, VERDE, pg.Rect(15, 15, self.player.vida*(self.largura//300), 50))

        # Barra de vida dos inimigos
        for inimigo in self.inimigos:
            pg.draw.rect(self.tela, VERMELHO, pg.Rect(inimigo.rect.x, inimigo.rect.y -10,
                                                      inimigo.rect.width, 5))
            pg.draw.rect(self.tela, VERDE, pg.Rect(inimigo.rect.x, inimigo.rect.y -10,
                                                   inimigo.rect.width*(inimigo.vida/TANQUE_VIDA), 5))

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

        self.menu = PGutilitarios.Botao((self.largura//2 -180, self.altura//2 +50), BOTAO_MENU, (360, 280), lambda : self.jogo.mudar_tela("menu"),
                          self.botoes, self.todas_sprites)

    def eventos(self):
        for event in self.jogo.eventos:
            self.eventos_padrao(event), (216, 144)

            if event.type == KEYDOWN:
                if event.key in (K_KP_ENTER, K_RETURN):
                    self.restart.funcionar()
                if event.key == K_ESCAPE:
                    self.menu.funcionar()

            for botao in self.botoes:
                botao.eventos(event)
    
    def desenhar(self):
        self.tela.fill(self.jogo.fundo)
        self.mostrar_imagem(FUNDO_GAMEOVER, self.largura//2, self.altura//2)
        self.todas_sprites.draw(self.tela)

jogo = Zombies()
jogo.loop()
pg.quit()

# ATUALIZAÇÕES:
# - Adicionar mais monstros
# - Adicionar sons ao jogo
# - Colisão dos monstros
# - Colocar nome do personagem
# - Configurações
# - Créditos
# - Tela de pausa
# - Melhorar a IA dos inimigos

# BUGS:
# bug do Mikael Jackson
