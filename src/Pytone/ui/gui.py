import pygame
from ui.piano_roll import PianoRoll
from ui.song_ribbon import SongRibbon
from models.note import Note
from ui.cursor import Cursor
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE

def Run() -> None:
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pytone")
    Cursor().init(screen, (255, 255, 255), 2)
    pianoroll: PianoRoll = PianoRoll(screen, pygame.Rect(64, 64, SCREEN_WIDTH-64, SCREEN_HEIGHT))
    songribbon: SongRibbon = SongRibbon(screen, 64)

    while True:
        clock.tick(60)
        pianoroll.current_beat = songribbon.current_beat
        pianoroll.draw()
        songribbon.draw()
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