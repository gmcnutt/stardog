
def align_horz(rect, align):
    """ Widen 'rect' leftwards to a multile of 'align'. """
    lmargin = rect.left % align
    rmargin = align - (rect.right % align)
    rect.left -= lmargin
    rect.width += (lmargin + rmargin)

def align_vert(rect, align):
    """ Heighten 'rect' upwards to a multile of 'align'. """
    lmargin = rect.top % align
    rmargin = align - (rect.bottom % align)
    rect.top -= lmargin
    rect.height += (lmargin + rmargin)

class Background(object):
    """ Abstract base class for background renderers. """
    def __init__(self, *args, **kwargs):
        pass
        
    def blit(self, surf, rect):
        pass

class FillBackground(Background):

    def __init__(self, color=(255, 255, 255), *args, **kwargs):
        super(FillBackground, self).__init__(*args, **kwargs)
        self.color = color

    def blit(self, surf, rect):
        surf.fill(self.color, rect)


class TextureBackground(Background):

    def __init__(self, fname, *args, **kwargs):
        super(TextureBackground, self).__init__(*args, **kwargs)
        self.image = pygame.image.load(IMAGEDIR + fname).convert_alpha()
        self.rect = self.image.get_rect()

    def blit(self, surf, dest):
        dest2 = dest.copy()
        align_horz(dest2, self.rect.width)
        align_vert(dest2, self.rect.height)
        area = self.rect.copy().move(dest2.topleft)
        for row in range(dest2.height/area.height):
            for col in range(dest2.width/area.width):
                surf.blit(self.image, area)
                area.left += area.width
            area.top += area.height
            area.left = dest2.left

