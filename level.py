# $Revision: 1.24 $
#
# Copyright (c) Gordon McNutt, 2011
#

import pygame
import vector
import sprite as spaceobj

white = 255, 255, 255
GRID_COLOR = 128, 128, 128
GRID_SIZE = 500
CULL_FACTOR = 10


def _check_collision(sprite, sprites):
    """Check for collision between a sprite and a group of sprites.

    Returns first sprite found or None. Uses the collision masks.

    """
    for other in sprites:
        if sprite.rect.colliderect(other.rect):
            if pygame.sprite.collide_mask(sprite, other):
                return other
    return None


def _check_group_collision(group1, group2):
    """Check for collision between two groups of sprites.

    Returns a list of tuples (sprite1, sprite2) or None. Uses
    collision masks.

    """
    hits = []
    for spr1 in group1:
        for spr2 in group2.sprites():
            if spr1.rect.colliderect(spr2.rect):
                if pygame.sprite.collide_mask(spr1, spr2):
                    hits.append((spr1, spr2))
    return hits


def _check_dock(sprite, sprites):
    """Check for collision between a sprite and a group of sprites.

    Returns first sprite found or None. Does NOT check the collision
    mask, just the bounding rectangles. XXX: why not?

    """
    for other in sprites:
        if sprite.rect.colliderect(other.dock_rect):
            return other
    return None


class Level(object):
    """ The level holds all the sprites and every frame updates them and
    repaints the screen. """
    def __init__(self, screen=None, fps=60, bgd=None, show_boxes=False,
                 show_grid=False):
        """
        screen: screen surface
        fps: desired frames per second
        bgd: background object
        show_boxes: True to show bounding boxes
        """
        super(Level, self).__init__()
        self.rect = screen.get_rect()
        self.dock = None
        self.screen = screen
        self.fps = fps
        self.bgd = bgd
        self.all = pygame.sprite.LayeredDirty()
        self.drawn_rects = []
        self.player_shots = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.hits_player = pygame.sprite.Group()
        self.hits_player_shot = pygame.sprite.Group()
        self.docks_with_player = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.hot_group = pygame.sprite.LayeredDirty()
        self.player = None
        self.show_boxes = show_boxes
        self.show_grid = show_grid
        self.viewrect = pygame.Rect((0, 0), self.rect.size)
        self.scrollrect = self.rect.inflate(self.rect.width / 6 -
                                            self.rect.width,
                                            self.rect.height / 6 -
                                            self.rect.height)
        self.cullrect = self.rect.inflate(self.rect.width * CULL_FACTOR,
                                          self.rect.height * CULL_FACTOR)

    def __nonzero__(self):
        """Return true iff the level is still 'active'.

        Allows the caller to use an expression like this for the main
        loop:

        while mylevel:
            mylevel.update()
            # do other per-frame activities

        """
        if (self.player and self.player.alive()) or self.explosions:
            return True
        else:
            return False

    def add(self, sprite, maploc):
        """Add a sprite to the level.

        This classifies the sprite based on its class type (for
        collision checking) and assigns its map location.

        """
        sprite.put_at(self, maploc)
        if isinstance(sprite, spaceobj.Explosion):
            self.explosions.add(sprite)
        elif isinstance(sprite, spaceobj.PlayerShot):
            self.player_shots.add(sprite)
        elif isinstance(sprite, spaceobj.PlayerShip):
            self.player = sprite
        if isinstance(sprite, spaceobj.CollidesWithPlayer):
            self.hits_player.add(sprite)
        if isinstance(sprite, spaceobj.CollidesWithPlayerShot):
            self.hits_player_shot.add(sprite)
        if isinstance(sprite, spaceobj.DocksWithPlayer):
            self.docks_with_player.add(sprite)
        if isinstance(sprite, spaceobj.Pickup):
            self.pickups.add(sprite)
        self.all.add(sprite)
        return sprite

    def view(self, sprite):
        """Center the viewrect on the sprite."""
        offset = vector.subtract(sprite.rect.center, self.viewrect.center)
        self.scroll(offset)

    def start(self):
        """Start the level.

        Call once before calling update() or scroll().

        """
        self.bgd.blit(self.screen, self.rect)
        pygame.display.flip()

    def paint_grid(self):
        """Paint a grid on the background.

        Returns the list of dirty rectangles.

        """
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
        """Kill sprites outside the culling rectangle."""
        for sprite in self.all:
            if not self.cullrect.contains(sprite.maprect) and \
                    not isinstance(sprite, spaceobj.DocksWithPlayer):
                sprite.kill()

    def update_hot_group(self):
        """Rebuild the list of visible sprites."""
        self.hot_group.empty()
        for sprite in self.all:
            if self.viewrect.colliderect(sprite.maprect):
                self.hot_group.add(sprite)
                sprite.pre_render()

    def update(self):
        """Animate, run AI and handle collisions.

        Should be called every frame. Erases the dirty rects from the
        last update and makes some more. Handles scrolling, updating
        all the sprites, repainting them, and checking for collisions.

        """
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
            self.scroll((0, (self.player.rect.bottom -
                             self.scrollrect.bottom)))
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
        if self.show_grid:
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
        if self.player.alive():
            self.drawn_rects.append(self.player.draw_velocity())
        # # draw angles
        # for sprite in self.all:
        #     if hasattr(sprite, 'draw_angle'):
        #         self.drawn_rects.append(sprite.draw_angle())
        dirty_rects = erased_rects + self.drawn_rects
        #pygame.display.update(dirty_rects)

        # Collision checking.
        if self.hits_player:
            if self.player.alive():
                group = [sprite for sprite in self.hot_group if
                         isinstance(sprite, spaceobj.CollidesWithPlayer)]
                other = _check_collision(self.player, group)
                if other:
                    other.destroy()
                    self.player.destroy()
        if self.hits_player_shot:
            group = [sprite for sprite in self.hot_group if
                     isinstance(sprite, spaceobj.CollidesWithPlayerShot)]
            hits = _check_group_collision(group, self.player_shots)
            for hit in hits:
                hit[0].destroy()
                hit[1].destroy()
        if self.docks_with_player:
            if self.player.alive():
                group = [sprite for sprite in self.hot_group if
                         isinstance(sprite, spaceobj.DocksWithPlayer)
                         and sprite.ready_to_dock]
                other = _check_dock(self.player, group)
                if other:
                    self.dock = other
        if self.pickups:
            if self.player.alive():
                group = [sprite for sprite in self.hot_group if
                         isinstance(sprite, spaceobj.Pickup)]
                other = _check_collision(self.player, group)
                if other:
                    self.player.get(other)
                    other.kill()
        return dirty_rects

    def scroll(self, offset):
        """Scroll the view."""
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
        """Get a randomly located offscreen rectangle.

        Get a random position for a rect of size 'size' within the
        cullrect but outside the viewrect. This is for adding sprites
        to the level so they don't appear to "teleport" into view.

        """
        position = vector.randintrect(self.cullrect)
        rect = pygame.Rect(position, size)
        while self.viewrect.contains(rect):
            position = vector.randintrect(self.cullrect)
            rect = pygame.Rect(position, size)
        return position
