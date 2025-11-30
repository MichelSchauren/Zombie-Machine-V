# ...existing code...
from typing import Dict, List, Tuple
import pygame as pg

class SpatialGrid:
    def __init__(self, cell_size: int, width: int, height: int):
        self.cell_size = cell_size
        self.cols = (width + cell_size - 1) // cell_size
        self.rows = (height + cell_size - 1) // cell_size
        self.cells: Dict[Tuple[int,int], List[pg.Rect]] = {}

    def _cells_for_rect(self, rect: pg.Rect):
        cx0 = max(0, rect.left // self.cell_size)
        cy0 = max(0, rect.top // self.cell_size)
        cx1 = min(self.cols - 1, rect.right // self.cell_size)
        cy1 = min(self.rows - 1, rect.bottom // self.cell_size)
        for cy in range(cy0, cy1 + 1):
            for cx in range(cx0, cx1 + 1):
                yield (cx, cy)

    def insert(self, rect: pg.Rect):
        """Adiciona um rect (geralmente um tile) nas células correspondentes."""
        for cell in self._cells_for_rect(rect):
            self.cells.setdefault(cell, []).append(rect)

    def query(self, rect: pg.Rect) -> List[pg.Rect]:
        """Retorna a lista de rects potencialmente colidíveis com `rect` (sem filtrar por colliderect)."""
        found = []
        seen = set()
        for cell in self._cells_for_rect(rect):
            for r in self.cells.get(cell, ()):
                key = id(r)
                if key not in seen:
                    seen.add(key)
                    found.append(r)
        return found

    def clear(self):
        self.cells.clear()
# ...existing code...