from . import Wrapper, Label


class Button(Wrapper):

    OFF_COLOR = (128, 128, 128)
    ON_COLOR = (255, 128, 64)

    def __init__(self, cb=None, text=None, font=None, **kwargs):
        bgc = self.OFF_COLOR
        label = Label(bgcolor=bgc, text=text, font=font, **kwargs)
        super(Button, self).__init__(widget=label, bgcolor=bgc, **kwargs)
        self.cb = cb

    def onclick(self, pos):
        # Passing self to workaround the problem notes in the OptionDialog
        # class.
        self.cb(self)

    def mouseover(self, pos):
        self.bgcolor = self.ON_COLOR
        self.widget.bgcolor = self.ON_COLOR
        return self

    def mouseoff(self):
        self.bgcolor = self.OFF_COLOR
        self.widget.bgcolor = self.OFF_COLOR
