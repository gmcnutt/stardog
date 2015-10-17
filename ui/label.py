from . import Widget
import pygame


class Label(Widget):

    def __init__(self, font=None, text=None, **kwargs):
        """ Text label """
        super(Label, self).__init__(**kwargs)
        self.font = font
        self.text = text
        self.lines = []

    def layout(self, maxrect):
        self.rect = pygame.Rect((maxrect.topleft), (0, 0))
        x = maxrect.left
        y = maxrect.top
        line = ''
        for char in self.text:
            chrect = self.font.get_dims(char)
            x += chrect.width
            line += char
            if x > maxrect.right:
                x = maxrect.left
                y += maxrect.height
                line = line[:-1]
                self.lines.append(line)
                line = ''
                if y > maxrect.bottom:
                    raise Exception("Text won't fit")
                elif y > self.rect.bottom:
                    self.rect.height += chrect.height
            elif x > self.rect.right:
                self.rect.width += chrect.width
        if line != '':
            self.lines.append(line)
            self.rect.height += chrect.height
        return self.rect

    def paint(self, **kwargs):
        super(Label, self).paint(**kwargs)
        self.font.write(self.surf, self.rect, self.text)
        return self.rect
