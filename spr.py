import pygame as pg
from pygame.locals import *

from constantes import *

class Mapa(pg.sprite.Sprite):
    def __init__(self, ecra, arq: str, *groups) -> None:
        super().__init__(ecra.todas_sprites, groups)
        self.ecra = ecra
        self.image = pg.image.load(arq).convert_alpha()
        self.rect = self.image.get_rect()
        self.desl = pg.Vector2(0, 0)
        self.rect.center = ecra.centro_mapa

    def update(self) -> None:
        self.rect.center = self.ecra.centro_mapa

class Personagem(pg.sprite.Sprite):
    def __init__(self, ecra, desl: tuple, vida: int, arq_spritesheet: str,
                 tam_img: tuple, quant_imgs: int, estados: dict, groups: list=[]) -> None:
        super().__init__(ecra.todas_sprites, ecra.personagens, *groups)

        self.ecra = ecra
        self.spritesheet = pg.image.load(arq_spritesheet).convert_alpha()

        self.imagens = self.get_imagens(self.spritesheet, tam_img, quant_imgs)
        self.imagens = self.organizar_imagens(estados)

        self.image = self.imagens["parado"][0][1]
        self.rect = self.image.get_rect()
        self.desl = pg.Vector2(desl)
        self.rect.center = ecra.centro_mapa + self.desl

        self.vivo = True
        self.vida = vida
        self.atual = 0
        self.estado = "parado"
        self.lado = 1  # 0: esquerda, 1: direita

    def get_imagens(self, spritesheet: pg.Surface, tam_img: tuple, quant_imgs: int) -> list:
        colunas = int(quant_imgs**0.5)
        linhas = colunas + (1 if quant_imgs % colunas != 0 else 0)
        imagens = []

        for linha in range(linhas):
            for coluna in range(colunas):
                if len(imagens) < quant_imgs:
                    x = coluna * tam_img[0]
                    y = linha * tam_img[1]
                    imagem = spritesheet.subsurface((x, y), tam_img)
                    imagens.append(imagem)
                else:
                    break
        return imagens
    
    def organizar_imagens(self, estados: dict) -> dict:
        imagens_organizadas = {}
        indice = 0

        for estado, quantidade in estados.items():
            imagens_organizadas[estado] = []
            for _ in range(quantidade):
                imgs_estado = [pg.transform.flip(self.imagens[indice], True, False), self.imagens[indice]]
                imagens_organizadas[estado].append(imgs_estado)
                indice += 1
        return imagens_organizadas
    
    def atualizar_pos(self) -> None:
        self.rect.center = self.ecra.centro_mapa + self.desl
        
    def morrer(self):
        if self.vida <= 0:
            self.estado = 'morrendo'
        
    def movimentar(self) -> None:
        pass

    def direcionar(self) -> None:
        pass

    def atualizar_img(self) -> None:
        pass

class Player(Personagem):
    def __init__(self, ecra, pos: tuple) -> None:
        estados = {
            "correndo": 11,
            "atirando_correndo": 8,
            "morrendo": 5,
            "atirando_parado": 1,
            "parado": 1
        }
        super().__init__(ecra, pos, PLAYER_VIDA, PLAYER_SPRITESHEET,
                         (80, 80), 26, estados)
        
        self.atirando = False
        self.contador_tpf = 0
        
    def update(self):
        if self.vivo:
            pressionados = pg.key.get_pressed()
            pos_mouse = pg.mouse.get_pos()
            press_mouse = pg.mouse.get_pressed()

            # MOVER PERSONAGEM
            direcao = pg.Vector2(0, 0)
            for tecla, vetor in DIRECOES.values():
                if any(pressionados[k] for k in tecla):
                    direcao += pg.Vector2(vetor)

            if direcao.length() != 0:
                direcao = direcao.normalize()

            # verificar colisão
            '''
            vel = PLAYER_VEL_ATIRANDO if self.atirando else PLAYER_VEL
            rect_colisor = pg.Rect(0, 0, self.rect.width//2, self.rect.height//4)
            rect_colisor.bottomleft = (self.rect.left +20, self.rect.bottom -20)
            rect_colisor.x += direcao.x * vel
            rect_colisor.y += direcao.y * vel
            if not any([True for colisor in self.ecra.colisores
                        if colisor.colliderect(rect_colisor)]):
                self.desl += direcao * vel
                self.ecra.centro_mapa = pg.Vector2(self.ecra.largura//2, self.ecra.altura//2) -self.desl
                for i, colisor in enumerate(self.ecra.colisores):
                    colisor.center = (self.ecra.centro_mapa - pg.Vector2(937, 937)) + pg.Vector2(self.ecra.COLISORES[1].topleft)'''

            # ATIRAR
            '''
            if press_mouse[0]:
                self.atirando = True
                if self.contador_tpf >= 1:
                    pos = (self.rect.left +10, self.rect.centery +9) if self.lado == 0 else (self.rect.right -10, self.rect.centery +9)
                    Tiro(self.ecra, pos, pos_mouse)
                    self.contador_tpf -= 1
                else:
                    self.contador_tpf += TPF
            else:
                self.atirando = False
                self.contador_tpf = 0'''

            # ATUALIZAR IMAGEM
            self.morrer()
            # estado
            self.estado_atual = self.estado
            if self.estado == "morrendo":
                pass
            if self.atirando:
                if direcao.length() != 0:
                    self.estado = "atirando_correndo"
                else:
                    self.estado = "atirando_parado"
            else:
                if direcao.length() != 0:
                    self.estado = "correndo"
                else:
                    self.estado = "parado"
                    
            # lado
            if self.atirando:
                self.lado = 0 if pos_mouse[0] < self.rect.centerx else 1
            else:
                self.lado = 0 if direcao.x < 0 else 1 if direcao.x > 0 else self.lado
                
            # imagem
            self.atual += 0.5
            if self.atual >= len(self.imagens[self.estado]) or self.estado != self.estado_atual:
                self.atual = 0
                
                # Morrer
                if self.estado == 'morrendo':
                    self.morto = True

            self.image = self.imagens[self.estado][int(self.atual)][self.lado]

class Tanque(Personagem):
    def __init__(self, ecra, pos: tuple) -> None:
        estados = {
            "parado": 1,
            "andando": 5,
            "atacando": 8,
            "morrendo": 4
        }
        super().__init__(ecra, pos, TANQUE_VIDA, TANQUE_SPRITESHEET,
                         (80, 80), 18, estados, [ecra.inimigos])
        
        self.dano = TANQUE_DANO
        
    def update(self):
        if self.vivo:
            player = self.ecra.player
            dist_player = pg.Vector2(self.rect.center).distance_to(pg.Vector2(player.rect.center))
            
            # MOVER PERSONAGEM
            direcao = pg.Vector2(player.rect.center) - pg.Vector2(self.rect.center)

            if direcao.length() != 0:
                direcao = direcao.normalize()
                
            self.desl += direcao * TANQUE_VEL
            self.atualizar_pos()

            # ATUALIZAR IMAGEM
            self.morrer()
            # estado
            estado_atual = self.estado
            if self.estado == "morrendo":
                pass
            elif dist_player > TANQUE_ALCANCE:
                self.estado = "andando"
            else:
                self.estado = "atacando"
                    
            # lado
            self.lado = 1 if self.rect.centerx < player.rect.centerx else 0

            # imagem
            self.atual += 0.3
            if self.atual >= len(self.imagens[self.estado]) or self.estado != estado_atual:
                self.atual = 0
                
                # Dar dano ao atacar
                if self.estado == 'atacando':
                    player.vida -= self.dano

                # Morrer
                if self.estado == 'morrendo':
                    self.morto = True

            self.image = self.imagens[self.estado][int(self.atual)][self.lado]

class Tiro(pg.sprite.Sprite):
    def __init__(self, ecra, pos: tuple, destino: tuple) -> None:
        super().__init__(ecra.todas_sprites, ecra.tiros)

        self.ecra = ecra
        self.image = pg.Surface((5, 5))
        self.image.fill(AMARELO)
        self.rect = self.image.get_rect()
        self.rect.center = pg.Vector2(pos)
        
        self.destino = pg.Vector2(destino)
        self.velocidade = pg.Vector2(self.calcular_vel())

    def calcular_vel(self) -> tuple:
        direcao = self.destino - pg.Vector2(self.rect.center)
        if direcao.length() != 0:
            direcao = direcao.normalize()
        vel_x = direcao.x * TIRO_VEL
        vel_y = direcao.y * TIRO_VEL
        return (vel_x, vel_y)
    
    def update(self) -> None:
        # Movimentar o tiro
        self.rect.x += self.velocidade.x
        self.rect.y += self.velocidade.y

        # Verificar colisão
        if not self.ecra.mapa.rect.colliderect(self.rect):
            self.kill()
        for inimigo in pg.sprite.spritecollide(self, self.ecra.inimigos, False):
            inimigo.vida -= TIRO_DANO
            if inimigo.vida <= 0:
                inimigo.vivo = False
            self.kill()