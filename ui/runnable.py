import pygame
import sys


class Runnable(object):
    def __init__(self):
        self.running = True
        self.run_result = None

    def stop(self, result=None):
        self.run_result = result
        self.running = False

    def run(self):
        undermouse = None
        saved_background = self.surf.copy()
        while self.running:
            dirtyrect = self.paint(show_boxes=False)
            pygame.display.update(dirtyrect)
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.onclick(event.pos)
            if event.type == pygame.MOUSEMOTION:
                if not undermouse:
                    undermouse = self.mouseover(event.pos)
                elif not undermouse.rect.collidepoint(event.pos):
                    undermouse.mouseoff()
                    undermouse = self.mouseover(event.pos)
            elif event.type == pygame.QUIT:
                sys.exit()
        dirtyrect = self.surf.blit(saved_background, (0, 0))
        pygame.display.update(dirtyrect)
        return self.run_result
