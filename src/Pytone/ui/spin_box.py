import pygame
import pygame.freetype
from ui.widget import Widget
from typing import Callable
import math
from ui.constants import DARK_ACCENT, BUTTON_COLOR, TEXT_COLOR
from ui.button import Button

class SpinBox(Widget):
    """A UI widget for entering integers.
    Has buttons on right for increasing or decreasing the current value.

    Properties
     - position: a tuple of ints representing where to draw the widget
     - value: an int representing the current state of the input.
     - min: the minimum (inclusive) int for value
     - max: the maximum (inclusive) int for value
     - get_next: a callable that takes the current value and returns the next. Initialized to 'next = current + 1'
     - get_previous: a callable that takes the current value and returns the previous. Initialized to 'previous = current - 1'
     - width: how large the spin box should be. Determined based on the size of the text times the largest value.
     - plus: a button that calls increment
     - minus: a button that calls decrement
    """
    def __init__(self, screen: pygame.Surface, font: pygame.freetype.Font, position: tuple[int, int], value, min_value, max_value, get_next: Callable[[int], int] = lambda x: x + 1, get_previous: Callable[[int], int] = lambda x: x - 1):
        super().__init__(screen)
        self.font: pygame.freetype.Font = font
        self.position: tuple[int, int] = position
        self.value: int = value
        self.min: int = min_value
        self.max: int = max_value
        self.get_next: Callable[[int], int] = get_next
        self.get_previous: Callable[[int], int] = get_previous
        self.width = 16 * (int(math.log10(max_value)) + 1) + 16

        x, y = self.position
        self.plus: Button = Button(screen, pygame.Rect(x + self.width + 4, y, 20, 16), self.increment)
        self.minus: Button = Button(screen, pygame.Rect(x + self.width + 4, y + 20, 20, 12), self.decrement)

    def increment(self) -> None:
        self.value = self.get_next(self.value)
        if self.value > self.max:
            self.value = self.max

    def decrement(self) -> None:
        self.value = self.get_previous(self.value)
        if self.value < self.min:
            self.value = self.min

    def draw(self):
        x, y = self.position

        # text
        pygame.draw.rect(self.screen, DARK_ACCENT, pygame.Rect(x, y, self.width, 32))
        self.font.render_to(self.screen, (x + 8, y + 4), str(self.value), TEXT_COLOR)

        # buttons
        self.plus.draw()
        x, y, w, h = self.plus.rect
        pygame.draw.rect(self.screen, TEXT_COLOR, (x + 8, y, 4, 12))
        pygame.draw.rect(self.screen, TEXT_COLOR, (x + 4, y + 4, 12, 4))

        self.minus.draw()
        x, y, w, h = self.minus.rect
        pygame.draw.rect(self.screen, TEXT_COLOR, (x + 4, y + 4, 12, 4))

    def process(self, event) -> None:
        self.plus.process(event)
        self.minus.process(event)
