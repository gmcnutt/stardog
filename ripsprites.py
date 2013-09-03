#!/usr/bin/python

import pygame
import sys

if len(sys.argv) != 4:
    print("Usage: ripsprites.py <image> <rows> <cols>")
    sys.exit(0)

fname = sys.argv[1]
rows = int(sys.argv[2])
cols = int(sys.argv[3])

num = rows * cols
if not num:
    raise Exception("number of image can't be zero")

source = pygame.image.load(fname)
srect = source.get_rect()

if srect.width % cols != 0:
    raise Exception("width {} not a multiple of columns {}".format(srect.width, cols))

if srect.height % rows != 0:
    raise Exception("height {} not a multiple of rows {}".format(srect.height, rows))

width = int(srect.width/cols)
height = srect.height/rows

path = '/'.join(fname.split('/')[:-1])
prefix = fname.split('/')[-1].split('.')[0]
index = 0

pygame.init()
pygame.display.set_mode((240,320))

for row in range(rows):
    area = pygame.Rect(0, height * row, width, height)
    for col in range(cols):
        dest = pygame.Surface((width, height)).convert_alpha(source)
        dest.blit(source, (0, 0), area)
        pygame.image.save(dest, '%s/%d.png'%(path, index))
        area.move_ip(width, 0)
        index += 1
