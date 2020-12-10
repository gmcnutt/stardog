from . import Wrapper
import pygame


class Frame(Wrapper):

    def __init__(self, **kwargs):
        Wrapper.__init__(self, top_pad=60, right_pad=40, **kwargs)
        self.image = pygame.image.load("frame.png")
        self.rect = self.image.get_rect()

    def paint(self, **kwargs):
        #import pdb; pdb.set_trace()
        self.surf.blit(self.image, self.rect)
        self.widget.paint(**kwargs)
        return self.rect
