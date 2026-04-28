import pygame
try:
    from pygame._sdl2.video import Window
except ImportError:
    Window = None
from ui.piano_roll import PianoRoll
from ui.song_ribbon import SongRibbon
from ui.cursor import Cursor
from ui.constants import PIXEL_SCALE
from models.song import Song
from models.track import Track
from models.audioEngine import Engine

DEFAULT_WINDOW_SIZE: tuple[int, int] = (200*PIXEL_SCALE, 200*PIXEL_SCALE)


class GUI:
    """ Class for standing up widgets and updating them repeatedly.

    Properties:
     - clock: the pygame clock object for waiting 1/60th of a second between frames
     - screen: the pygame surface to draw widgets onto.
     - font: the pygame font for drawing text on the screen
     - pianoroll: the PianoRoll object responsible for allows the user to draw notes on the screen.
     - songribbon: the SongRibbon object that allows the user to manage playback of the song.
    """
    def __init__(self):
        """Stand up and connect widgets"""
        pygame.init()
        pygame.display.set_caption("Pytone")

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.screen: pygame.Surface = self.create_maximized_screen()
        self.FONT: pygame.freetype.Font = pygame.freetype.Font("src/Pytone/assets/Tiny5.ttf", 1, resolution=PIXEL_SCALE*5*128)
        Engine().start()

        Song().add_track(Track(instrument=1))
        Song().add_track(Track(instrument=1))
        Song().add_track(Track(instrument=1))
        Song().add_track(Track(instrument=1))
        self.songribbon: SongRibbon = SongRibbon(self.screen, self.FONT, 30*PIXEL_SCALE)
        self.pianoroll: PianoRoll = PianoRoll(self.screen, self.FONT, 16*PIXEL_SCALE, 30*PIXEL_SCALE, lambda: self.songribbon.current_beat, 0)
        self.songribbon.on_track_change = self.pianoroll.update_track
        Cursor().init(self.screen, (255, 255, 255), 8)

    def create_maximized_screen(self) -> pygame.Surface:
        """Create a resizable window and maximize it when SDL supports that."""
        screen = pygame.display.set_mode(
            DEFAULT_WINDOW_SIZE,
            pygame.RESIZABLE,
        )

        if Window is not None:
            try:
                Window.from_display_module().maximize()
            except pygame.error:
                display_info = pygame.display.Info()
                screen = pygame.display.set_mode(
                    (display_info.current_w, display_info.current_h),
                    pygame.RESIZABLE,
                )

        return screen

    def update_screen(self, size: tuple[int, int]) -> None:
        """Recreate the display surface and share it with existing widgets."""
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.songribbon.screen = self.screen
        self.pianoroll.screen = self.screen
        Cursor().screen = self.screen

    def run(self) -> None:
        """Run the program forever"""
        while True:
            dt = self.clock.tick(60)
            self.pianoroll.current_beat = self.songribbon.current_beat
            self.pianoroll.draw()
            self.songribbon.draw(dt)
            Cursor().draw()
            pygame.display.flip()
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                Cursor().process(event)
                self.pianoroll.process(event)
                self.songribbon.process(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.VIDEORESIZE:
                    self.update_screen(event.size)


if __name__ == "__main__":
    GUI().run()
