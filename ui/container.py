from . import Widget
import vector


class Container(Widget):

    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        self.contents = []

    def add(self, widget):
        self.contents.append(widget)

    def deliver(self, pos, func):
        for widget in self.contents:
            if widget.rect.collidepoint(pos):
                return func(widget)

    def onclick(self, pos):
        self.deliver(pos, lambda w: w.onclick(pos))

    def mouseover(self, pos):
        return self.deliver(pos, lambda w: w.mouseover(pos))

    def paint(self, **kwargs):
        super(Container, self).paint(**kwargs)
        for widget in self.contents:
            widget.paint(**kwargs)
        return self.rect

    def layout(self, max_rect):
        self.size = 0
        for widget in self.contents:
            usedrect = widget.layout(max_rect)
            max_rect.height -= usedrect.height
            max_rect.top += usedrect.height
            self.rect.height += usedrect.height
            self.rect.width = max(self.rect.width, usedrect.width)
        for widget in self.contents:
            widget.center((self.rect.centerx, widget.rect.centery))
        return self.rect

    def center(self, pos):
        offset = vector.subtract(pos, self.rect.center)
        super(Container, self).center(pos)
        for widget in self.contents:
            widget.move(offset)

    def tick(self):
        for widget in self.contents:
            widget.tick()
