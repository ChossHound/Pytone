import pygame
from pygame import Rect
from ui.constants import PIXEL_SCALE

class Cursor:
    screen = None
    color = None
    size = None

    def __init__(self, screen=None, color=None, size=None):
        if screen is not None and color is not None and size is not None:
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

    def is_overlapping(self, other: Rect) -> bool:
        return Rect.colliderect(self.get_rect(), other)
        
    def get_rect(self) -> Rect:
        x, y = self.get_position()
        return Rect(x, y, self.size, self.size)

    def draw(self):
        x, y = self.get_position()
        pygame.draw.rect(self.screen, self.color, self.get_rect())