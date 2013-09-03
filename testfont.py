import font
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((640, 480))
large_font = font.AfterFont('large_font.json', 'art/png/')

large_font.write(screen, screen.get_rect(), 
                 "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890%:!?+-=*.")
pygame.display.update()

while True:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        sys.exit()


