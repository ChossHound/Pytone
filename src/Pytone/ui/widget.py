
import pygame
import pygame.freetype
from abc import ABC, abstractmethod


class Widget(ABC):
    """The base class that all UI objects inherit from.

    Properties:
     - screen: The pygame.Surface that objects on drawn onto.
    """
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen: pygame.Surface = screen

    @abstractmethod
    def process(self, event: pygame.event.Event) -> None:
        """
        Check the event buffer on each frame to affect the widget.
        """

    @abstractmethod
    def draw(self) -> None:
        """
        Draws the widget to the screen
        """
