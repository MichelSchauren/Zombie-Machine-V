import pygame as pg
import os

pg.init()
tela = pg.display.set_mode((1, 1))

TAM_RECT = 5
dir_local = os.path.dirname(__file__)
caminho_img = os.path.join(dir_local, "Sprites", "Mapas", "colisores.png")
img_map = pg.image.load(caminho_img).convert_alpha()
rect_map = img_map.get_rect()
mask_map = pg.mask.from_surface(img_map)
LARGURA, ALTURA = img_map.get_size()

tile_map = os.path.join(dir_local, "Sprites", "Mapas", f"tile_map{rect_map.width//TAM_RECT}x{rect_map.height//TAM_RECT}.txt")
with open(tile_map, "w") as f:
    for y in range(0, ALTURA, TAM_RECT):
        linha = ""
        for x in range(0, LARGURA, TAM_RECT):
            rect_tile = pg.Rect(x, y, TAM_RECT, TAM_RECT)
            offset = (rect_tile.x - rect_map.x, rect_tile.y - rect_map.y)

            if mask_map.overlap_area(pg.mask.Mask(rect_tile.size, True), offset):
                linha += "1"
            else:
                linha += "0"
        f.write(linha + "\n")
print("Tile map criado com sucesso!")
