# $Revision: 1.24 $
#
# Copyright (c) Gordon McNutt, 2011
#

import minimap
import pygame
import vector

from sprite import *

white = 255, 255, 255
GRID_COLOR = 128, 128, 128
GRID_SIZE = 500
CULL_FACTOR = 10

def check_collision(sprite, sprites):
    """ Check if 'sprite' collides with any sprite S in 'group'. Returns first
    such S found or None. """
    for other in sprites:
        if sprite.rect.colliderect(other.rect):
            if pygame.sprite.collide_mask(sprite, other):
                return other
    return None

def check_group_collision(group1, group2):
    """ Check if any sprite S1 in 'group1' collides with any sprite S2 in
    'group2'. Returns a list of all (S1, S2) pairs found or None. """
    hits = []
    for spr1 in group1:
        for spr2 in group2.sprites():
            if spr1.rect.colliderect(spr2.rect):
                if pygame.sprite.collide_mask(spr1, spr2):
                    hits.append((spr1, spr2))
    return hits


class Level(object):
    """ The level holds all the sprites and every frame updates them and
    repaints the screen. """
    def __init__(self, screen=None, 
                 fps=60, bgd=None, show_boxes=False,
                 *args, **kwargs):
        """
        screen: screen surface
        fps: desired frames per second
        bgd: background object
        show_boxes: True to show bounding boxes
        """
        super(Level, self).__init__(*args, **kwargs)
        self.rect = screen.get_rect()
        self.screen = screen
        self.fps = fps
        self.bgd = bgd
        self.all = pygame.sprite.LayeredDirty()
        self.drawn_rects = []
        self.player_shots = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.hits_player = pygame.sprite.Group()
        self.hits_player_shot = pygame.sprite.Group()
        self.hot_group = pygame.sprite.LayeredDirty()
        self.player = None
        self.show_boxes = show_boxes
        self.viewrect = pygame.Rect((0, 0), self.rect.size)
        self.scrollrect = self.rect.inflate(self.rect.width/6 - 
                                            self.rect.width, 
                                             self.rect.height/6 -
                                            self.rect.height)
        self.cullrect = self.rect.inflate(self.rect.width * CULL_FACTOR,
                                          self.rect.height * CULL_FACTOR)
        self.minimap = minimap.LevelMap(self, 100, (0, 0), surf=self.screen,
                                        bgcolor = (64, 64, 64))

    def __nonzero__(self):
        """ Returns true iff the level is still 'active'. Allows the caller to
        use an expression like this for the main loop:
        
        while mylevel:
            mylevel.update()
            # do other per-frame activities
        """
        if (self.player and self.player.alive()) or self.explosions:
            return True
        else:
            return False

    def add(self, sprite, maploc):
        """ Add a sprite to the level. This classifies the sprite based on its
        class type (for collision checking) and assigns its map location. """
        sprite.put_at(self, maploc)
        if isinstance(sprite, Explosion):
            self.explosions.add(sprite)
        elif isinstance(sprite, PlayerShot):
            self.player_shots.add(sprite)
        elif isinstance(sprite, PlayerShip):
            self.player = sprite
        if isinstance(sprite, CollidesWithPlayer):
            self.hits_player.add(sprite)
        if isinstance(sprite, CollidesWithPlayerShot):
            self.hits_player_shot.add(sprite)
        self.all.add(sprite)

    def view(self, sprite):
        """ Center the viewrect on the sprite. """
        offset = vector.subtract(sprite.rect.center, self.viewrect.center)
        self.scroll(offset)

    def start(self):
        """ Blit the background for the first time before calling update. """
        self.bgd.blit(self.screen, self.rect)
        pygame.display.flip()

    def paint_grid(self):
        """ Paint a grid on the background. Returns the list of dirty
        rectangles. """
        dirty = []
        x = GRID_SIZE - (self.viewrect.left % GRID_SIZE)
        while x < self.rect.right:
            dirty.append(pygame.draw.line(self.screen, GRID_COLOR, (x, 0), 
                                          (x, self.rect.height)))
            x += GRID_SIZE
        y = GRID_SIZE - (self.viewrect.top % GRID_SIZE)
        while y < self.rect.bottom:
            dirty.append(pygame.draw.line(self.screen, GRID_COLOR, (0, y), 
                                          (self.rect.width, y)))
            y += GRID_SIZE
        return dirty

    def cull(self):
        """ Kill any sprites not completely inside of the culling
        rectangle. """
        for sprite in self.all:
            if not self.cullrect.contains(sprite.maprect):
                sprite.kill()

    def update_hot_group(self):
        self.hot_group.empty()
        for sprite in self.all:
            if self.viewrect.colliderect(sprite.maprect):
                self.hot_group.add(sprite)
                sprite.pre_render()
        

    def update(self):
        """ Called every frame. Erases the dirty rects from the last update and
        makes some more! This handles scrolling, updating all the sprites,
        repainting them, and checking for collisions."""
        # Erase the rects drawn last time we were in update by blitting the
        # background over them.
        for drect in self.drawn_rects:
            self.bgd.blit(self.screen, drect)
        erased_rects = self.drawn_rects
        # Handle auto-scrolling. If the player moves out of the scrolling rect
        # then scroll in that direction.
        if self.player.rect.top < self.scrollrect.top:
            self.scroll((0, (self.player.rect.top - self.scrollrect.top)))
        elif self.player.rect.bottom > self.scrollrect.bottom:
            self.scroll((0, (self.player.rect.bottom - self.scrollrect.bottom)))
        if self.player.rect.left < self.scrollrect.left:
            self.scroll(((self.player.rect.left - self.scrollrect.left), 0))
        elif self.player.rect.right > self.scrollrect.right:
            self.scroll(((self.player.rect.right - self.scrollrect.right), 0))
        # Cull out-of-bound sprites.
        self.cull()
        # Update (move) all sprites.
        self.all.update()
        # Reset the drawn rects to empty before we start painting sprites.
        self.drawn_rects = []
        # Paint the grid.
        self.drawn_rects += self.paint_grid()
        # Gather sprites into the hot group and render it.
        self.update_hot_group()
        self.drawn_rects += self.hot_group.draw(self.screen)
        # Show bounding boxes if called for.
        if self.show_boxes:
            for sprite in self.all:
                pygame.draw.rect(self.screen, white, sprite.rect, 1)
            pygame.draw.rect(self.screen, white, self.scrollrect, 1)
        # Draw player velocity vector line.
        self.drawn_rects.append(self.player.draw_velocity())
####        # draw angles
####        for sprite in self.bases:
####            if hasattr(sprite, 'draw_angle'):
####                self.drawn_rects.append(sprite.draw_angle())
        # Paint the minimap.
        self.drawn_rects.append(self.minimap.paint())
        dirty_rects = erased_rects + self.drawn_rects
        pygame.display.update(dirty_rects)

        # Collision checking.
        if self.hits_player:
            if self.player.alive():
                group = [sprite for sprite in self.hot_group if \
                             isinstance(sprite, CollidesWithPlayer)]
                base = check_collision(self.player, group)
                if base:
                    base.destroy()
                    self.player.destroy()
        if self.hits_player_shot:
            group = [sprite for sprite in self.hot_group if \
                         isinstance(sprite, CollidesWithPlayerShot)]
            hits = check_group_collision(group, self.player_shots)
            for hit in hits:
                hit[0].destroy()
                hit[1].destroy()
                    
    def scroll(self, offset):
        """ Scroll the view. """
        # Clamp the view to the maprect. Subtle: the sprites are offset in the
        # opposite direction.
        clamped_rect = self.viewrect.move(offset)
        clamped_offset = vector.subtract(self.viewrect.topleft, 
                                         clamped_rect.topleft)
        self.viewrect = clamped_rect
        self.cullrect.center = self.viewrect.center
        for sprite in self.all:
            sprite.scroll(clamped_offset)

    def get_offscreen_position(self, size):
        """ Get a random position for a rect of size 'size' within the cullrect
        but outside the viewrect."""
        position = vector.randintrect(self.cullrect)
        rect = pygame.Rect(position, size)
        while self.viewrect.contains(rect):
            position = vector.randintrect(self.cullrect)
            rect = pygame.Rect(position, size)
        return position
