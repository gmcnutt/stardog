def calculate_acceleration(err, vel, maxval, damp=1):
    """
    'err' is the difference in position.
    'vel' is the current velocity.
    'maxval' is the upper bound on acceleration/deceleration.
    'damp' is a fudge factor to reduce oscillations when near the target.

    >>> calculate_acceleration(100, 1, 10)
    10
    >>> calculate_acceleration(0, 10, 10)
    -10
    >>> calculate_acceleration(0, 8, 10)
    -2
    """
    #
    # If not moving yet apply max acceleration to get us to the halfway point.
    #
    dbg = 'err={} vel={} '.format(err, vel)
    if not vel:
        if abs(err) < damp:
            return 0
        halfway = err / 2
        if abs(halfway) < maxval:
            return halfway
        elif halfway > 0:
            return maxval
        else:
            return -maxval
    
    #
    # Now that we're moving figure out how much distance it will take to
    # stop. Subtract this from the error. If the result is >0 then accelerate
    # some more toward the halfway point. If the result is <=0 then we've
    # overshot and need to apply maximum deceleration.
    #
    rem = err - vel - vel
    halfway = rem / 2
    dbg += ': rem={} hlf={} '.format(rem, halfway)
    if abs(halfway) < maxval:
        accel = halfway
    elif halfway > 0:
        accel = maxval
    else:
        accel = -maxval
    dbg += '-> {}'.format(accel)
    print(dbg)
    return accel

if __name__ == "__main__":
    import doctest
    doctest.testmod()
