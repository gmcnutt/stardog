import sys
sys.path.append('../')

import animation
import pygame
import unittest

pygame.init()
pygame.display.set_mode((240,320))

class AnimationCheck(unittest.TestCase):
    def test_defaults(self):
        anim = animation.Animation()
        self.assertEqual(anim.frames, [])
        self.assertEqual(anim.ticks_per_frame, 0)
        self.assertEqual(anim.loop, True)

    def test_append_non_image(self):
        anim = animation.Animation(0)
        self.assertRaises(TypeError, anim.append_frame, None)

    def test_append_image(self):
        anim = animation.Animation(0)
        anim.append_frame(pygame.image.load('./test1.png'))
        self.assertEqual(len(anim.frames), 1)

    def test_ctor_with_frames(self):
        anim = animation.Animation(frames=[pygame.image.load('./test1.png')])
        self.assertEqual(len(anim.frames), 1)

class AnimationLoadCheck(unittest.TestCase):
    def setUp(self):
        self.dirname = './'

    def test_basic(self):
        anim = animation.load(self.dirname, 60, {'fps':3,
                                                 'loop': True,
                                                 'frames':['test1.png',
                                                           'test2.png']})
        self.assertEqual(len(anim.frames), 2)
        self.assertTrue(anim.loop)

    def test_loop_false(self):
        anim = animation.load(self.dirname, 60, {'fps':3,
                                                 'loop': False,
                                                 'frames':['test1.png',
                                                           'test2.png']})
        self.assertEqual(len(anim.frames), 2)
        self.assertFalse(anim.loop)

    def test_empty_frames(self):
        anim = animation.load(self.dirname, 60, {'fps':3,
                                                 'frames':[]})
        self.assertEqual(len(anim.frames), 0)
        self.assertTrue(anim.loop)

class AnimationViewCheck(unittest.TestCase):
    def setUp(self):
        self.images = [pygame.image.load('./test1.png'),
                       pygame.image.load('./test2.png')]
        self.anim = animation.Animation(2, self.images)

    def test_empty_animation(self):
        anim = animation.Animation()
        self.assertRaises(IndexError, animation.AnimationView, anim)

    def test_done(self):
        anim = animation.Animation(frames=[self.images[0]], loop=False)
        avw = animation.AnimationView(anim)
        self.assertTrue(avw.update())
        self.assertTrue(avw.done)
        self.assertFalse(avw.update())
        self.assertTrue(avw.done)

    def test_one_loop(self):
        avw = animation.AnimationView(self.anim)
        self.assertFalse(avw.update())
        self.assertFalse(avw.done)
        self.assertTrue(avw.update())
        self.assertFalse(avw.done)
        self.assertFalse(avw.update())
        self.assertFalse(avw.done)

suite = unittest.TestSuite()

suite.addTest(unittest.makeSuite(AnimationViewCheck, 'test'))
suite.addTest(unittest.makeSuite(AnimationCheck, 'test'))
suite.addTest(unittest.makeSuite(AnimationLoadCheck, 'test'))

if __name__ == '__main__':
    unittest.main()
