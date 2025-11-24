import pygame as pg
from pygame.locals import *

from constantes import *

class Mapa(pg.sprite.Sprite):
    def __init__(self, pos, arquivo: str, *groups):
        super().__init__(groups)

        self.image = pg.image.load(arquivo).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = pos

class Personagem(pg.sprite.Sprite):
    def __init__(self, ecra, spritesheet: str, div_spr: tuple, org_spr: dict,
                  pos: tuple, vida: int, *groups) -> None:
        super().__init__(groups)
        self.ecra = ecra

        self.spritesheet = pg.image.load(spritesheet).convert_alpha()
        self.imagens = {'direita': {}, 'esquerda': {}}

        sprites = self.dividir_spritesheet(self.spritesheet, div_spr)
        self.organizar_sprites(sprites, org_spr)

        self.image = self.imagens['direita']['parado'][0]
        self.rect = self.image.get_rect()

        self.desl = list(pos)
        self.rect.center = (self.ecra.mapa_centro[0]+self.desl[0], self.ecra.mapa_centro[1]+self.desl[1])

        self.vida = vida
        self.direcao = 'direita'
        self.estado = 'parado'
        self.atual = 0
        self.atirando = False
        self.morto = False

    def dividir_spritesheet(self, spritesheet, div_spr: tuple) -> None:
        w, h, n_imgs = div_spr
        r = int(n_imgs**0.5)
        linhas, colunas = r + (1 if r**2 != n_imgs else 0), r
        sprites = []
        for linha in range(linhas):
            for coluna in range(colunas):
                if len(sprites) < n_imgs:
                    spr = spritesheet.subsurface(coluna*w, linha*h, w, h)
                    sprites.append(spr)
                else:
                    break

        return sprites
    
    def organizar_sprites(self, sprites: list, estados: dict) -> None:
        for direcao in self.imagens:
            self.imagens[direcao] = {}
            for estado, pos in estados.items():
                self.imagens[direcao][estado] = []
                for n_spr in range(pos[0], pos[1]):
                    sprite = sprites[n_spr]
                    if direcao == 'esquerda':
                        sprite = pg.transform.flip(sprite, True, False)
                    self.imagens[direcao][estado].append(sprite)

    def update(self):
        super().update()
        # Morrer
        if self.vida <= 0 and self.estado != 'morrendo':
            self.estado, self.atual = 'morrendo', 0

    def atualizar_pos(self) -> None:
        self.rect.center = (self.ecra.mapa_centro[0]+self.desl[0], self.ecra.mapa_centro[1]+self.desl[1])

    def movimentar(self) -> None:
        pass

    def direcionar(self) -> None:
        pass

    def atualizar_img(self) -> None:
        pass

class Player(Personagem):
    def __init__(self, ecra, spritesheet: str, div_spr: tuple, org_spr: dict,
                  pos: tuple, vida: int) -> None:
        super().__init__(ecra, spritesheet, div_spr, org_spr, pos, vida, ecra.todas_sprites)
        
    def update(self) -> None:
        self.atualizar_pos()
        if not self.morto:
            super().update()
            pos_mouse = pg.mouse.get_pos()
            precionados = pg.key.get_pressed()
            pres_mouse = pg.mouse.get_pressed()

            self.atirando = True if pres_mouse[0] else False

            # Movimentação
            if self.estado == 'morrendo':
                pass
            elif (precionados[K_a] or precionados[K_LEFT]) and (precionados[K_d] or precionados[K_RIGHT]):
                self.estado, self.atual = 'atacando' if self.atirando else 'parado', 0
            elif any([precionados[tecla] for tecla in (K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN, K_RIGHT)]):
                # Controle do estado de atirar
                if self.atirando:
                    if self.estado != 'caminhando':
                        self.estado, self.atual = 'caminhando', 0
                # Controle do entado de correr
                else:
                    if self.estado != 'correndo':
                        self.estado, self.atual = 'correndo', 0
            else:
                self.estado, self.atual = 'atacando' if self.atirando else 'parado', 0

            # Controle de direção
            if self.atirando:
                if pos_mouse[0] < self.ecra.largura//2:
                    self.direcao = 'esquerda'
                else:
                    self.direcao = 'direita'
            elif self.estado == 'parado':
                pass
            elif precionados[K_a] or precionados[K_LEFT]:
                self.direcao = 'esquerda'
            elif precionados[K_d] or precionados[K_RIGHT]:
                self.direcao = 'direita'

            self.image = self.imagens[self.direcao][self.estado][int(self.atual)]

            if self.estado == 'morrendo':
                self.atual += 0.2
            elif self.atirando:
                self.atual += VEL_ATIRANDO/8
            else:
                self.atual += VEL_PLAYER/8
            if int(self.atual) > len(self.imagens[self.direcao][self.estado])-1:
                self.atual = 0

                # Morrer
                if self.estado == 'morrendo':
                    self.morto = True
                    self.ecra.gameover.rodar()

class Rapido(Personagem):
    def __init__(self, ecra, spritesheet: str, div_spr: tuple, org_spr: dict,
     pos: tuple, vida: int) -> None:
        super().__init__(ecra, spritesheet, div_spr, org_spr, pos, vida,
         ecra.todas_sprites, ecra.inimigos)

class Tanque(Personagem):
    def __init__(self, ecra, spritesheet: str, div_spr: tuple, org_spr: dict,
     pos: tuple, vida: int) -> None:
        super().__init__(ecra, spritesheet, div_spr, org_spr, pos, vida,
         ecra.todas_sprites, ecra.inimigos)

        self.dano = DANO_TANQUE

    def update(self):
        self.atualizar_pos()
        if not self.morto:
            super().update()

            player = self.ecra.player
            dist_player = calc_dist(self.rect.center, player.rect.center)

            # Definir estado e mover
            if self.estado == 'morrendo':
                pass
            elif dist_player > 40:
                velx, vely = calc_movimento(self.rect.center, player.rect.center, VEL_TANQUE)
                self.desl[0] += velx
                self.desl[1] += vely
                if self.estado != 'caminhando':
                    self.estado, self.atual = 'caminhando', 0
            elif self.estado != 'atacando':
                self.estado, self.atual = 'atacando', 0

            # Definir direção
            dir = 'esquerda' if self.rect.centerx > player.rect.centerx else 'direita'

            # Atualizar imagem
            self.image = self.imagens[dir][self.estado][int(self.atual)]
            self.atual += VEL_TANQUE/8
            if int(self.atual) > len(self.imagens[dir][self.estado])-1:
                self.atual = 0

                # Dar dano ao atacar
                if self.estado == 'atacando':
                    player.vida -= self.dano

                # Morrer
                if self.estado == 'morrendo':
                    self.morto = True
        else:
            self.atual += 1
            if self.atual >= 50:
                self.kill()

class Tiro(pg.sprite.Sprite):
    def __init__(self, ecra, origem: tuple, destino: tuple, *groups) -> None:
        super().__init__(groups)
        self.ecra = ecra
        self.origem = origem
        self.destino = destino

        self.image = pg.Surface((5, 5))
        self.image.fill((220, 220, 0))
        self.rect = self.image.get_rect()
        self.rect.center = origem

        self.velx, self.vely = calc_movimento(self.origem, self.destino, VEL_TIRO)
        self.distancia = calc_dist(self.origem, self.destino)

    def update(self):
        self.rect.x += self.velx
        self.rect.y += self.vely

        # Some quando atinge o limite da distância
        dist_atual = calc_dist(self.origem, self.rect.center)
        if dist_atual > abs(self.distancia):
            self.kill()

        # Dar dano
        for inimigo in self.ecra.inimigos:
            if self.rect.colliderect(inimigo.rect) and not inimigo.morto:
                inimigo.vida -= DANO_TIRO
                self.kill()
                break

class Botao(pg.sprite.Sprite):
    def __init__(self, pos=tuple, botao=str, reverso=False):
        super().__init__()

        spritesheet = pg.image.load(SPRITESHEET_BOTOES).convert_alpha()
        self.parados = spritesheet.subsurface((14, 15), (313, 150))
        self.precionados = spritesheet.subsurface((14, 189), (313, 150))

        self.cordenadas = {
            'settings': ((0, 0), (97, 44)),
            'pessoa': ((163, 0), (44, 44)),
            'bandeira': ((110, 0), (44, 44)),
            'pause': ((216, 0), (97, 44)),
            'play': ((0, 52), (71, 44)),
            'menu': ((79, 52), (76, 44)),
            'seta': ((163, 52), (44, 44)),
            'certo': ((216, 52), (44, 44)),
            'errado': ((269, 52), (44, 44)),
            'exit': ((79, 104), (76, 45)),
            'som': ((216, 104), (44, 44)),
        }

        self.precionado = False
        self.botao_parado = self.parados.subsurface(self.cordenadas[botao][0], self.cordenadas[botao][1])
        self.botao_precionado = self.precionados.subsurface(self.cordenadas[botao][0], self.cordenadas[botao][1])

        if reverso:
            self.botao_parado = pg.transform.flip(self.botao_parado, True, False)
            self.botao_precionado = pg.transform.flip(self.botao_precionado, True, False)

        self.image = self.botao_parado
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def funcionar(self):
        pass

    def pressionar(self):
        self.precionado = True
        self.image = self.botao_precionado

    def despressionar(self):
        self.precionado = False
        self.image = self.botao_parado