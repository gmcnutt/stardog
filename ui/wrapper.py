from . import DEFAULT_BORDER
from . import Container


class Wrapper(Container):
    """Wraps an empty border around another widget."""

    def __init__(self, widget=None, **kwargs):
        super(Wrapper, self).__init__(**kwargs)
        self.widget = widget

    def add(self, widget):
        raise Exception("Can only wrap one widget")

    def paint(self, **kwargs):
        super(Wrapper, self).paint(**kwargs)
        self.widget.paint(**kwargs)
        return self.rect

    def layout(self, maxrect):
        self.rect = maxrect.copy()
        self.widget.layout(maxrect.inflate(-2 * DEFAULT_BORDER,
                                           -2 * DEFAULT_BORDER))
        self.rect.height = 2 * DEFAULT_BORDER + self.widget.rect.height
        self.rect.width = 2 * DEFAULT_BORDER + self.widget.rect.width
        return self.rect

    def center(self, pos):
        super(Wrapper, self).center(pos)
        self.widget.center(pos)

    def move(self, pos):
        super(Wrapper, self).move(pos)
        self.widget.move(pos)

    def deliver(self, pos, func):
        if self.widget.rect.collidepoint(pos):
            return func(self.widget)
