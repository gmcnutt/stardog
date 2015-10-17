from . import DEFAULT_BGCOLOR
import pygame


class Widget(object):

    def __init__(self, surf=None, bgcolor=DEFAULT_BGCOLOR):
        self.surf = surf
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.bgcolor = bgcolor

    def paint(self, show_boxes=False):
        self.surf.fill(self.bgcolor, self.rect)
        if show_boxes:
            pygame.draw.rect(self.surf, (255, 255, 255), self.rect, 1)
        return self.rect

    def layout(self, max_rect):
        return self.rect

    def move(self, pos):
        self.rect.move_ip(pos)

    def center(self, pos):
        self.rect.center = pos

    def mouseover(self, pos):
        return self

    def mouseoff(self):
        pass

    def onclick(self, pos):
        pass
