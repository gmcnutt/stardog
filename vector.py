import random as _random
import math

def normalize(v):
    """ Normalize a vector so that the max component is 1. """
    ms = max(abs(v[0]), abs(v[1]))
    if ms:
        vout = float(v[0])/ms, float(v[1])/ms
        return vout
    else:
        return v

def scalar_multiply(v, s):
    """ Multiply a vector by a scalar """
    return v[0] * s, v[1] * s

def scalar_divide(v, s):
    """ Divide a vector by a scalar """
    return v[0] / s, v[1] / s

def subtract(v2, v1):
    """ Return v2 - v1 """
    return v2[0] - v1[0], v2[1] - v1[1]

def add(v2, v1):
    """ Return v2 + v1 """
    return v2[0] + v1[0], v2[1] + v1[1]

def randintrect(rect):
    """ Return a random vector within pygame.Rect 'rect' """
    return int(_random.randint(rect.left, rect.right)), \
        int(_random.randint(rect.top, rect.bottom))
               

def randint(x, y, x0=0, y0=0):
    """ Return a random vector from [x0, y0] to [x, y] """
    return int(_random.randint(x0, x)), int(_random.randint(y0, y))

def randnorm():
    """ Return a random normalized vector """
    return normalize(_random.random(), _random.random())

def intvector(v):
    """ Convert the components to ints. """
    return int(v[0]), int(v[1])

def zero():
    return 0, 0

def to_angle(v):
    """
    Convert a vector to degrees, measured as counter-clockwise rotation from 0,
    which is straight up the y-azis. The result is always positive between [0,
    360).

    >>> to_angle((0, -1))
    0
    >>> to_angle((-0.577, -1))
    30
    >>> to_angle((-1, -1.0))
    45
    >>> to_angle((-1, -0.577))
    60
    >>> to_angle((-1, 0.0))
    90
    >>> to_angle((-1, 0.577))
    120
    >>> to_angle((-1, 1.0))
    135
    >>> to_angle((-0.577, 1))
    150
    >>> to_angle((0, 1))
    180
    >>> to_angle((0.577, 1))
    210
    >>> to_angle((1, 1.0))
    225
    >>> to_angle((1, 0.577))
    240
    >>> to_angle((1, -0.0))
    270
    >>> to_angle((1, -0.577))
    300
    >>> to_angle((1, -1.0))
    315
    >>> to_angle((0.577, -1))
    330
    >>> to_angle((0, -1))
    0
    >>> to_angle((-0.017, -1))
    1
    >>> to_angle((0, -1))
    0
    >>> to_angle((0, -1))
    0
    >>> to_angle((-0.577, -1))
    30
    """
    dx = v[0]
    dy = v[1]
    if not dy:
        if dx > 0:
            return 270
        else:
            return 90
    if not dx:
        if dy < 0:
            return 0
        else:
            return 180
    tangent = float(dx) / float(dy)
    angle = math.degrees(math.atan(tangent))
    if (dy > 0):
        angle = 180 + angle
    else:
        angle = (360 + angle) % 360
    return int(round(angle))


def from_angle(degrees, acc=3):
    """
    Convert a degree in angles into a normalized vector with 'acc' digits of
    accuracy after the decimal. The angle should measure counter-clockwise
    rotation from 0, which is straight up the y-axis. Note: ccw is compatible
    with pygame.transform.rotate.

    >>> from_angle(0)
    (0, -1)
    >>> from_angle(30)
    (-0.577, -1)
    >>> from_angle(45)
    (-1, -1.0)
    >>> from_angle(60)
    (-1, -0.577)
    >>> from_angle(90)
    (-1, 0.0)
    >>> from_angle(120)
    (-1, 0.577)
    >>> from_angle(135)
    (-1, 1.0)
    >>> from_angle(150)
    (-0.577, 1)
    >>> from_angle(180)
    (0, 1)
    >>> from_angle(210)
    (0.577, 1)
    >>> from_angle(225)
    (1, 1.0)
    >>> from_angle(240)
    (1, 0.577)
    >>> from_angle(270)
    (1, -0.0)
    >>> from_angle(300)
    (1, -0.577)
    >>> from_angle(315)
    (1, -1.0)
    >>> from_angle(330)
    (0.577, -1)
    >>> from_angle(360)
    (0, -1)
    >>> from_angle(1)
    (-0.017, -1)
    >>> from_angle(-1)
    (0.017, -1)
    >>> from_angle(0.001)
    (0, -1)
    >>> from_angle(0.01)
    (0, -1)
    >>> from_angle(179.999)
    (0, 1)
    >>> from_angle(390)
    (-0.577, -1)
    >>> from_angle(-390)
    (0.577, -1)
    """
    degrees = 360 - degrees
    degrees = degrees % 360
    tan = round(math.tan(math.radians(degrees)), acc)
    #print(tan)
    if tan == 0:
        # 0 means an angle near 0 or 180 degrees.
        degrees = round(degrees)
        if not degrees % 360:
            return 0, -1
        else:
            return 0, 1
    if abs(tan) >= 1:
        # |x|>|y| so normalize on |x|
        y = round(-1/tan, acc)
        if degrees >= 0 and degrees <= 180:
            return 1, y
        else:
            return -1, -y
    else:
        # |y|>|x| so normalize on |y|
        if degrees >= 0 and degrees <= 180:
            x = abs(tan)
        else:
            x = -abs(tan)
        if degrees >= 90 and degrees <= 270:
            return x, 1
        else:
            return x, -1

if __name__ == "__main__":
    import doctest
    doctest.testmod()
