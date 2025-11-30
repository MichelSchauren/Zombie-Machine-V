import pygame as pg
from pygame.locals import *

from constantes import *

class Mapa(pg.sprite.Sprite):
    def __init__(self, mapa_rect, arquivo: str, *groups):
        super().__init__(groups)
        self.mapa_rect = mapa_rect

        self.image = pg.image.load(arquivo).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = mapa_rect.topleft

    def update(self):
        self.rect.topleft = self.mapa_rect.topleft

class Personagem(pg.sprite.Sprite):
    def __init__(self, ecra, spritesheet: str, div_spr: tuple, org_spr: dict,
                  desl: tuple, vida: int, *groups) -> None:
        super().__init__(groups, ecra.personagens, ecra.todas_sprites)
        self.ecra = ecra

        self.spritesheet = pg.image.load(spritesheet).convert_alpha()
        self.imagens = {'direita': {}, 'esquerda': {}}

        sprites = self.dividir_spritesheet(self.spritesheet, div_spr)
        self.organizar_sprites(sprites, org_spr)

        self.image = self.imagens['direita']['parado'][0]

        self.rect = self.image.get_rect()
        self.rect_map = self.image.get_rect()
        self.rect_colid = pg.Rect(0, 0, self.rect.width//2, self.rect.height//4)

        self.rect_map.center = desl
        self.rect_colid.midbottom = self.rect_map.midbottom
        self.rect.topleft = (self.ecra.mapa_rect.x + self.rect_map.x, self.ecra.mapa_rect.y + self.rect_map.y)

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
        self.rect_colid.midbottom = self.rect_map.midbottom
        self.rect.topleft = (self.ecra.mapa_rect.x + self.rect_map.x, self.ecra.mapa_rect.y + self.rect_map.y)

    def movimentar(self) -> None:
        pass

    def direcionar(self) -> None:
        pass

    def atualizar_img(self) -> None:
        pass

class Player(Personagem):
    def __init__(self, ecra, desl: tuple) -> None:
        
        spritesheet = PLAYER_SPRITESHEET
        div_spr = (80, 80, 26)
        org_spr = {'correndo': (0, 11), 'caminhando': (11, 19), 'morrendo': (19,24),
                              'atacando': (24, 25), 'parado': (25, 26)}
        vida = PLAYER_VIDA
        
        super().__init__(ecra, spritesheet, div_spr, org_spr, desl, vida)
        
    def update(self) -> None:
        self.atualizar_pos()
        if not self.morto:
            super().update()
            pos_mouse = pg.mouse.get_pos()
            precionados = pg.key.get_pressed()
            pres_mouse = pg.mouse.get_pressed()

            self.atirando = True if pres_mouse[0] else False

            # Controle de estados
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
                if pos_mouse[0] < self.rect.centerx:
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
                self.atual += PLAYER_VEL_ATIRANDO/8
            else:
                self.atual += PLAYER_VEL/8
            if int(self.atual) > len(self.imagens[self.direcao][self.estado])-1:
                self.atual = 0

                # Morrer
                if self.estado == 'morrendo':
                    self.morto = True
                    
        else:
            self.atual += 1
            if self.atual >= 30:
                self.ecra.jogo.mudar_ecra("gameover")

class Rapido(Personagem):
    def __init__(self, ecra, desl: tuple) -> None:
        super().__init__()

class Tanque(Personagem):
    def __init__(self, ecra, desl: tuple) -> None:
        
        spritesheet = TANQUE_SPRITESHEET
        div_spr = (80, 80, 18)
        org_spr = {'parado': (0, 1), 'caminhando': (1, 6), 'atacando': (6, 14), 'morrendo': (14, 18)}
        vida = TANQUE_VIDA
        self.dano = TANQUE_DANO

        super().__init__(ecra, spritesheet, div_spr, org_spr, desl, vida, ecra.inimigos)   

    def update(self):
        self.atualizar_pos()

        if not self.morto:
            super().update()

            player = self.ecra.player
            dist_player = pg.Vector2(self.rect.center).distance_to(pg.Vector2(player.rect.center))

            # Definir estado e mover
            # Não mover quando estiver morto
            if self.estado == 'morrendo':
                pass
            # Mover quando estiver a mais de 40 pixels de distancia do player
            elif dist_player > TANQUE_ALCANCE:
                direcao = pg.Vector2(player.rect.center) - pg.Vector2(self.rect.center)
                if direcao.length() != 0: direcao = direcao.normalize()
                velx, vely = direcao.x * TANQUE_VEL, direcao.y * TANQUE_VEL
                
                # Verificar colisão antes de mover
                colisor = self.rect_colid.move(velx, vely)
                possiveis = self.ecra.grid.query(colisor)
                if not any(colisor.colliderect(r) for r in possiveis): # Não colidiu
                    self.rect_map.move_ip(velx, vely)
                    if self.estado != 'caminhando':
                        self.estado, self.atual = 'caminhando', 0
                elif self.estado != 'parado': # colidiu
                    self.estado, self.atual = 'parado', 0

            # atacar quando estiver próximo ao player
            elif self.estado != 'atacando':
                self.estado, self.atual = 'atacando', 0

            # Definir direção
            dir = 'esquerda' if self.rect.centerx > player.rect.centerx else 'direita'

            # Atualizar imagem
            self.image = self.imagens[dir][self.estado][int(self.atual)]
            self.atual += TANQUE_VEL/8
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
    def __init__(self, ecra, desl: tuple, destino: tuple, *groups) -> None:
        super().__init__(groups)
        self.ecra = ecra

        self.image = pg.Surface((5, 5))
        self.image.fill(AMARELO)
        self.rect = self.image.get_rect()
        self.rect.center = (self.ecra.mapa_rect.x + desl[1], self.ecra.mapa_rect.y + desl[1])

        self.origem = self.rect.center
        self.destino = destino

        self.mov = pg.Vector2(pg.Vector2(destino) - pg.Vector2(desl))
        self.mov = self.mov.normalize() * TIRO_VEL

        self.rect_map = self.rect.copy()
        self.rect_map.center = desl
    
    def update(self):
        self.rect_map.move_ip(self.mov.x, self.mov.y)
        
        # Some quando colide ou sai do mapa
        possiveis = self.ecra.grid.query(self.rect_map)
        if not 0 <= self.rect_map.centerx <= MAPA_LARGURA or not 0 <= self.rect_map.centery <= MAPA_ALTURA  or \
            any(self.rect_map.colliderect(r) for r in possiveis):
            self.kill()

        # Dar dano
        for inimigo in self.ecra.inimigos:
            if not inimigo.morto and self.rect_map.colliderect(inimigo.rect_map) and pg.sprite.collide_mask(self, inimigo):
                inimigo.vida -= TIRO_DANO
                self.kill()
                break
        self.atualizar_pos()

    def atualizar_pos(self) -> None:
        self.rect.topleft = (self.ecra.mapa_rect.x + self.rect_map.x, self.ecra.mapa_rect.y + self.rect_map.y)

        