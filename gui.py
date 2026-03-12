import pygame
from piano_roll import PianoRoll
from note import Note
from cursor import Cursor
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pytone")
    cursor: Cursor = Cursor(screen, (255, 255, 255), 2)
    pianoroll: PianoRoll = PianoRoll(screen, pygame.Rect(64, 0, SCREEN_WIDTH-64, SCREEN_HEIGHT))

    while True:
        clock.tick(60)
        pianoroll.draw()
        cursor.draw()
        pygame.display.flip()
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            pianoroll.process(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()