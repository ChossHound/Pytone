from ui.widget import Widget
from ui.constants import PIXEL_SCALE, DARK_ACCENT, BUTTON_COLOR
from ui.cursor import Cursor
from typing import Callable
import pygame


class Slider(Widget):
    """ Widget for displaying and modifying a percentage as a line.
    properties:
     - position: a tuple[int, int] of where to draw the line
     - width: how long the line should be
     - get_percent: a callable that returns the percentage to display
     - set_percent: a callable that sets the percentage
     - scrubbing: a bool to track whether the percentage should be set when the mouse moves
    """
    def __init__(self,
                 screen: pygame.Surface,
                 position: tuple[int, int],
                 width: int,
                 get_percent: Callable[[None], float],
                 set_percent: Callable[[float], None]):
        super().__init__(screen)
        self.position: tuple[int, int] = position
        self.width: int = width
        self.get_percent: Callable[[None], float] = get_percent
        self.set_percent: Callable[[float], None] = set_percent
        self.scrubbing: bool = False

    def draw(self):
        x, y = self.position
        pygame.draw.rect(self.screen, DARK_ACCENT, self.get_rect())
        pygame.draw.rect(self.screen,
                         BUTTON_COLOR,
                         pygame.Rect(x,
                                     y,
                                     int(self.get_percent() * self.width),
                                     2*PIXEL_SCALE))

    def get_rect(self) -> pygame.Rect:
        """Determine how the rectangle should be drawn"""
        return pygame.Rect((self.position), (self.width, 2*PIXEL_SCALE))

    def percent_from_position(self) -> float:
        """Convert the cursor's position to a % between the start and end of the line."""
        x, y = Cursor().get_position()
        percent: float = (x - self.position[0]) / self.width
        return min(max(0.0, percent), 1.0)

    def process(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if Cursor().is_overlapping(self.get_rect()):
                self.scrubbing = True
                self.set_percent(self.percent_from_position())
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.scrubbing = False
        if event.type == pygame.MOUSEMOTION and self.scrubbing:
            self.set_percent(self.percent_from_position())
