import pygame
from ui.widget import Widget
from ui.cursor import Cursor
from ui.constants import DARK_ACCENT, TEXT_COLOR, BUTTON_COLOR, PIXEL_SCALE
from typing import Callable

class DropDown(Widget):
    """Widget for selecting options from a list

    Properties:
     - position: where to draw the top-left corner of the wdiget
     - options: the list of options to choose from. A List of tuples between the name of the option and its ID. The ID does not have to follow the index.
     - width: how large the widget is drawn. Calculated from the length of the longest option.
     - index: which option is currently selected
     - open: whether or not the list is open
     - on_change: a callable that is called everytime a new option is selected
    """
    def __init__(self, screen: pygame.Surface, font: pygame.freetype.Font, position: tuple[int, int], options: list[tuple[str, int]], on_change=lambda: None):
        super().__init__(screen)
        self.font: pygame.freetype.Font = font
        self.position: tuple[int, int] = position
        self.options: list[tuple[str, int]] = options
        self.width: int = len(max(options, key=lambda x: len(x[0]))[0]) * 4*PIXEL_SCALE + 10*PIXEL_SCALE
        self.index: int = 0
        self.open: bool = False
        self.on_change: Callable[[int], None] = on_change

    def get_rect(self) -> pygame.Rect:
        """Get the bounding box for the widget. Changes if it is open or not"""
        if self.open:
            return pygame.Rect(self.position, (self.width, 3*PIXEL_SCALE + len(self.options)*9*PIXEL_SCALE))
        return pygame.Rect(self.position, (self.width, 12*PIXEL_SCALE))

    def get_value(self) -> int:
        """Returns the ID of the current choice"""
        return self.options[self.index][1]

    def set_value(self, new: int) -> None:
        """Sets the current choice based on an ID"""
        for i in range(0, len(self.options)):
            if new == self.options[i][1]:
                self.index = i
                return
        raise IndexError

    def draw(self):
        self.font.origin = True
        pygame.draw.rect(self.screen, DARK_ACCENT, self.get_rect())
        if self.open:
            for i in range(0, len(self.options)):
                self.font.render_to(self.screen, (self.position[0] + 2*PIXEL_SCALE, self.position[1] + 9*PIXEL_SCALE + 9*PIXEL_SCALE*i), self.options[i][0], TEXT_COLOR)
        else:
            self.font.render_to(self.screen, (self.position[0] + 2*PIXEL_SCALE, self.position[1] + 9*PIXEL_SCALE), self.options[self.index][0], TEXT_COLOR)
            self.font.render_to(self.screen, (self.position[0] + self.width - 6*PIXEL_SCALE, self.position[1] + 8*PIXEL_SCALE), "v", BUTTON_COLOR)
        self.font.origin = False

    def process(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if Cursor().is_overlapping(self.get_rect(), self):
                if self.open:
                    position: int = Cursor().get_position()[1]
                    position -= self.get_rect()[1]
                    position /= self.get_rect()[3]
                    position *= len(self.options)
                    old: int = self.index
                    self.index = min(max(int(position), 0), len(self.options) - 1)
                    if old != self.index:
                        self.on_change(self.options[self.index][1])
                    Cursor().relinquish_focus(self)
                    self.open = False
                else:
                    self.open = True
                    Cursor().obtain_focus(self)
            else:
                self.open = False
                Cursor().relinquish_focus(self)
