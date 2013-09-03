""" An Animation is a sequence of frames (images). """

import pygame

class Animation(object):
    """ A description of an animation, including the frame sequence. """
    def __init__(self, ticks_per_frame=0, frames=None, loop=True):
        self.frames = frames or []
        self.ticks_per_frame = ticks_per_frame
        self.loop = loop

    def append_frame(self, frame):
        """ Append a frame to the animation. """
        if not isinstance(frame, pygame.Surface):
            raise TypeError('{} is not a pygame.Surface'.format(type(frame)))
        self.frames.append(frame)

    def get_view(self):
        return AnimationView(self)


class SingleFrameAnimation(object):
    """ Special case of an animation with only one frame. """
    def __init__(self, frame):
        if not isinstance(frame, pygame.Surface):
            raise TypeError('{} is not a pygame.Surface'.format(type(frame)))
        self.frame = frame

    def get_view(self):
        return SingleFrameAnimationView(self)


class AnimationView(object):
    """ Manages the state of an animation so it can be used by multiple
    objects. """
    def __init__(self, animation):
        self.animation = animation
        self.ticks_remaining = self.animation.ticks_per_frame
        self.frameno = 0
        self.done = False
        self.frame = self.animation.frames[self.frameno]        

    def update(self):
        """ Advance the state of the animation. """
        if self.done:
            return False
        self.ticks_remaining -= 1
        if self.ticks_remaining <= 0:
            self.frameno += 1
            if self.frameno == len(self.animation.frames):
                self.frameno = 0
                if not self.animation.loop:
                    self.done = True
            self.ticks_remaining = self.animation.ticks_per_frame
            self.frame = self.animation.frames[self.frameno]
            return True
        return False


class SingleFrameAnimationView(AnimationView):
    """ Viewer for a single-frame animation. """
    def __init__(self, animation):
        if not isinstance(animation, SingleFrameAnimation):
            raise TypeError('animation must be a SingleFrameAnimation')
        self.frame = animation.frame

    def update(self):
        pass

def load_image(filename):
    return pygame.image.load(filename).convert_alpha()

def load(dirname, fps, descr):
    """ 
    Load an animation where 'dirname' contains image files and 'descr' is a
    dictionary.
    """
    if len(descr['frames']) == 1:
        return SingleFrameAnimation(load_image(dirname + '/' + \
                                                   descr['frames'][0]))
    animation = Animation(fps/descr.get('fps', 1), 
                          loop=descr.get('loop', True))
    for frame in descr['frames']:
        animation.append_frame(load_image(dirname + '/' + frame))
    return animation
