import pygame
from . import Label


class ValueLabel(Label):

    """ Label with a title and a dynamic value. """
    def __init__(self, pos=None, title=None, value_func=None, **kwargs):
        super(ValueLabel, self).__init__(**kwargs)
        self.title = title
        self.value_func = value_func
        self.rect = pygame.Rect((pos), (150, 20))
        self.text = '{}:{}'.format(self.title, self.value_func())

    def tick(self):
        self.text = '{}:{}'.format(self.title, self.value_func())
        self.paint()
        return self.rect
        #pygame.display.update(self.rect)
