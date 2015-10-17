#
# Copyright (c) Gordon McNutt, 2013
#
import json
import os
import pygame


class Font(object):
    """ Abstract base class which defines the required fields and methods for
    all Font classes. """
    def __init__(self):
        self.max_width = 0
        self.max_height = 0

    def write(self, surf, rect, text):
        raise NotImplemented("Abstract method")

    def get_dims(self, char):
        raise NotImplemented("Abstract method")


class ImageFont(Font):
    """A Font from an image."""

    def __init__(self, image, rects):
        """ Make a font from Surface 'image', where the position of each letter
        is given by a Rect in 'rects', in ASCII order. """
        self.image = image
        self.rects = rects
        self.max_width = max([r.width for r in rects.values()])
        self.max_height = max([r.height for r in rects.values()])

    def write(self, surf, rect, text):
        """ Write 'text' onto 'surf' within rectangle 'rect'. """
        dest = rect.copy()
        for char in text:
            area = self.rects[char]
            dest.size = area.size
            if rect.contains(dest):
                surf.blit(self.image, dest, area)
            if char == '\n':
                dest.top += dest.height
                dest.left = rect.left
            else:
                dest.left += dest.width

    def get_dims(self, char):
        return self.rects[char]


class AfterFont(ImageFont):
    """ A Font created from a JSON file formatted for the game After. """

    def __init__(self, jsonfile, imagedir):
        """ Make an image file by parsing 'jsonfile'. """
        descr = json.loads(open(jsonfile).read())
        image = pygame.image.load(os.path.join(imagedir,
                                               descr['image_filename']))
        rects = {}
        for k, v in descr['rects'].items():
            rects[k] = pygame.Rect(v)
        super(AfterFont, self).__init__(image, rects)

    def write(self, surf, rect, text):
        text = text.upper()
        return super(AfterFont, self).write(surf, rect, text)

    def get_dims(self, char):
        return super(AfterFont, self).get_dims(char.upper())
