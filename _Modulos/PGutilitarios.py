import pygame as pg
import os

# Funções utilitárias para Pygame
def mostrar_imagem(surface, caminho, x, y, escala: float=1) -> None:
        imagem = pg.image.load(caminho).convert_alpha()
        imagem = pg.transform.scale(imagem, (int(imagem.get_width()*escala),
                                             int(imagem.get_height()*escala)))
        imagem_rect = imagem.get_rect()
        imagem_rect.center = (x, y)
        surface.blit(imagem, imagem_rect)

def mostrar_texto(surface, mensagem=str, x=None, y=None,
                      cor=(0, 0, 0), tam=32, fonte="arial",
                      espacamento=10, bold=False, center=False) -> None:
        x = surface.get_width()//2 if x is None else int(x)
        y = surface.get_height()//2 if y is None else int(y)
        font = pg.font.match_font(fonte)
        font = pg.font.Font(font, tam)
        font.set_bold(bold)
        linhas = mensagem.split('\n')
        for i, linha in enumerate(linhas):
            texto = font.render(linha, True, cor)
            texto_rect = texto.get_rect()
            if center:
                texto_rect.center = (x, y + i*(tam+espacamento))
            else:
                texto_rect.topleft = (x, y + i*(tam+espacamento))
            surface.blit(texto, texto_rect)

# Objetos úteis para interfaces gráficas
class Caixa_Texto():
    def __init__(self, x: int, y: int, largura_min: int, fonte: str, tam: int, texto="", cor_texto=(0, 0, 0), cor_fundo=None, contorno=1, border_radius=5, padding=5, max_len=20):
        self.x = x
        self.y = y
        self.largura_min = largura_min
        self.texto = texto
        self.fonte = pg.font.SysFont(fonte, tam)
        self.cor_texto = cor_texto
        self.cor_fundo = cor_fundo
        self.contorno = contorno
        self.border_radius = border_radius
        self.padding = padding
        self.max_len = max_len
        self.cursor_pos = len(self.texto)
        self.selecionado = False
        self.criar_superficie()

    def criar_superficie(self, surface=None):
        if type(surface) == Superficie:
            fonte_escalada = pg.font.SysFont('consolas', surface.tranform_tam(self.fonte.get_height()))
            self.superficie = fonte_escalada.render(self.texto, True, self.cor_texto, self.cor_fundo)
        else:
            self.superficie = self.fonte.render(self.texto, True, self.cor_texto, self.cor_fundo)
        self.rect_texto = self.superficie.get_rect(topleft=(self.x, self.y))
        self.rect = pg.Rect(self.rect_texto.x - self.padding, self.rect_texto.y - self.padding, max(self.largura_min, self.rect_texto.width + self.padding*2), self.rect_texto.height + self.padding*2)

        # Calcula a posição X do cursor
        texto_ate_cursor = self.texto[:self.cursor_pos]
        superficie_cursor = self.fonte.render(texto_ate_cursor, True, self.cor_texto, self.cor_fundo)
        cursor_x = self.x + superficie_cursor.get_width()
        self.cursor_rect = pg.Rect(cursor_x, self.y, 2, self.rect_texto.height)
        
    def eventos(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.selecionado = True
            else:
                self.selecionado = False

        if event.type == pg.KEYDOWN and self.selecionado:
            if event.key == pg.K_RETURN:
                self.selecionado = False
            elif event.key == pg.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.texto = self.texto[:self.cursor_pos-1] + self.texto[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pg.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos -1)
            elif event.key == pg.K_RIGHT:
                self.cursor_pos = min(len(self.texto), self.cursor_pos +1)
            elif len(self.texto) < self.max_len:
                self.texto = self.texto[:self.cursor_pos] + event.unicode + self.texto[self.cursor_pos:]
                self.cursor_pos += 1
            self.criar_superficie()

    def desenhar(self, surface):
        surface.blit(self.superficie, self.rect_texto)
        if type(surface) == Superficie:
            self.criar_superficie(surface)
            if self.contorno > 0: surface.draw_rect((0, 0, 0), self.rect, self.contorno if not self.selecionado else 1, self.border_radius)
            if self.selecionado: surface.draw_rect(self.cor_texto, self.cursor_rect)
        else:
            if self.contorno > 0: pg.draw.rect(surface, (0, 0, 0), self.rect, self.contorno if not self.selecionado else 1, self.border_radius)
            if self.selecionado: pg.draw.rect(surface, self.cor_texto, self.cursor_rect)

class Barra:
    def __init__(self, pos: tuple, largura: int, altura: int, niveis: list, nivel_atual: int, cor=(255, 255, 255), mostrar_niveis=True):
        self.rect = pg.Rect(pos[0], pos[1], largura, altura)
        self.rect_escalado = self.rect.copy()
        self.largura = largura
        self.altura = altura
        self.cor = cor
        self.raio_circulos = altura//12
        self.mostrar_niveis = mostrar_niveis

        self.espacamento = largura/(len(niveis)-1)
        self.niveis = niveis
        self.nivel_atual = nivel_atual

        self.fonte = pg.font.SysFont('consolas', altura//4, True)

    def atualizar(self):
        precionado = pg.mouse.get_pressed()
        pos_mouse = pg.mouse.get_pos()

        if precionado[0] and self.rect_escalado.collidepoint(pos_mouse):
            for n in range(len(self.niveis)):
                posX = int(n*self.espacamento) + self.rect.x
                if posX - self.espacamento//2 <= pos_mouse[0] < posX + self.espacamento//2:
                    self.nivel_atual = n

        return self.niveis[self.nivel_atual]

    def desenhar(self, surface):
        if type(surface) == Superficie:
            surface.transform_rect(self.rect, self.rect_escalado)
            surface.draw_line(self.cor, self.rect.midleft, self.rect.midright, self.altura//20)

            # desenhar niveis   
            if self.mostrar_niveis:  
                for i, _ in enumerate(self.niveis):
                    posX = int(i*self.espacamento) + self.rect.x
                    surface.draw_circle(self.cor, (posX, self.rect.centery), self.raio_circulos)

            # desenhar nivel atual
            posX_atual = int(self.nivel_atual*self.espacamento) + self.rect.x
            fonte_escalada = pg.font.SysFont('consolas', surface.tranform_tam(self.fonte.get_height()), True)
            texto = fonte_escalada.render(self.niveis[self.nivel_atual], True, self.cor)
            texto_rect = texto.get_rect()
            texto_rect.midbottom = (posX_atual, self.rect.bottom)

            surface.draw_circle(self.cor, (posX_atual, self.rect.centery), self.raio_circulos*2)
            surface.blit(texto, texto_rect)
        else:
            pg.draw.line(surface, self.cor, self.rect.midleft, self.rect.midright, self.altura//20)   
            
            # desenhar niveis   
            if self.mostrar_niveis:  
                for i, _ in enumerate(self.niveis):
                    posX = int(i*self.espacamento) + self.rect.x
                    pg.draw.circle(surface, self.cor, (posX, self.rect.centery), self.raio_circulos)

            # desenhar nivel atual
            posX_atual = int(self.nivel_atual*self.espacamento) + self.rect.x
            texto = self.fonte.render(self.niveis[self.nivel_atual], True, self.cor)
            texto_rect = texto.get_rect()
            texto_rect.midbottom = (posX_atual, self.rect.bottom)

            pg.draw.circle(surface, self.cor, (posX_atual, self.rect.centery), self.raio_circulos*2)
            surface.blit(texto, texto_rect)

class Superficie(pg.Surface):
    def __init__(self, x: int, y: int, largura: int, altura: int, cor: tuple=(0, 0, 0), zoom: int=-1) -> None:
        super().__init__((largura, altura))
        self.rect = pg.Rect(x, y, largura, altura)
        self.cor = cor

        self.offset_x = 0
        self.offset_y = 0
        self.zoom = zoom

        self.limite_x = largura//2
        self.limite_y = altura//2
        self.limite_zoom = 10

        self.pos_mouse = pg.mouse.get_pos()
        
    def blit(self, source, dest, area = None, special_flags = 0) -> None:
        super().blit(self.transform_surface(source), self.transform_rect(dest), self.transform_rect(area), special_flags)
        
    def eventos(self, event) -> None:
        # Sistema de zoom
        if event.type == pg.MOUSEWHEEL and self.rect.collidepoint(self.pos_mouse):
            if event.precise_y > 0 and self.zoom < self.limite_zoom:
                self.zoom += 0.1
            elif event.precise_y < 0 and self.zoom > 0.1:
                self.zoom -= 0.1

    def atualizar(self, scroll_x: bool=True, scroll_y: bool=True, zoom_ativo: bool=True) -> None:
        teclas_press = pg.key.get_pressed()
        mouse_press = pg.mouse.get_pressed()

        # Mover com as teclas do teclado
        if teclas_press[pg.K_LEFT] and self.offset_x < self.limite_x and scroll_x:
            self.offset_x += 10
        if teclas_press[pg.K_RIGHT] and -self.limite_x < self.offset_x and scroll_x:
            self.offset_x -= 10
        if teclas_press[pg.K_UP] and self.offset_y < self.limite_y and scroll_y:
            self.offset_y += 10
        if teclas_press[pg.K_DOWN] and -self.limite_y < self.offset_y and scroll_y:
            self.offset_y -= 10

        # Mover com o Mouse
        pos_mouse_atual = pg.mouse.get_pos()
        if mouse_press[0] and self.rect.collidepoint(pos_mouse_atual):
            dx = pos_mouse_atual[0] - self.pos_mouse[0]
            dy = pos_mouse_atual[1] - self.pos_mouse[1]
            self.offset_x += dx if scroll_x and -self.limite_x < self.offset_x < self.limite_x else 0
            self.offset_y += dy if scroll_y and -self.limite_y < self.offset_y < self.limite_y else 0
        self.pos_mouse = pos_mouse_atual

    def desenhar(self, surface: pg.Surface) -> None:
        surface.blit(self, self.rect)
    
    # Desenhar formas geométricas
    def draw_rect(self, color: tuple, rect: pg.Rect, width: int=0, border_radius: int=-1) -> None:
        rect = self.transform_rect(rect)
        width = self.tranform_tam(width)
        border_radius = self.tranform_tam(border_radius)
        pg.draw.rect(self, color, rect, width, border_radius)

    def draw_circle(self, color: tuple, center: tuple, raio: float, width: int = 0) -> None:
        pg.draw.circle(self, color, self.tranform_pos(center), self.tranform_tam(raio), self.tranform_tam(width))

    def draw_line(self, color: tuple, start_pos: tuple, end_pos: tuple, width: int=0) -> None:
        pg.draw.line(self, color, self.tranform_pos(start_pos), self.tranform_pos(end_pos), self.tranform_tam(width))

    def draw_polygon(self, color: tuple, points: list, width: int=0) -> None:
        novo_points = [self.tranform_pos(ponto) for ponto in points]
        pg.draw.polygon(self, color, novo_points, self.tranform_tam(width))

    def draw_arc(self, color: tuple, rect: pg.Rect, start_angle: float, stop_angle: float, width: int=0) -> None:
        pg.draw.arc(self, color, self.transform_rect(rect), start_angle, stop_angle, self.tranform_tam(width))
        
    # Redimencionar tamanhos
    def transform_surface(self, surface) -> None: 
        largura = self.tranform_tam(surface.get_width())
        altura = self.tranform_tam(surface.get_height())
        pg.transform.scale(surface, (largura, altura))
        return surface

    def transform_rect(self, rect: pg.Rect=None, rect_escalado: pg.Rect=None) -> None:
        if rect is not None:
            rect_escalado = rect.copy() if rect_escalado is None else rect_escalado
            rect_escalado.x, rect_escalado.y = self.tranform_pos((rect.x, rect.y))
            rect_escalado.width = self.tranform_tam(rect.width)
            rect_escalado.height = self.tranform_tam(rect.height)
            return rect_escalado

    def tranform_pos(self, pos: tuple) -> None:
        return int((pos[0] + self.offset_x) * self.zoom), int((pos[1] + self.offset_y) * self.zoom)

    def tranform_tam(self, tam) -> None:
        return int(tam * self.zoom)

if __name__ == "__main__":
    pg.init()
    largura, altura = 400, 300
    tela = pg.display.set_mode((largura, altura))
    superficie = Superficie(10, 10, 320, 180, (230, 255, 230), 1)
    caixa = Caixa_Texto(50, 50, 60, 'arial', 20, 'Texto...')
    barra = Barra((50, 150), 200, 41, ('Super Fácil', 'Fácil', 'Médio', 'Difícil', 'Super Díficil'), 1, cor=(0, 0, 0))

    rodando = True
    while rodando:
        pg.time.Clock().tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                rodando = False
            caixa.eventos(event)
            superficie.eventos(event)
            
        barra.atualizar()
        superficie.atualizar()

        tela.fill((200, 200, 200))
        superficie.fill(superficie.cor)

        caixa.desenhar(superficie)
        barra.desenhar(superficie)
        
        superficie.desenhar(tela)
        pg.display.flip()

class Botao(pg.sprite.Sprite):
    def __init__(self, func: lambda: None, pos: tuple, arq_img: str=None,
                 tam: tuple=(40, 40), cor: tuple=(0, 0, 0),
                 texto: str=None, escala: float=1, aumt_select: bool=False, groups: list=[]):
        super().__init__(*groups)

        self.func = func

        self.image = pg.image.load(arq_img) if arq_img else pg.Surface(tam)
        self.image = pg.transform.scale(self.image, (int(self.image.get_width()*escala),
                                                     int(self.image.get_height()*escala)))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        self.aumt_select = aumt_select
        if self.aumt_select:
            self.imagens = [self.image, pg.transform.scale(self.image, (int(self.image.get_width()*1.1),
                                                              int(self.image.get_height()*1.1)))]

        if not arq_img: self.image.fill(cor)
        if texto:
            font = pg.font.Font("consolas", tam[1]//2)
            texto = font.render(texto, True, (0, 0, 0))
            texto_rect = texto.get_rect()
            self.image.blit(texto, texto_rect)
        
    def eventos(self, event) -> None:
        pos_mouse = pg.mouse.get_pos()
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pos_mouse):
                self.func()

        if self.aumt_select:
            if event.type == pg.MOUSEMOTION:
                if self.rect.collidepoint(pos_mouse):
                    self.image = self.imagens[1]
                else:
                    self.image = self.imagens[0]
