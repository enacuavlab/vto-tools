#! /usr/bin/env morseexec
""" Basic MORSE simulation scene for <test_pprz> environment
Feel free to edit this template as you like!
"""

from morse.builder import *

robot = Quadrotor()

d2r = 3.14159 / 180.

# The list of the main methods to manipulate your components
# is here: http://www.openrobots.org/morse/doc/stable/user/builder_overview.html
robot.translate(0.0, 0.0, 0.0)
robot.rotate(0.0, 0.0, 0.0)

# Add a motion controller
motion = Teleport()
robot.append(motion)
#motion.add_stream('pprzlink', ac_id='natnet2ivy.py', msg_name='GROUND_REF')
motion.add_stream('pprzlink', ac_id=112)
#motion.add_stream('pprzlink')
#motion.add_stream('pprzlink', ac_id=101) (if you need to specify the aircraft ID)

env = Environment('voliere.blend', fastmode = False)
env.fullscreen(False)
env.set_camera_location([-2.0, -9.0, 8.0])
env.set_camera_rotation([45. * d2r,  0., -10. * d2r])
#env.set_horizon_color(color=(0.05, 0.22, 0.4))
#env.show_framerate()

