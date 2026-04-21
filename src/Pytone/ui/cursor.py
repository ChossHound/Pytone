import pygame
from ui.constants import PIXEL_SCALE


class Cursor():
    """ A singleton object for tracking and drawing the cursor to the screen.

    Properties:
     - screen: the pygame.surface to draw the cursor on to.
     - color: the color to draw the cursor.
     - size: the size to draw the cursor.
     - holding_left: a bool that tracks if the user is currently holding left click.
     - holding_right: a bool that tracks if the user is currently holding right click.
    """
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

    def init(self, screen: pygame.Surface, color: tuple[int, int, int], size: int) -> None:
        self.screen: pygame.Surface = screen
        self.holding_left: bool = False
        self.holding_right: bool = False
        self.color: tuple[int, int, int] = color
        self.size: int = size

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.holding_left = True
            if event.button == 3:
                self.holding_right = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.holding_left = False
            if event.button == 3:
                self.holding_right = False

    def is_holding_left(self) -> bool:
        return self.holding_left

    def is_holding_right(self) -> bool:
        return self.holding_right

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.get_rect())
