import pygame
from ui.constants import PIXEL_SCALE

class Cursor:
    _instance: "Cursor | None" = None
    def __new__(cls) -> "Cursor":
        """
        Create (or return) the single Cursor instance.

        Returns:
            The singleton Cursor object.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def init(self, screen=None, color=None, size=None) -> None:
        self.holding = False
        self.screen = screen
        self.color = color
        self.size = size * PIXEL_SCALE

    def get_position(self) -> tuple[int, int]:
        (x, y) = pygame.mouse.get_pos()
        x //= PIXEL_SCALE
        y //= PIXEL_SCALE
        x *= PIXEL_SCALE
        y *= PIXEL_SCALE
        return (x, y)

    def is_overlapping(self, other: pygame.Rect) -> bool:
        return self.get_rect().colliderect(other)
        
    def get_rect(self) -> pygame.Rect:
        x, y = self.get_position()
        r: pygame.Rect = pygame.Rect(x, y, self.size, self.size)
        return r

    def process(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.holding = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.holding = False
        
    def is_holding(self) -> bool:
        return self.holding

    def draw(self):
        x, y = self.get_position()
        pygame.draw.rect(self.screen, self.color, self.get_rect())