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
    """

    def __init__(self, screen: pygame.Surface, rect: pygame.Rect, call_back: Callable[..., None]) -> None:
        super().__init__(screen)
        self.rect: pygame.Rect = rect
        self.call_back: Callable[..., None] = call_back
        pass

    def draw(self) -> None:
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.rect)

    def process(self, event: pygame.event.Event) -> None:
        if (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                Cursor().is_overlapping(self.rect)):
            self.call_back()
