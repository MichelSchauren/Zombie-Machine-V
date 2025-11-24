import pygame as pg
import os
import json
from sys import exit

# Flags
SCROLLX = 2
SCROLLY = 4
ZOOM = 1

# Janela principal do seu jogo. Dentro dela será mostrado os ecras.
class Jogo:
    def __init__(self, titulo: str, largura: int, altura: int, escala=1, fps=15, fonte="consolas") -> None:
        self.fps = fps
        self.escala = escala
        self.largura_padrao = largura
        self.altura_padrao = altura
        self.largura = self.largura_padrao*self.escala
        self.altura = self.altura_padrao*self.escala
        self.tela = pg.display.set_mode((self.largura, self.altura), pg.RESIZABLE)
        self.titulo = pg.display.set_caption(titulo)
        self.fonte = fonte
        self.relogio = pg.time.Clock()
        self.rodando = True

        # Com os registros você pode armazenar informações em arquivos json
        self.registros = {
        #   registro = carregar_registro( >caminho< ), 
        }

        self.ecras = {
            "menu": Menu(self),
        }
        self.ecra_atual = self.ecras["menu"]

    def salvar_registro(self, caminho: str, registro) -> None:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(registro, f, ensure_ascii=False, indent=2)

    def carregar_registro(self, caminho: str) -> None:
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)

    def mudar_ecra(self, nome) -> None:
        self.ecra_atual = self.ecras[nome]
        self.ecra_atual.__init__(self)

    def loop(self) -> None:
        while self.rodando:
            self.eventos = pg.event.get()
            self.ecra_atual.eventos()
            self.ecra_atual.atualizar()
            self.ecra_atual.desenhar()

            pg.display.flip()
            self.relogio.tick(self.fps)

# Ecrã é uma tela/superfície que conterá os elementos do jogo.
class Ecra:
    def __init__(self, jogo, *flags) -> None:
        self.flags = flags
        if len(flags) >= 2:
            self.sx = 0
            self.sy = 0
            self.pos_mouse = pg.mouse.get_pos()
        if len(flags) % 2 == 1:
            self.zoom = 1

        self.jogo = jogo
        self.largura = self.jogo.largura
        self.altura = self.jogo.altura
        self.tela = self.jogo.tela
        self.fundo = (0, 0, 0)
        self.criar_sprites()

    def criar_sprites(self) -> None:
        self.todas_sprites = pg.sprite.Group()

    def eventos(self) -> None:
        for event in self.jogo.eventos:
            self.eventos_padrao(event)

    def eventos_padrao(self, event) -> None:
        if event.type == pg.QUIT:
            self.jogo.rodando = False
            pg.quit()
            exit()

        if event.type == pg.VIDEORESIZE:
            self.jogo.largura = pg.display.get_window_size()[0]
            self.jogo.altura = pg.display.get_window_size()[1]
            self.jogo.tela = pg.display.set_mode((self.jogo.largura, self.jogo.altura), pg.RESIZABLE)
            self.jogo.escala = self.jogo.altura/self.jogo.altura_padrao
            self.jogo.ecra_atual.__init__(self.jogo)

        # Movimentar a tela
        if sum(self.flags) >= 2 and event.type == pg.MOUSEMOTION:
            x = event.pos[0]
            y = event.pos[1]
            precionado = pg.mouse.get_pressed()

            if precionado[2]:
                self.sx += x - self.pos_mouse[0] if SCROLLX in self.flags else 0
                self.sy += y - self.pos_mouse[1] if SCROLLY in self.flags else 0
            self.pos_mouse = event.pos

        # Dar zoom
        if len(self.flags) % 2 == 1 and event.type == pg.MOUSEWHEEL:
            if 0 < self.zoom + event.y < 10:
                self.zoom += event.y

    def atualizar(self) -> None:
        self.todas_sprites.update()

    def desenhar(self) -> None:
        self.tela.fill(self.fundo)
        self.todas_sprites.draw(self.tela)

# A diferença para um ecrã normal é que roda com um loop próprio, volta para o ecrã passado quando self.rodando=False.
class SubEcra(Ecra):
    def __init__(self, ecra) -> None:
        super().__init__(ecra.jogo)
        self.ecra = ecra

    def eventos_padrao(self, event) -> None:
        super().eventos_padrao(event)
        print('*')

        if event.type == pg.VIDEORESIZE:
            self.__init__(self.ecra)

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.rodando = False

    def desenhar(self) -> None:
        self.ecra.desenhar()
        self.todas_sprites.draw(self.tela)

    def rodar(self) -> None:
        self.__init__(self.ecra)
        self.rodando = True
        while self.rodando:
            self.eventos()
            self.atualizar()
            self.desenhar()

            pg.display.flip()
            self.jogo.relogio.tick(self.jogo.fps)

# Um exemplo de ecrã é o menu do jogo.
class Menu(Ecra):
    pass