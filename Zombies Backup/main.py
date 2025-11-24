import pygame as pg
from pygame.locals import *

from constantes import *
from spr import *
from _Modulos import ecras

class Zombies(ecras.Jogo):
    def __init__(self):
        super().__init__(TITULO, LARGURA, ALTURA, 1, FPS, FONTE)

        self.telas = {
            "menu": Menu(self),
            "gameplay": GamePlay(self)
        }
        self.tela_atual = self.telas["menu"]

class Menu(ecras.Ecra):
    def __init__(self, jogo, *flags):
        super().__init__(jogo, *flags)

    def criar_sprites(self):
        super().criar_sprites()
        self.botoes = pg.sprite.Group()

        self.play = Botao((self.largura//2 -35, self.altura//2 +100), 'play')
        self.botoes.add(self.play)
        self.todas_sprites.add(self.play)

    def eventos(self):
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key in (K_KP_ENTER, K_RETURN):
                    self.jogo.mudar_tela("gameplay")

            pos_mouse = pg.mouse.get_pos()
            if event.type == MOUSEBUTTONDOWN:
                if self.play.rect.collidepoint(pos_mouse):
                    self.play.pressionar()
            if event.type == MOUSEBUTTONUP:
                if self.play.precionado:
                    self.play.despressionar()
                    if self.play.rect.collidepoint(pos_mouse):
                        self.jogo.mudar_tela("gameplay")

    def desenhar(self):
        super().desenhar()
    
class GamePlay(ecras.Ecra):
    def __init__(self, jogo, *flags) -> None:
        self.mapa_centro = [jogo.largura//2, jogo.altura//2]
        self.tiros_atirar = 0

        super().__init__(jogo, *flags)

        self.gameover = GameOver(self)

    def criar_sprites(self) -> None:
        super().criar_sprites()
        self.tiros = pg.sprite.Group()
        self.inimigos = pg.sprite.Group()
        
        self.mapa = Mapa(self.mapa_centro, MAPA_IMG, self.todas_sprites)
        self.mapa_estruturas = Mapa(self.mapa_centro, MAPA_ESTRUTURAS, self.todas_sprites)

        self.player = Player(self, SPRITESHEET_PLAYER, (80, 80, 26),
                             {'correndo': (0, 11), 'caminhando': (11, 19), 'morrendo': (19,24),
                              'atacando': (24, 25), 'parado': (25, 26)},
                                (0, 0), VIDA_PLAYER)

        self.mapa_difiente = Mapa(self.mapa_centro, MAPA_DIFIENTE, self.todas_sprites)

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
            Tanque(self, SPRITESHEET_TANQUE, (80, 80, 18),
                             {'parado': (0, 1), 'caminhando': (1, 6), 'atacando': (6, 14),
                               'morrendo': (14, 18)},
                               gerar_spawn_aleatorio(self.player.desl), VIDA_TANQUE)

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
        super().desenhar()

        # Barra de vida do player
        pg.draw.rect(self.tela, VERMELHO, pg.Rect(15, 15, VIDA_PLAYER*(self.largura//300), 50))
        pg.draw.rect(self.tela, VERDE, pg.Rect(15, 15, self.player.vida*(self.largura//300), 50))

        # Barra de vida dos inimigos
        for inimigo in self.inimigos:
            pg.draw.rect(self.tela, VERMELHO, pg.Rect(inimigo.rect.x, inimigo.rect.y -10,
                                                      inimigo.rect.width, 5))
            pg.draw.rect(self.tela, VERDE, pg.Rect(inimigo.rect.x, inimigo.rect.y -10,
                                                   inimigo.rect.width*(inimigo.vida/VIDA_TANQUE), 5))

class GameOver(ecras.SubEcra):
    def criar_sprites(self):
        super().criar_sprites()
        self.botoes = pg.sprite.Group()

        jogo = self.jogo
        self.play = Botao((self.largura//2 -35, self.altura//2 +180), 'play')
        self.play.funcionar = lambda : jogo.mudar_tela("gameplay")
        self.menu = Botao((self.largura//2 -38, self.altura//2 +100), 'menu')
        self.menu.funcionar = lambda : jogo.mudar_tela("menu")
        self.botoes.add(self.play, self.menu)
        self.todas_sprites.add(self.play, self.menu)

    def eventos(self):
        for event in pg.event.get():
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.jogo.mudar_tela("menu")

            pos_mouse = pg.mouse.get_pos()
            if event.type == MOUSEBUTTONDOWN:
                for botao in self.botoes.sprites():
                    if botao.rect.collidepoint(pos_mouse):
                        botao.pressionar()
            if event.type == MOUSEBUTTONUP:
                for botao in self.botoes.sprites():
                    if botao.precionado:
                        botao.despressionar()
                        if botao.rect.collidepoint(pos_mouse):
                            botao.funcionar()
                            self.rodando = False
                            

jogo = Zombies()
jogo.loop()
pg.quit()

# ATUALIZAÇÕES:
# - Adicionar mais monstros
# - Barreira de limite do mapa
# - Melhorar mapa das estruturas
# - Adicionar sons ao jogo
# - Colisão dos monstros 

# Menu inicial
# Tela de game over (restart, menu)
# Configurações

# BUGS:
# ...
