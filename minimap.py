import pygame
import ui
import vector


class LevelMap(ui.Widget):
    """ Mini-map of a level. Covers the cullrect. Shows sprites which have the
    'color' attribute. """

    def __init__(self, level, scale, pos, **kwargs):
        """ 'level' provides the sprites. 'scale' is the scale factor. 'pos' is
        where on the screen to put the map. """
        super(LevelMap, self).__init__(**kwargs)
        self.level = level
        self.scale = scale
        self.rect.topleft = pos
        self.rect.size = vector.scalar_divide(level.cullrect.size, scale)

    def paint(self):
        """ Loop over all sprites on the level and paint dots for the ones that
        have a 'color' attribute. Use their distance from the topleft corner of
        the cullrect and the scale factor to calculate their positions on the
        minimap. """
        self.surf.fill(self.bgcolor, self.rect)
        ori_left = self.level.cullrect.left
        ori_top = self.level.cullrect.top
        rect = pygame.Rect(0, 0, 0, 0)
        for sprite in self.level.all:
            if hasattr(sprite, 'color'):
                off_left = (sprite.maprect.centerx - ori_left) / self.scale
                off_top = (sprite.maprect.centery - ori_top) / self.scale
                rect.left = self.rect.left + off_left
                rect.top = self.rect.top + off_top
                # Note: this next part make big asteroids blink as they rotate
                # (size oscillates between 0 and 1; change in brightness looks
                # like a blink)
                #rect.width = sprite.rect.width / self.scale
                #rect.height = sprite.rect.height / self.scale
                pygame.draw.rect(self.level.screen, sprite.color, rect)
        return pygame.draw.rect(self.level.screen, (255, 255, 255), self.rect, 
                                1)
