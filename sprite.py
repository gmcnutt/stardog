"""Custom sprites for space objects."""
#
# Copyright (c) Gordon McNutt, 2013
#

import animation
import json
import pygame
import math
import random
import vector

DOODAD_LAYER = 0
DEFAULT_LAYER = 1
PLAYER_LAYER = 3


class CollidesWithPlayer(object):
    """Mix-in used for identification."""
    pass


class DocksWithPlayer(object):
    """Mix-in used for identification."""
    pass


class CollidesWithPlayerShot(object):
    """Mix-in used for identification."""
    pass


class Pickup(object):
    """Mix-in used for identification."""
    pass


class BaseSprite(pygame.sprite.DirtySprite):
    """A sprite with a rect for collision detection and a maprect for showing
    in a viewer.
    """
    def __init__(self):
        super(BaseSprite, self).__init__()
        self.dirty = 2  #  Always dirty (repainted each frame)
        self._layer = DEFAULT_LAYER
        self.maprect = None  # Offset from map viewer ULC
        self.rect = None  # Offset from universal ULC

    def move(self, offset):
        """Move the sprite by 'offset'."""
        if offset[0] or offset[1]:
            self.rect.move_ip(offset)
            self.maprect.move_ip(offset)

    def destroy(self):
        """Explode and exit stage."""
        self.level.add(Explosion(), self.maprect.center)
        self.kill()

    def scroll(self, offset):
        self.rect.move_ip(offset)

    def put_at(self, level, maploc):
        self.level = level
        self.maprect = self.rect.copy()
        self.maprect.center = maploc
        self.rect.center = vector.subtract(maploc, level.viewrect.topleft)


class EnemyShip(object):
    """Abstract mix-in for classification."""
    color = (255, 0, 0)


class ModelObject(BaseSprite):
    """A sprite that gets its images from a model (a table of
    animations). Subclasses should override the class instance variable
    __model__.
    """

    __model__ = None

    def __init__(self, velocity=None, angular_velocity=0):
        super(ModelObject, self).__init__()
        if velocity and not isinstance(velocity, list):
            raise TypeError('velocity must be a list, not {}'.
                            format(type(velocity)))
        self.animation_view = self.__model__['default'].get_view()
        self._set_image(self.animation_view.frame)
        self.velocity = velocity or [0, 0]
        self.angular_velocity = angular_velocity
        self.angle = 0

    def _set_image(self, image, original=True, remask=True):
        """Set the current sprite image and rect and rebuild the collision
        mask. Unless rotated remember this as the original prior to
        rotation."""
        self.image = image
        if remask:
            self.mask = pygame.mask.from_surface(self.image)
        old_rect = self.rect
        self.rect = self.image.get_rect()
        if old_rect:
            self.rect.center = old_rect.center
        if original:
            self.original_image = image

    def pre_render(self):
        """Prepare to blit the image."""
        if self.angle:
            self._rotate_image()

    def _rotate_image(self):
        """Rotate the current image and update the rect and collision
        mask. Recenters the rotated image in the old location."""
        center = self.rect.center
        image = pygame.transform.rotate(self.original_image, self.angle)
        self._set_image(image, False)
        self.rect.center = center

    def update(self):
        """Update the animation then move and rotate."""
        if self.animation_view.update():
            self._set_image(self.animation_view.frame, remask=False)
        self.move(self.velocity)
        self.angle += self.angular_velocity

    def draw_angle(self):
        """Draw a line representing the angle """
        direction = vector.from_angle(self.angle)
        vect = vector.scalar_multiply(direction, 20)
        endpos = vector.add(self.rect.center, vect)
        return pygame.draw.line(self.level.screen, (255, 255, 0),
                                self.rect.center,
                                endpos)

    def draw_velocity(self):
        """Draw a line representing the velocity."""
        vect = vector.scalar_multiply(self.velocity, 10)
        endpos = vector.add(self.rect.center, vect)
        return pygame.draw.line(self.level.screen, (0, 255, 255),
                                self.rect.center,
                                endpos)


class TickShot(ModelObject, CollidesWithPlayer):

    def __init__(self, **kwargs):
        super(TickShot, self).__init__(**kwargs)
        self.ttl = 3 * 60  # FIXME: assumes 60 fps

    def update(self):
        super(TickShot, self).update()
        self.ttl -= 1
        if self.ttl <= 0:
            self.kill()


class TickShip(ModelObject, EnemyShip, CollidesWithPlayer,
               CollidesWithPlayerShot):

    def __init__(self, **kwargs):
        super(TickShip, self).__init__(**kwargs)
        self._init_shoot(1 * 60)

    def update(self):
        super(TickShip, self).update()
        self._shoot()

    def _init_shoot(self, period):
        self.shot_period = period
        self.ticks_to_fire = period

    def _shoot(self):
        self.ticks_to_fire -= 1
        if self.ticks_to_fire <= 0:
            direction = vector.from_angle(self.angle + 180)
            velocity = vector.scalar_multiply(direction, 3)
            location = vector.add(
                self.maprect.center,
                vector.scalar_multiply(direction,
                                       self.maprect.width / 2))
            #self.level.add(EnemyShot(velocity), location)
            self.level.add(TickShot(velocity=list(velocity)),
                           location)
            self.ticks_to_fire = self.shot_period


class Asteroid(ModelObject, CollidesWithPlayer, CollidesWithPlayerShot):
    """Rotating destructible rock."""
    color = (160, 160, 160)
    pass


class OreAsteroid(Asteroid):
    """Asteroid that yields ore when destroyed."""

    def destroy(self):
        vel = vector.add(vector.randint(3, 3), self.velocity)
        self.level.add(Ore(velocity=[vel[0], vel[1]],
                                angular_velocity=random.randint(0, 5)),
                       self.maprect.center)
        super(OreAsteroid, self).destroy()


class BigAsteroid(Asteroid):
    """Rotating destructible rock that spawns smaller rocks when
    destroyed."""
    color = (128, 128, 128)

    def destroy(self):
        """Spawn 0-2 child asteroids."""
        for i in range(2):
            vel = vector.add(vector.randint(3, 3), self.velocity)
            self.level.add(Asteroid(velocity=[vel[0], vel[1]],
                                    angular_velocity=random.randint(0, 5)),
                           self.maprect.center)
        if random.randint(0, 10) < 5:
            self.level.add(OreAsteroid(velocity=[vel[0], vel[1]],
                                       angular_velocity=random.randint(0, 5)),
                           self.maprect.center)
        super(BigAsteroid, self).destroy()


class PlayerShot(ModelObject):
    """Bullet sprite."""
    # To make shots more accurate, overload move(), update() and scroll() so
    # that instead of incrementing the rects recompute them from the
    # origin. The normal method of simply incrementing the rects causes
    # roundoff errors to accumulate and the shot will miss the original target
    # location.
    def __init__(self, **kwargs):
        super(PlayerShot, self).__init__(**kwargs)
        self.ttl = 5 * 60

    def put_at(self, *args):
        super(PlayerShot, self).put_at(*args)
        self.original_rect = self.rect.copy()
        self.original_maprect = self.maprect.copy()
        self.moves = 0
        self.scroll_offset = 0, 0

    def scroll(self, offset):
        self.scroll_offset = vector.add(self.scroll_offset, offset)

    def move(self, offset):
        self.moves += 1
        toff = vector.scalar_multiply(self.velocity, self.moves)
        self.rect = self.original_rect.move(vector.add(toff,
                                                       self.scroll_offset))
        self.maprect = self.original_maprect.move(toff)
        self.ttl -= 1
        if self.ttl <= 0:
            self.kill()


class PlayerShip(ModelObject):
    """The player's ship. Responds to mouse position and buttons."""

    color = (0, 255, 0)

    def __init__(self, ammo=500, **kwargs):
        super(PlayerShip, self).__init__(**kwargs)
        self.max_accel = 0.25
        self.accel_damp = 1.0
        self._layer = PLAYER_LAYER
        self.max_shots = 20
        self.fire_wait_tick = 10
        self.ammo = ammo
        self.ore = 0

    def _fire(self):
        """Fire if the mouse button is held down."""
        buttons = pygame.mouse.get_pressed()
        if buttons[0] and self.ammo and self.fire_wait_tick <= 0:
            pos = pygame.mouse.get_pos()
            velocity = vector.subtract(pos, self.rect.center)
            velocity = vector.normalize(velocity)
            velocity = vector.scalar_multiply(velocity, 10)
            velocity = vector.add(velocity, vector.intvector(self.velocity))
            self.level.add(PlayerShot(velocity=list(velocity)),
                           self.maprect.center)
            self.fire_wait_tick = 10
            self.ammo -= 1
        else:
            self.fire_wait_tick -= 1

    def _rotate(self):
        """Rotate the ship to face the current mouse position."""
        mousepos = pygame.mouse.get_pos()
        dx = self.rect.centerx - mousepos[0]
        dy = self.rect.centery - mousepos[1]
        # Note: dy != 0 since we divide by it; the > N is to prevent erratic
        # wobbling when the mouse is near the center.
        if abs(dx) > 2 and abs(dy) > 2:
            tangent = float(dx) / float(dy)
            angle = math.degrees(math.atan(tangent))
            if (dy < 0):
                angle = 180.0 + angle
            self.angle = angle

    def _get_acceleration(self, err, vel):
        """Computes acceleration so that the ship will accelerate toward the
        mouse and decelerate as it gets close."""
        if abs(err) < 2 and not vel:
            return 0
        if not vel:
            if err > 0:
                return 1
            else:
                return -1
        # eta: estimated time of arrival; the time remaining until err=0 at
        # current vel
        eta = err / vel
        # ets: estimated time to stop; the time required to reduce vel to 0 at
        # max decel
        ets = abs(vel) / self.max_accel
        # adjust accel to make eta and ets equal on the next iteration,
        # assuming constant error
        import math
        if err > 0:
            accel = math.sqrt(err * self.max_accel) - vel
        else:
            accel = -vel - math.sqrt(abs(err) * self.max_accel)
        if accel > 0:
            accel = min(accel, self.max_accel)
        else:
            accel = max(accel, -self.max_accel)
        return accel

    def _accelerate(self):
        """Computes acceleration and adjusts velocity."""
        pos = pygame.mouse.get_pos()
        errv = pos[0] - self.rect.centerx, pos[1] - self.rect.centery
        accx = self._get_acceleration(errv[0], self.velocity[0])
        accy = self._get_acceleration(errv[1], self.velocity[1])
        if accx or accy:
            self.velocity = self.velocity[0] + accx, \
                self.velocity[1] + accy

    def update(self):
        """Fire, rotate and move."""
        self._fire()
        self._rotate()
        if not (pygame.KMOD_SHIFT & pygame.key.get_mods()):
            self._accelerate()
        self.move(self.velocity)

    def get(self, sprite):
        self.ore += 1


class Explosion(ModelObject):
    """An explosion."""
    def update(self):
        super(Explosion, self).update()
        if self.animation_view.done:
            self.kill()


class Stardock(ModelObject, DocksWithPlayer):
    """The player can dock here."""
    color = (255, 255, 128)

    def __init__(self, **kwargs):
        ModelObject.__init__(self, **kwargs)
        self._cooldown = 0

    def _set_image(self, image, *args, **kwargs):
        super(Stardock, self)._set_image(image, *args, **kwargs)
        self.dock_rect = self.rect.inflate(-self.rect.width * 0.90,
                                           -self.rect.height * 0.90)

    def start_cooldown(self, ticks):
        self.animation_view = self.__model__['cooldown'].get_view()
        self._set_image(self.animation_view.frame)
        self._cooldown = ticks

    def update(self):
        super(Stardock, self).update()
        if self._cooldown > 0:
            self._cooldown -= 1
            if self._cooldown == 0:
                self.animation_view = self.__model__['default'].get_view()
                self._set_image(self.animation_view.frame)

    @property
    def ready_to_dock(self):
        return self._cooldown == 0


class Ore(ModelObject, Pickup):
    """Ore that the player can pick up."""
    color = (0, 128, 255)
