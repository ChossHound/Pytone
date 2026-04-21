from typing import Callable
import pygame
from ui.widget import Widget
from ui.constants import BUTTON_COLOR
from ui.cursor import Cursor


class Button(Widget):
    """A widget for calling a method when the user clicks on it.

    Properties:
     - rect: the pygame.Rect that determines where and how large the button should be drawn.
     - call_back: a callable that returns nothing. Called when the user clicks on the button.
     - pressed: a bool representing whether or not the button is currently being held
     - last_called: an int representing the number of milliseconds that have ellapsed between pygame.init and the button being pressed.
    """

    def __init__(self, screen: pygame.Surface, rect: pygame.Rect, call_back: Callable[..., None]) -> None:
        super().__init__(screen)
        self.rect: pygame.Rect = rect
        self.call_back: Callable[..., None] = call_back
        self.pressed: bool = False
        self.last_called: int = 0

    def draw(self) -> None:
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.rect)

    def process(self, event: pygame.event.Event) -> None:
        if (Cursor().is_overlapping(self.rect)):
            self.pressed = Cursor().holding_left
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.call_back()
                self.last_called = pygame.time.get_ticks()

    def is_held(self) -> bool:
        """Return whether or not the button is being held.
           A button is held when it has been 'pressed' for longer than half a second.
        """
        return self.pressed and pygame.time.get_ticks() - self.last_called > 500
