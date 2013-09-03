import sys
sys.path.append('../')

import level
import model
import pygame
import sprite
import unittest

pygame.init()
SCREEN=pygame.display.set_mode((240,320))

class LoadCheck(unittest.TestCase):
    def setUp(self):
        self.dirname = 'models/oneanim'

    def test_normal(self):
        mdl = model.load('models/oneanim', 60)
        self.assertIsNotNone(mdl['default'])
        anim = mdl['default']
        self.assertTrue(anim.loop)
        self.assertEquals(anim.ticks_per_frame, 20)
        self.assertEquals(len(anim.frames), 3)

    def test_single_frame(self):
        mdl = model.load('models/oneframe', 60)
        self.assertIsNotNone(mdl['default'])

suite = unittest.makeSuite(LoadCheck,'test')

class ModelObjectTest(unittest.TestCase):
    def setUp(self):
        self.model = model.load('models/oneanim', 6)

    def test_ctor(self):
        modobj = sprite.ModelObject(self.model)
        self.assertIsNotNone(modobj.image)
        self.assertIsNotNone(modobj.mask)
        self.assertIsNotNone(modobj.rect)
        self.assertIsNotNone(modobj.original_image)
        self.assertEquals(modobj.original_image, modobj.image)
        self.assertEquals(modobj.velocity, [0, 0])

    def test_set_image(self):
        modobj = sprite.ModelObject(self.model)
        new_image = pygame.image.load('./test1.png')
        original_image = modobj.image
        modobj._set_image(new_image, False)
        self.assertEquals(modobj.image, new_image)
        self.assertEquals(modobj.original_image, original_image)
        modobj._set_image(new_image, True)
        self.assertEquals(modobj.image, new_image)
        self.assertEquals(modobj.original_image, new_image)

    def test_rotate(self):
        modobj = sprite.ModelObject(self.model)
        self.assertEquals(modobj.angle, 0)
        modobj.rotate(0)
        self.assertEquals(modobj.angle, 0)
        self.assertIsNotNone(modobj.image)
        self.assertIsNotNone(modobj.mask)
        self.assertIsNotNone(modobj.rect)
        self.assertIsNotNone(modobj.original_image)
        self.assertNotEqual(modobj.original_image, modobj.image)
        modobj.rotate(25)
        self.assertEquals(modobj.angle, 25)
        self.assertIsNotNone(modobj.image)
        self.assertIsNotNone(modobj.mask)
        self.assertIsNotNone(modobj.rect)
        self.assertIsNotNone(modobj.original_image)
        self.assertNotEqual(modobj.original_image, modobj.image)
        modobj.rotate(16)
        self.assertEquals(modobj.angle, 25+16)
        self.assertIsNotNone(modobj.image)
        self.assertIsNotNone(modobj.mask)
        self.assertIsNotNone(modobj.rect)
        self.assertIsNotNone(modobj.original_image)
        self.assertNotEqual(modobj.original_image, modobj.image)
        modobj.rotate(-121.456)
        self.assertEquals(modobj.angle, 25+16-121.456)
        self.assertIsNotNone(modobj.image)
        self.assertIsNotNone(modobj.mask)
        self.assertIsNotNone(modobj.rect)
        self.assertIsNotNone(modobj.original_image)
        self.assertNotEqual(modobj.original_image, modobj.image)
        modobj.rotate(-121234329874398798.45632434543)
        self.assertEquals(modobj.angle, 
                          25+16-121.456-121234329874398798.45632434543)
        self.assertIsNotNone(modobj.image)
        self.assertIsNotNone(modobj.mask)
        self.assertIsNotNone(modobj.rect)
        self.assertIsNotNone(modobj.original_image)
        self.assertNotEqual(modobj.original_image, modobj.image)
        
    def test_update_1(self):
        """ Test update with no animation update, no angular velocity, no
        velocity """
        modobj = sprite.ModelObject(self.model)
        level.Level(screen=SCREEN).add(modobj, (11, 11))
        modobj.update()
        self.assertEquals(modobj.image, modobj.animation_view.frame)
        self.assertEquals(modobj.maprect.topleft, (0, 0))
        self.assertEquals(modobj.rect.topleft, (0, 0))

    def test_update_2(self):
        """ Test update with animation update, no angular velocity, no
        velocity """
        modobj = sprite.ModelObject(self.model)
        level.Level(screen=SCREEN).add(modobj, (11, 11))
        original_image = modobj.image
        modobj.update()
        self.assertEqual(modobj.image, original_image)
        modobj.update()
        self.assertNotEqual(modobj.image, original_image)
        modobj.update()
        self.assertNotEqual(modobj.image, original_image)
        modobj.update()
        self.assertNotEqual(modobj.image, original_image)
        modobj.update()
        self.assertNotEqual(modobj.image, original_image)
        modobj.update()
        self.assertEqual(modobj.image, original_image)
        modobj.update()
        self.assertEqual(modobj.image, original_image)

    def test_update_3(self):
        """ Test update with velocity """
        modobj = sprite.ModelObject(self.model)
        level.Level(mapsize=(1000, 1000), screen=SCREEN).add(modobj, (100, 100))
        modobj.velocity = [1, 1]
        modobj.update()
        self.assertEquals(modobj.maprect.center, (101, 101))
        self.assertEquals(modobj.maprect.topleft, (90, 90))
        self.assertEquals(modobj.rect.topleft, (90, 90))
        modobj.update()
        self.assertEquals(modobj.maprect.center, (102, 102))
        self.assertEquals(modobj.maprect.topleft, (91, 91))
        self.assertEquals(modobj.rect.topleft, (91, 91))
        modobj.velocity = [0, -1]
        modobj.update()
        self.assertEquals(modobj.maprect.topleft, (91, 90))
        self.assertEquals(modobj.rect.topleft, (91, 90))
        modobj.velocity = [-1, 0]
        modobj.update()
        self.assertEquals(modobj.maprect.topleft, (90, 90))
        self.assertEquals(modobj.rect.topleft, (90, 90))
        modobj.velocity = [-1, -1]
        modobj.update()
        self.assertEquals(modobj.maprect.topleft, (89, 89))
        self.assertEquals(modobj.rect.topleft, (89, 89))
        modobj.update()
        self.assertEquals(modobj.maprect.topleft, (88, 88))
        self.assertEquals(modobj.rect.topleft, (88, 88))

    def test_update_4(self):
        """ Test update with angular velocity """
        modobj = sprite.ModelObject(self.model)
        level.Level(screen=SCREEN).add(modobj, (11, 11))
        modobj.angular_velocity = 1
        modobj.update()
        self.assertEquals(modobj.angle, 1)
        self.assertEquals(modobj.maprect.topleft, (0, 0))
        self.assertEquals(modobj.rect.topleft, (0, 0))
        self.assertEquals(modobj.rect.center, (11, 11))
        modobj.update()
        self.assertEquals(modobj.angle, 2)
        self.assertEquals(modobj.maprect.topleft, (0, 0))
        self.assertEquals(modobj.rect.topleft, (0, 0))
        self.assertEquals(modobj.rect.center, (11, 11))
        modobj.angular_velocity = 90
        modobj.update()
        self.assertEquals(modobj.angle, 92)
        self.assertEquals(modobj.maprect.topleft, (0, 0))
        self.assertEquals(modobj.rect.topleft, (0, 0))
        self.assertEquals(modobj.rect.center, (11, 11))
        modobj.angular_velocity = 43
        modobj.update()
        self.assertEquals(modobj.angle, 135)
        self.assertEquals(modobj.maprect.topleft, (0, 0))
        self.assertEquals(modobj.rect.topleft, (-5, -5))
        self.assertEquals(modobj.rect.center, (11, 11))
        modobj.angular_velocity = 45
        modobj.update()
        self.assertEquals(modobj.angle, 180)
        self.assertEquals(modobj.maprect.topleft, (0, 0))
        self.assertEquals(modobj.rect.topleft, (0, 0))
        self.assertEquals(modobj.rect.center, (11, 11))

    def test_scroll(self):
        modobj = sprite.ModelObject(self.model)
        level.Level(screen=SCREEN).add(modobj, (11, 11))
        modobj.scroll((10, 10))
        self.assertEquals(modobj.maprect.topleft, (0, 0))
        self.assertEquals(modobj.maprect.center, (11, 11))
        self.assertEquals(modobj.rect.topleft, (10, 10))
        self.assertEquals(modobj.rect.center, (21, 21))
 
####    def test_put_at(self):
####        modobj = sprite.ModelObject(self.model)
####        level = object()
####        level.viewrect = pygame.Rect((12, 34), (56, 78))
####        maploc = (10, 20)
####        modobj.put_at(level, maploc)
####        self.assertEquals(modobj.level, level)
####        self.assertEquals(modobj.maprect, modobj.rect)
####        self.assertEquals(modobj.maprect.center, maploc)
####        self.assertEquals(modobj.rect.center, (-2, -14))

suite.addTest(unittest.makeSuite(ModelObjectTest, 'test'))


if __name__ == '__main__':
    unittest.main()
