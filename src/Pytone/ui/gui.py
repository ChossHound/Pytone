import pygame
from ui.piano_roll import PianoRoll
from ui.song_ribbon import SongRibbon
from ui.cursor import Cursor
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE
from models.song import Song
from models.audioEngine import Engine


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
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.FONT: pygame.freetype.Font = pygame.freetype.Font("src/Pytone/assets/Tiny5.ttf", 1, resolution=PIXEL_SCALE*5*128)
        Engine().start()

        self.songribbon: SongRibbon = SongRibbon(self.screen, self.FONT, 30*PIXEL_SCALE)
        self.pianoroll: PianoRoll = PianoRoll(self.screen, self.FONT, 16*PIXEL_SCALE, 30*PIXEL_SCALE, lambda: self.songribbon.current_beat, Song(), 0)
        Cursor().init(self.screen, (255, 255, 255), 8)

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


if __name__ == "__main__":
    GUI().run()
