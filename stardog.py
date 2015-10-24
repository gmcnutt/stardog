"""Stardog - a 2d space shooter game."""

from level import *
import argparse
import font
import minimap
import model
import os
import pygame
import random
import sprite
import sys
import ui
import vector

SIZE = WIDTH, HEIGHT = 480 * 2, 480 * 2
FPS = 60
MAX_SHOTS = 20
SCROLL = 50
ROOTDIR = os.path.dirname(__file__)
IMAGEDIR = os.path.join(ROOTDIR, "art", "png")
MODELDIR = os.path.join(ROOTDIR, 'models')


def align_horz(rect, align):
    lm = rect.left % align
    rm = align - (rect.right % align)
    rect.left -= lm
    rect.width += (lm + rm)


def align_vert(rect, align):
    lm = rect.top % align
    rm = align - (rect.bottom % align)
    rect.top -= lm
    rect.height += (lm + rm)


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
        dialog = ui.OkDialog(font=self.font, text=msg, surf=self.screen)
        self.layout_and_center(dialog).run()

    def choose(self, options):
        dialog = ui.OptionDialog(font=self.font, options=options,
                                 surf=self.screen)
        return self.layout_and_center(dialog).run()

    def show(self, msg):
        wrapper = ui.Wrapper(
            widget=ui.Label(font=self.font, text=msg, surf=self.screen),
            surf=self.screen)
        self.layout_and_center(wrapper)
        pygame.display.update(wrapper.paint())


class Background(object):

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
        path = os.path.join(IMAGEDIR, fname)
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()

    def blit(self, surf, dest):
        dest2 = dest.copy()
        align_horz(dest2, self.rect.width)
        align_vert(dest2, self.rect.height)
        area = self.rect.copy().move(dest2.topleft)
        for row in range(dest2.height / area.height):
            for col in range(dest2.width / area.width):
                surf.blit(self.image, area)
                area.left += area.width
            area.top += area.height
            area.left = dest2.left


def add_ticks(level, num):
    for i in range(num):
        vel = vector.subtract(vector.randint(7, 7), (3, 3))
        position = level.get_offscreen_position((22, 22))
        level.add(sprite.TickShip(velocity=list(vel),
                                  angular_velocity=random.random() * 5),
                  position)


def add_asteroids(level, num):
    for i in range(num):
        vel = vector.subtract(vector.randint(7, 7), (3, 3))
        position = level.get_offscreen_position((50, 50))
        level.add(sprite.BigAsteroid(velocity=list(vel),
                                     angular_velocity=random.random() * 5),
                  position)

def add_tick_factories(level, num):
    for i in range(num):
        position = level.get_offscreen_position((50, 50))
        level.add(sprite.TickFactory(angular_velocity=1), position)

def run(screen, args, gui):
    level = Level(screen=screen,
                  fps=FPS,
                  bgd=FillBackground((0, 0, 0)),
                  show_boxes=False, show_grid=args.grid)

    level.add(sprite.PlayerShip(), level.rect.center)
    level.view(level.player)

    level.add(sprite.Stardock(angular_velocity=1),
              (level.rect.center[0] + 100, level.rect.center[1] + 100))
    stardock2 = level.add(sprite.Stardock(angular_velocity=1),
                          (level.rect.center[0] + 5000,
                           level.rect.center[1] + 5000))

    add_tick_factories(level, 10)
    #add_ticks(level, 10)
    add_asteroids(level, 100)

    large_font = font.AfterFont(os.path.join(ROOTDIR, 'large_font.json'),
                                IMAGEDIR)

    clock = pygame.time.Clock()
    def fps_tick():
        clock.tick(FPS)
        return int(clock.get_fps())

    fps_counter = ui.ValueLabel(pos=(0, screen.get_rect().height - 20),
                                title="FPS",
                                value_func=fps_tick,
                                font=large_font,
                                surf=screen)
    obj_counter = ui.ValueLabel(
        pos=(fps_counter.rect.right, fps_counter.rect.top),
        title="Objects",
        value_func=lambda: len(level.all),
        font=large_font, 
        surf=screen)
    mmap = minimap.LevelMap(level, 100, (0, 0), surf=screen,
                            bgcolor=(64, 64, 64))
    
    ammo_counter = ui.ValueLabel(
        pos=(mmap.rect.right, mmap.rect.top),
        title="Ammo",
        value_func=lambda: level.player.ammo,
        font=large_font, 
        surf=screen)
    ore_counter = ui.ValueLabel(
        pos=(ammo_counter.rect.right, ammo_counter.rect.top),
        title="Ore",
        value_func=lambda: level.player.ore,
        font=large_font,
        surf=screen)

    gui.prompt("Proceed to Stardock 2.")

    level.start()
    loops = 0
    while level:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.unicode == u'q':
                    return
                elif event.unicode == u'n' and args.step:
                    level.update()
                    obj_counter.tick()
                elif event.key == pygame.K_UP:
                    level.scroll((0, -1 * SCROLL))
                elif event.key == pygame.K_DOWN:
                    level.scroll((0, 1 * SCROLL))
                elif event.key == pygame.K_LEFT:
                    level.scroll((-1 * SCROLL, 0))
                elif event.key == pygame.K_RIGHT:
                    level.scroll((1 * SCROLL, 0))
                else:
                    #print('key:{}'.format(event))
                    pass
        dirty = []
        if not args.step:
            dirty = level.update()

        dirty.append(fps_counter.tick())
        dirty.append(ammo_counter.tick())
        dirty.append(ore_counter.tick())
        dirty.append(mmap.paint())
        dirty.append(obj_counter.tick())
        pygame.display.update(dirty)

        if level.dock:
            gui.prompt('Docking')
            level.player.fire_wait_tick = 10  # prevent gratuitous shot
            if level.dock == stardock2:
                gui.prompt("Mission Completed!")
                level.player.fire_wait_tick = 10  # prevent gratuitous shot
            level.player.ammo = 500
            level.dock.start_cooldown(3 * 60)
            level.dock = None


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='An interactive game')
    parser.add_argument('--step', type=bool, default=False,
                        help='step one tick at a time')
    parser.add_argument('--notfullscreen', default=False,
                        action='store_true',
                        help='Run in a window instead of fullscreen')
    parser.add_argument('--grid', default=False, action='store_true',
                        help='Show grid')
    args = parser.parse_args()

    pygame.init()
    if args.notfullscreen:
        screen = pygame.display.set_mode(SIZE)
    else:
        screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.key.set_repeat(1, 25)
    large_font = font.AfterFont(os.path.join(ROOTDIR, 'large_font.json'),
                                IMAGEDIR)
    pygame.mouse.set_cursor(*pygame.cursors.diamond)

    # Load all the models
    model_map = [(sprite.PlayerShip, 'sinistar_Bship'),
                 (sprite.PlayerShot, 'sinistar_bullet_12_3'),
                 (sprite.BigAsteroid, 'tyrian_rock0'),
                 (sprite.Asteroid, 'tyrian_rock1a'),
                 (sprite.TickShip, 'sinistar_ship3'),
                 (sprite.TickShot, 'sinistar_bullet_4_3'),
                 (sprite.Explosion, 'sinistar_Explode3'),
                 (sprite.Stardock, 'sinistar_base'),
                 (sprite.OreAsteroid, 'ore_asteroid'),
                 (sprite.Ore, 'ore'),
                 (sprite.TickFactory, 'tick_factory'),
                 ]
    for pair in model_map:
        pair[0].__model__ = model.load(os.path.join(MODELDIR, pair[1]), FPS)

    gui = UI(screen, large_font)
    run(screen, args, gui)
    while 'Again!' == gui.choose(['Again!', 'Quit']):
        run(screen, args, gui)
    screen.fill((0, 0, 0))
    pygame.display.update()
    gui.show('Thanks for playing!')
