import pygame as pg
from pygame.locals import *

from constantes import *
from spr import *
from _Modulos import ecras
from _Modulos import PGutilitarios
from _Modulos.spatial_grid import SpatialGrid

import random as rand

class Zombie(ecras.Jogo):
    def __init__(self) -> None:
        super().__init__(TITULO, LARGURA, ALTURA, 1, FPS, FONTE)

        self.player_nome = "Player"

        self.ecras = {
            "menu": Menu(self),
            "gameplay": GamePlay(self),
            "gameover": GameOver(self),
            "options": Options(self),
            "credits": Credits(self)
        }
        self.ecra_atual = self.ecras["menu"]

class Menu(ecras.Ecra):
    def __init__(self, jogo, *flags) -> None:
        super().__init__(jogo, *flags)

    def criar_sprites(self) -> None:
        super().criar_sprites()
        self.botoes = pg.sprite.Group()

        self.start = PGutilitarios.Botao(lambda : self.jogo.mudar_ecra("gameplay"), (self.largura//2 +64, self.altura//2 -290), BOTAO_START,
                                         escala=0.4, aumt_select=True, groups=[self.botoes, self.todas_sprites])
        self.options = PGutilitarios.Botao(lambda : print("Opções"), (self.largura//2 +80, self.altura//2 +20), BOTAO_OPTIONS,
                                           escala=0.2, aumt_select=True, groups=[self.botoes, self.todas_sprites])
        self.credits = PGutilitarios.Botao(lambda : self.jogo.mudar_ecra("credits"), (self.largura//2 +80, self.altura//2 +135), BOTAO_CREDITS,
                                            escala=0.2, aumt_select=True, groups=[self.botoes, self.todas_sprites])

        self.caixa_nome = PGutilitarios.Caixa_Texto(pg.Rect(self.largura//2 +280, self.altura//2 -80, 240, 60), 24, self.jogo.fonte,
                                                     texto=self.jogo.player_nome, border_radius=20, padding=20, groups=[self.todas_sprites])

    def eventos(self) -> None:
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

            if event.type == KEYDOWN:
                if event.key in (K_KP_ENTER, K_RETURN):
                    self.start.func()

            for botao in self.botoes:
                botao.eventos(event)

            self.caixa_nome.eventos(event)
            self.jogo.player_nome = self.caixa_nome.texto

    def desenhar(self) -> None:
        self.tela.fill(PRETO)
        PGutilitarios.mostrar_imagem(self.tela, FUNDO_MENU, self.largura//2, self.altura//2)
        self.todas_sprites.draw(self.tela)
    
class GamePlay(ecras.Ecra):
    def __init__(self, jogo, *flags) -> None:
        self.mapa_rect = pg.Rect(0, 0, MAPA_LARGURA, MAPA_ALTURA)
        self.mapa_rect.center = (jogo.largura//2, jogo.altura//2)
        self.tiros_atirar = 0

        super().__init__(jogo, *flags)
        
        self.viewport = pg.Rect(0, 0, self.largura, self.altura)

    def criar_sprites(self) -> None:
        self.todas_sprites = pg.sprite.Group()
        self.mapas = pg.sprite.Group()
        self.tiros = pg.sprite.Group()
        self.personagens = pg.sprite.Group()
        self.inimigos = pg.sprite.Group()
        self.difientes = pg.sprite.Group()
        
        self.mapa = Mapa(self.mapa_rect, MAPA, self.todas_sprites, self.mapas)
        self.mapa_estruturas = Mapa(self.mapa_rect, MAPA_ESTRUTURAS, self.todas_sprites, self.mapas)

        self.player = Player(self, (MAPA_LARGURA//2, MAPA_ALTURA//2))
        self.nome_surf = pg.font.SysFont(self.jogo.fonte, 20, True).render(self.jogo.player_nome, True, PRETO)
        self.nome_rect = self.nome_surf.get_rect()

        self.mapa_difiente = Mapa(self.mapa_rect, MAPA_DIFIENTE, self.todas_sprites, self.difientes)

        # Colisores
        self.grid = SpatialGrid(TAM_RECT_MAP, MAPA_LARGURA, MAPA_ALTURA)
        for l, linha in enumerate(TILE_MAP):
            for c, caractere in enumerate(linha):
                if caractere == '1':
                    rect = pg.Rect(c*TAM_RECT_MAP, l*TAM_RECT_MAP, TAM_RECT_MAP, TAM_RECT_MAP)
                    self.grid.insert(rect)

    def eventos(self) -> None:
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

    def atualizar(self) -> None:
        pos_mouse = pg.mouse.get_pos()
        # Atirar
        if self.player.atirando:
            self.tiros_atirar += TPF
            if self.tiros_atirar >= 1:
                self.tiros_atirar -= 1

                if self.player.direcao == 'direita':
                    desl = (self.player.rect_map.centerx +24, self.player.rect_map.centery +8)
                else:
                    desl = (self.player.rect_map.centerx -24, self.player.rect_map.centery +8)
                destino = (-self.mapa_rect.x + pos_mouse[0], -self.mapa_rect.y + pos_mouse[1])

                Tiro(self, desl, destino, self.tiros, self.todas_sprites)

        # Spawnar Monstros
        if len(self.inimigos) < 10:
            Tanque(self, self.gerar_spawn_aleatorio(self.player.rect_map.center))

        # Calcular movimento
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
        p_colisor = self.player.rect_colid.move(velx, vely)
        possiveis = self.grid.query(p_colisor)  # usar grid.query para obter só rects próximos
        if not any(p_colisor.colliderect(col) for col in possiveis) and self.player.estado != 'morrendo':
            liml, limr = self.largura//2, MAPA_LARGURA - self.largura//2
            limt, limb = self.altura//2, MAPA_ALTURA - self.altura//2
            
            if liml <= self.player.rect_map.centerx <= limr:
                if self.mapa_rect.left -velx > 0 or self.mapa.rect.right -velx < self.largura: pass
                else:
                    self.mapa_rect.x -= velx # Mover mapa no eixo x

            if limt <= self.player.rect_map.centery <= limb:
                if self.mapa_rect.top -vely > 0 or self.mapa.rect.bottom -vely < self.altura: pass
                else:
                    self.mapa_rect.y -= vely # Mover mapa no eixo y

            # Mover player se não houver colisões
            if 20 <= self.player.rect_map.centerx + velx <= MAPA_LARGURA -20: self.player.rect_map.centerx += velx
            if 20 <= self.player.rect_map.centery + vely <= MAPA_ALTURA -20: self.player.rect_map.centery += vely

        super().atualizar()

    def desenhar(self) -> None:
        self.desenhar_group(self.mapas)
        self.desenhar_group(self.tiros)
        self.desenhar_group(self.personagens)
        self.desenhar_group(self.difientes)

        # Barra de vida dos inimigos
        for inimigo in self.inimigos:
            barra = pg.Rect(inimigo.rect.x, inimigo.rect.y -10, inimigo.rect.width, 5)
            vida = pg.Rect(inimigo.rect.x, inimigo.rect.y -10, inimigo.rect.width*(inimigo.vida/TANQUE_VIDA), 5)
            if barra.colliderect(self.viewport):
                pg.draw.rect(self.tela, VERMELHO, barra)
                pg.draw.rect(self.tela, VERDE, vida)

        # Nome player
        self.nome_rect.center = (self.player.rect.centerx, self.player.rect.top -20)
        self.tela.blit(self.nome_surf, self.nome_rect)

        # Barra de vida do player
        pg.draw.rect(self.tela, VERMELHO, pg.Rect(15, 15, PLAYER_VIDA*(self.largura//300), 50))
        pg.draw.rect(self.tela, VERDE, pg.Rect(15, 15, self.player.vida*(self.largura//300), 50))

    def desenhar_group(self, group) -> None:
        for sprite in group.sprites():
            if sprite.rect.colliderect(self.viewport):
                self.tela.blit(sprite.image, sprite.rect)

    def gerar_spawn_aleatorio(self, player_desl: list) -> None:
        spawnX = rand.choice([n for n in range(0, MAPA_LARGURA) 
                                    if not player_desl[0]-300 <= n <= player_desl[0]+300])
        spawnY = rand.choice([n for n in range(0, MAPA_ALTURA) 
                                    if not player_desl[1]-300 <= n <= player_desl[1]+300])
        return (spawnX, spawnY)

class GameOver(ecras.Ecra):
    def criar_sprites(self):
        super().criar_sprites()
        self.botoes = pg.sprite.Group()

        self.menu = PGutilitarios.Botao(lambda : self.jogo.mudar_ecra("menu"), (self.largura//2 -100, self.altura//2 +130), BOTAO_MENU,
                                        escala=0.4, aumt_select=True, groups=[self.botoes, self.todas_sprites])

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
        self.tela.fill(PRETO)
        PGutilitarios.mostrar_imagem(self.tela, FUNDO_GAMEOVER, self.largura//2, self.altura//2)
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
        if self.altura_credits < -800:
            self.altura_credits = self.altura + 781

    def desenhar(self):
        super().desenhar()
        PGutilitarios.mostrar_imagem(self.tela, CREDITS, self.largura//2, self.altura_credits,
                                     self.jogo.escala)

jogo = Zombie()
jogo.loop()
pg.quit()

# ATUALIZAÇÕES:
# - Adicionar mais monstros
# - Adicionar sons ao jogo
# - Configurações (options)
# - Tela de pause
# - Melhorar a IA dos inimigos

# Otimizações / BUGS:
# 4. Evitar alocações frequentes de Vector2 e Surface
# 5. Otimizar testes de máscara (per-pixel)
# 6. Evitar loops desnecessários ao spawnar e atualizar

# Bugs no Mapa das estruturas