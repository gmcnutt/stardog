from . import Container, Runnable, Wrapper, Button

class OptionDialog(Container, Runnable):

    def __init__(self, options=None, font=None, **kwargs):
        Container.__init__(self, **kwargs)
        Runnable.__init__(self)
        for option in options:
            self.add(
                Wrapper(
                    Button(cb=lambda button: self.stop(button.widget.text),
                           text=option, font=font, **kwargs),
                    **kwargs))
