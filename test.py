import util

vel=0
err=100
maxaccel=20
damp=2

while abs(err) > damp or vel != 0:
    accel = util.calculate_acceleration(err, vel, maxaccel, damp)
    vel += accel
    err -= vel

print(err)
