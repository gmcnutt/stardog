#
# Copyright (c) Gordon McNutt, 2013
#

import argparse
import sys
import pygame
import random

import font
from level import *
import model
import os
import sprite
import vector
import ui

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


class FpsCounter(ui.Label):

    def __init__(self, pos, *args, **kwargs):
        super(FpsCounter, self).__init__(*args, **kwargs)
        self.clock = pygame.time.Clock()
        self.rect = pygame.Rect((pos), (300, 20))
        self.fps = 0

    def tick(self):
        self.clock.tick(FPS)
        self.fps = self.clock.get_fps()
        self.text = 'FPS:{}'.format(self.fps)
        #self.layout(self.maxrect)
        self.paint()
        pygame.display.update(self.rect)


class ObjectCounter(ui.Label):

    def __init__(self, pos, group, *args, **kwargs):
        super(ObjectCounter, self).__init__(*args, **kwargs)
        self.rect = pygame.Rect((pos), (300, 20))
        self.group = group

    def tick(self):
        self.count = len(self.group)
        self.text = '{}'.format(self.count)
        #self.layout(self.maxrect)
        self.paint()
        pygame.display.update(self.rect)


def run(screen, args):
    level = Level(screen=screen,
                  fps=FPS,
                  #bgd=TextureBackground("sand.png"),
                  bgd=FillBackground((0, 0, 0)),
                  show_boxes=False)

    hist = {}

    level.add(PlayerShip(), level.rect.center)
    level.view(level.player)

    add_ticks(level, 10)
    add_asteroids(level, 100)

    large_font = font.AfterFont(os.path.join(ROOTDIR, 'large_font.json'),
                                IMAGEDIR)
    fps_counter = FpsCounter((0, screen.get_rect().height - 20),
                             large_font, 'fps: ', screen)
    obj_counter = ObjectCounter((screen.get_rect().width - 300,
                                 screen.get_rect().height - 20),
                                level.all,
                                large_font, '', screen)

    level.start()
    loops = 0
    while level:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.unicode == u'q':
                    for k in sorted(hist.keys()):
                        print(k, hist[k])
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

        if not 'step' in sys.argv:
            level.update()
            obj_counter.tick()
            hist[obj_counter.count] = round(fps_counter.fps)

        fps_counter.tick()

    for k in sorted(hist.keys()):
        print(k, hist[k])


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='An interactive game')
    parser.add_argument('--step', type=bool, default=False,
                        help='step one tick at a time')
    args = parser.parse_args()

    pygame.init()
    # screen=pygame.display.set_mode(SIZE),
    #screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN),
    screen = pygame.display.set_mode(SIZE)
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
                 (sprite.Explosion, 'sinistar_Explode3')
                 ]
    for pair in model_map:
        pair[0].__model__ = model.load(os.path.join(MODELDIR, pair[1]), FPS)

    gui = ui.UI(screen, large_font)
    #gui.prompt("Get Ready!")
    run(screen, args)
    while 'Again!' == gui.choose(['Again!', 'Quit']):
        run(screen, args)
    screen.fill((0, 0, 0))
    pygame.display.update()
    gui.show('Thanks for playing!')