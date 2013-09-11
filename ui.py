import pygame
import sys
import vector

DEFAULT_BORDER = 5
DEFAULT_BGCOLOR = (94, 94, 94)


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
        print(self.rect)
        return self.rect

    def paint(self, **kwargs):
        super(Label, self).paint(**kwargs)
        self.font.write(self.surf, self.rect, self.text)
        return self.rect


class ValueLabel(Label):
    """ Label with a title and a dynamic value. """
    def __init__(self, pos=None, title=None, value_func=None, **kwargs):
        super(ValueLabel, self).__init__(**kwargs)
        self.title = title
        self.value_func = value_func
        self.rect = pygame.Rect((pos), (100, 20))

    def tick(self):
        self.text = '{}:{}'.format(self.title, self.value_func())
        self.paint()
        pygame.display.update(self.rect)


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


class Wrapper(Container):

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


class RunnableMixin(object):
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


class OkDialog(Container, RunnableMixin):

    def __init__(self, text=None, font=None, **kwargs):
        Container.__init__(self, **kwargs)
        RunnableMixin.__init__(self)
        self.add(Wrapper(Label(text=text, font=font, **kwargs), **kwargs))
        self.add(
            Wrapper(
                Button(cb=self.stop, text='Ok', font=font, **kwargs), **kwargs))


class OptionDialog(Container, RunnableMixin):

    def __init__(self, options=None, font=None, **kwargs):
        Container.__init__(self, **kwargs)
        RunnableMixin.__init__(self)
        for option in options:
            self.add(
                Wrapper(
                    Button(cb=lambda button: self.stop(button.widget.text),
                           text=option, font=font, **kwargs),
                    **kwargs))


class UI(object):

    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def layout_and_center(self, widget):
        maxrect = self.screen.get_rect()
        widget.layout(maxrect)
        widget.center(maxrect.center)
        return widget

    def prompt(self, msg):
        dialog = OkDialog(font=self.font, text=msg, surf=self.screen)
        self.layout_and_center(dialog).run()

    def choose(self, options):
        dialog = OptionDialog(font=self.font, options=options, surf=self.screen)
        return self.layout_and_center(dialog).run()

    def show(self, msg):
        wrapper = Wrapper(
            widget=Label(font=self.font, text=msg, surf=self.screen),
            surf=self.screen)
        self.layout_and_center(wrapper)
        pygame.display.update(wrapper.paint())
