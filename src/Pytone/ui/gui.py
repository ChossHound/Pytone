import pygame
from ui.piano_roll import PianoRoll
from ui.song_ribbon import SongRibbon
from models.note import Note
from models.song import Song
from models.audioEngine import Engine
from ui.cursor import Cursor
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE

def Run(song: Song | None = None, engine: Engine | None = None) -> None:
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pytone")
    song = Song() if song is None else song
    engine = Engine() if engine is None else engine
    Cursor().init(screen, (255, 255, 255), 2)
    songribbon: SongRibbon = SongRibbon(screen, 64, song=song, engine=engine)
    pianoroll: PianoRoll = PianoRoll(
        screen,
        pygame.Rect(64, 64, SCREEN_WIDTH-64, SCREEN_HEIGHT),
        songribbon.get_current_beat,
        song=song,
    )

    while True:
        dt = clock.tick(60)
        pianoroll.current_beat = songribbon.current_beat
        pianoroll.draw()
        songribbon.draw(dt)
        Cursor().draw()
        pygame.display.flip()
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            Cursor().process(event)
            pianoroll.process(event)
            songribbon.process(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

if __name__ == "__main__":
    Run()
