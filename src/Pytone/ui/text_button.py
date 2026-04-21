from typing import Callable
import pygame
import pygame.freetype
from ui.button import Button
from ui.constants import PIXEL_SCALE, BUTTON_COLOR, TEXT_COLOR
from ui.cursor import Cursor


class TextButton(Button):
    """A button that also contains centered text

    Properties:
     - text: the str that is printed on top of the button.
    """

    def __init__(self, screen: pygame.Surface, font: pygame.freetype.Font, rect: pygame.Rect, text: str, call_back: Callable[..., None]) -> None:
        super().__init__(screen, rect, call_back)
        self.font = font
        self.text: str = text
        pass

    def draw(self) -> None:
        super().draw()
        self.font.render_to(self.screen, (self.rect.x + 2 * PIXEL_SCALE, self.rect.y + PIXEL_SCALE), self.text, TEXT_COLOR)
