import pygame
from constants import PIXEL_SCALE

class Cursor:
    screen = None
    color = None
    size = None

    def __init__(self, screen=None, color=None, size=None):
        if screen is not None and color is not None and size is not None:
            self.screen = screen
            self.color = color
            self.size = size * PIXEL_SCALE

    @staticmethod
    def get_position() -> tuple[int, int]:
        (x, y) = pygame.mouse.get_pos()
        x //= PIXEL_SCALE
        y //= PIXEL_SCALE
        x *= PIXEL_SCALE
        y *= PIXEL_SCALE
        return (x, y)

    def draw(self):
        x, y = self.get_position()
        pygame.draw.rect(self.screen, self.color, (x, y, self.size, self.size))