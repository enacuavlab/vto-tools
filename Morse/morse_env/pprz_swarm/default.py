#! /usr/bin/env morseexec
""" Basic MORSE simulation scene for <test_pprz> environment
Feel free to edit this template as you like!
"""

from morse.builder import *
# The list of the main methods to manipulate your components
# is here: http://www.openrobots.org/morse/doc/stable/user/builder_overview.html

#uav_list = {}
#
#def new_quad(name, ac_id):
#    r = Quadrotor()
#    r.translate(0.0, 0.0, 0.0)
#    r.rotate(0.0, 0.0, 0.0)
#    # Add a motion controller
#    m = Teleport()
#    r.append(m)
#    m.add_stream('pprzlink', ac_id=ac_id)
#    uav_list[name] = r
#
#new_quad('bebop2_210', 210)

r1 = Quadrotor()
r1.translate(0.0, 0.0, 0.0)
r1.rotate(0.0, 0.0, 0.0)
m1 = Teleport()
r1.append(m1)
m1.add_stream('pprzlink', ac_id=211)

r2 = Quadrotor()
r2.translate(0.0, 0.0, 0.0)
r2.rotate(0.0, 0.0, 0.0)
m2 = Teleport()
r2.append(m2)
m2.add_stream('pprzlink', ac_id=212)

env = Environment('voliere.blend', fastmode = False)
env.fullscreen(False)
#env.set_camera_location([-20.0, 0.0, 10.0])
#env.set_camera_rotation([1.1,  0., -1.57])
#env.set_horizon_color(color=(0.05, 0.22, 0.4))
#env.show_framerate()

