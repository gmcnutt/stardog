from . import Container, Runnable, Wrapper, Button, Label

class OkDialog(Container, Runnable):

    def __init__(self, text=None, font=None, **kwargs):
        Container.__init__(self, **kwargs)
        Runnable.__init__(self)
        self.add(Wrapper(Label(text=text, font=font, **kwargs), **kwargs))
        self.add(
            Wrapper(
                Button(cb=self.stop, text='Ok', font=font, **kwargs), **kwargs))
