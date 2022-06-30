#!/usr/bin/env python3
from __future__ import print_function
from mission_control_path_plan import *
import sys
from os import path, getenv

from math import radians, atan2
import time
import numpy as np

from logger import Logger

# # if PAPARAZZI_SRC or PAPARAZZI_HOME not set, then assume the tree containing this
# # file is a reasonable substitute
PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
PPRZ_SRC = getenv("PAPARAZZI_SRC", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_SRC + "/sw/lib/python")
sys.path.append(PPRZ_HOME + "/var/lib/python") # pprzlink
import settings
import pprz_connect
from settings_xml_parse import PaparazziACSettings

from pprzlink.ivy import IvyMessagesInterface

from pprzlink.message import PprzMessage

from vector_fields import TrajectoryEllipse, ParametricTrajectory, spheric_geo_fence, repel, Controller

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mission Control")
    parser.add_argument("-on", "--running-on", help="Where is the code running-on", dest='running_on', default='ground')
    parser.add_argument("-f", "--file", help="path to messages.xml file", default='pprzlink/messages.xml')
    parser.add_argument("-c", "--class", help="message class", dest='msg_class', default='telemetry')
    parser.add_argument("-d", "--device", help="device name", dest='dev', default='/dev/ttyUSB0') #ttyTHS1
    parser.add_argument("-b", "--baudrate", help="baudrate", dest='baud', default=230400, type=int)
    parser.add_argument("-id", "--ac_id", help="aircraft id (receiver)", dest='ac_id', default=23, type=int)
    parser.add_argument("--interface_id", help="interface id (sender)", dest='id', default=0, type=int)
    # parser.add_argument("-ti", "--target_id", dest='target_id', default=2, type=int, help="Target aircraft ID")
    # parser.add_argument("-ri", "--repel_id", dest='repel_id', default=2, type=int, help="Repellant aircraft ID")
    # parser.add_argument("-bi", "--base_id", dest='base_id', default=10, type=int, help="Base aircraft ID")
    args = parser.parse_args()

    if args.running_on == 'ground' :
        interface  = IvyMessagesInterface("PprzConnect")

    if args.running_on == "serial" :
        from pprzlink.serial import SerialMessagesInterface
        interface = SerialMessagesInterface(None, device=args.dev,
                                               baudrate=args.baud, msg_class=args.msg_class, interface_id=args.id, verbose=False)


    #### Initialize the logger #################################
    logger = Logger(logging_freq_hz=int(10),
                    num_drones=3 )

    # mission_plan_dict={ 'morph' :{'start':None, 'duration':3, 'finalized':False},
    #                     'takeoff' :{'start':None, 'duration':15, 'finalized':False},
    #                     # 'circle'  :{'start':None, 'duration':15, 'finalized':False},
    #                     # 'parametric_circle'  :{'start':None, 'duration':15, 'finalized':False},
    #                     # 'nav2land':{'start':None, 'duration':5,  'finalized':False},
    #                     # 'land'    :{'start':None, 'duration':10, 'finalized':False} } #,
    #                     # 'kill'    :{'start':None, 'duration':10, 'finalized':False} }
    #                     }
    # mission_plan_dict={ 'parametric_circle'  :{'start':None, 'duration':15, 'finalized':False} }

    # Automatic Exploration of own Robustness
    # mission_plan_dict={#'takeoff' :{'start':None, 'duration':15, 'finalized':False},
    #                     'morph' :{'start':None, 'duration':3, 'finalized':False},
    #                     'M1_fault' :{'start':None, 'duration':5, 'finalized':False},
    #                     'Explore_robustness' :{'start':None, 'duration':600, 'finalized':False},
    #                     'Resurrect1' :{'start':None, 'duration':10, 'finalized':False},
    #                     # 'M1_fault' :{'start':None, 'duration':10, 'finalized':False},
    #                     }

    mission_plan_dict={ 'follow_fixed_wing_path_plan'  :{'start':None, 'duration':600, 'finalized':False} }

    # mission_plan_dict={ 'parametric_circle'  :{'start':None, 'duration':15, 'finalized':False} }

    # mission_plan_dict={ 'debug_mode'  :{'start':None, 'duration':15, 'finalized':False} }

    # mission_plan_dict={ 'Explore_robustness_hover_step'  :{'start':None, 'duration':600, 'finalized':False} }


    # mission_plan_dict={ 'Explore_robustness_circle_step'  :{'start':None, 'duration':600, 'finalized':False} }

    # arena_version = 102
    # vehicle_id_list =   [1]
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [1.5] # Imaginary source_strength
    # vehicle_goal_list = [([3.0, 3, 1.4], 5, 0.00)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[1.4,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[-3.0, 3, 1.4]]
    # vehicle_next_goal_list = [[1.5, 3, 1.4], [-1.5, 3, 1.4]]
    # # vehicle_next_goal_list = [[3., 2, 1.4], [-3., 2, 1.4], [-3., 1, 1.4], [3., 1, 1.4], [3., 0, 1.4], [-3., 0, 1.4], [-3., -1, 1.4], [3., -1, 1.4], [3., -2, 1.4],[-3., -2, 1.4],[-3., -3, 1.4],[3., -3, 1.4], [3., 2, 1.4], [-3., 2, 1.4], [-3., 1, 1.4], [3., 1, 1.4], [3., 0, 1.4], [-3., 0, 1.4], [-3., -1, 1.4], [3., -1, 1.4],  ]
    # # vehicle_next_goal_list = [[3., -3, 1.4], [-3., -3, 1.4], [-3., 2, 1.4], [2., 2, 1.4],[2., -2, 1.4], [-2., -2, 1.4], [-2., 1, 1.4], [1., 1, 1.4], [1., -1, 1.4], [-1., -1, 1.4], [-1., 0, 1.4], [0., 0, 1.4] ]
    # goal_index = 0


    # # Case 12.2 : Arena 6 : 3 Vehicles
    # arena_version = 6
    # vehicle_name_list =   ['V1', 'V2', 'V3']
    # vehicle_source_list = [0.65, 0.75, 0.65] # Source_strength
    # vehicle_imaginary_source_list = [0.75, 0.75, 0.75] # Imaginary source_strength
    # vehicle_goal_list = [([2.5, -3.5, 0.5], 5, 0.00), ([-0.5, 3., 0.5], 5, 0.00), ([3., 3., 0.5], 5, 0.00) ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[0.5,0,0,0],[0.5,0,0,0], [0.5,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[-2., 3., 0.5],[-2., -3, 0.5], [-3, 0, 0.5]]

    # # MUret Sim trial
    # arena_version = 61
    # vehicle_id_list =  [18]
    # vehicle_source_list = [0.65] # Source_strength
    # vehicle_imaginary_source_list = [0.95] # Imaginary source_strength
    # vehicle_goal_list = [([2.5, -3.5, 10.], 5, 0.00),  ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[10.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[-2., 3., 10.0]]
    # vehicle_next_goal_list = [ [ [2.5, -3.5, 10.], [-3., 0., 10.],[3.0, 3.5, 10.], [2.5, -3.5, 10.],  [-3., 0., 10.], [4., 0., 10.] ]  ]
    # # vehicle_next_goal_list = [ [ [4., 0., 10.] ,[2.5, -3.5, 10.], [3.0, 3.5, 10.], [2.5, -3.5, 10.],[-3., 0., 10.],  [-3., 0., 10.] ]  ]
    # # vehicle_next_goal_list = [ [ [-3., 0., 10.], [3.0, 3.5, 10.], [2.5, -3.5, 10.],  [-3., 0., 10.], [-0.5, 3., 10.]]  ]


    # vehicle_id_list =   [1]
    # vehicle_source_list = [0.65] # Source_strength
    # vehicle_imaginary_source_list = [0.95] # Imaginary source_strength
    # vehicle_goal_list = [([3.0, 3.5, 0.5], 5, 0.00),  ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[0.5,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[-3., 0., 0.5]]

    # vehicle_id_list =   [4, 1]
    # vehicle_source_list = [0.65, 0.65] # Source_strength
    # vehicle_imaginary_source_list = [0.75, 0.75] # Imaginary source_strength
    # vehicle_goal_list = [([2.5, -3.5, 0.5], 5, 0.00), ([3.0, 3.5, 0.5], 5, 0.00),  ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[0.5,0,0,0] , [0.5,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[-2., 3., 0.5], [-3., 0., 0.5]]

    # # Centered Hexa Building to see the repulsion of buildings plus the corrected velocity following.
    # arena_version = 201 # 102 #202 
    # vehicle_id_list =   [18]
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [0.75] # Imaginary source_strength
    # vehicle_goal_list = [([3.0, 1, 1.4], 5, 0.00)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[1.4,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[-3.0, 1, 1.4]]

    # Muret Single Vehicle Star Shape Flight
    # arena_version = 8
    # vehicle_id_list =   [18]
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [1.0] # Imaginary source_strength
    # vehicle_goal_list = [([40., 50., 10.], 5, 0.0)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[10.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[0., 0., 10.]]
    # vehicle_next_goal_list = [ [[40., 50., 10.], [40, 5, 10.], [10, 45, 10], [55, 25, 10], [0, 0, 10]]  ]


    # # Case 15
    arena_version = 8
    vehicle_id_list =   [18, 4]
    vehicle_source_list = [1.5, 1.5] # Source_strength
    vehicle_imaginary_source_list = [1.0, 1.0] # Imaginary source_strength
    vehicle_goal_list = [([40., 50., 10.], 5, 0.0), ([30., 30., 10.], 5, 0.0)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    vehicle_goto_goal_list =[ [10.,0,0,0], [10.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    vehicle_pos_list = [[0., 0., 10.], [0., 50., 10.]]
    vehicle_next_goal_list = [ [[40., 50., 10.],[55., 20., 10.],[20., 35., 10.] ],     [[30., 30., 10.], [25., 5., 10.],[0., 50., 10.]]   ]


    # # Case 17 Cancelled
    # arena_version = 8
    # vehicle_id_list =   [18, 4]
    # vehicle_source_list = [0.95, 0.95] # Source_strength
    # vehicle_imaginary_source_list = [1.0, 1.0] # Imaginary source_strength
    # vehicle_goal_list = [([55., 20., 10.], 5, 0.0), ([15., 27., 10.], 5, 0.0)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[ [10.,0,0,0], [10.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[20., 35., 10.], [38., 45., 10.]]
    # vehicle_next_goal_list = [ [[55., 20., 10.]], [[15., 27., 10.]]   ]


# Vehicle1 = Vehicle("V1",0,1.0)            # Vehicle ID, Source_strength
# Vehicle2 = Vehicle("V2",0,1.0)
# Vehicle3 = Vehicle("V3",0,1.0)
# Vehicle4 = Vehicle("V4",0,1.0)
# Vehicle5 = Vehicle("V5",0,1.0)

# Vehicle_list = [Vehicle1,Vehicle2, Vehicle3, Vehicle4, Vehicle5]

# Vehicle1.Set_Goal([-200, 300, 50], 5, 0)       # goal,goal_strength 30, safety 0.001 for vortex method
# Vehicle2.Set_Goal([ 210, 110, 50], 5, 0)
# Vehicle3.Set_Goal([-200, 100, 50], 5, 0)
# Vehicle4.Set_Goal([-50 , 300, 50], 5, 0)
# Vehicle5.Set_Goal([ 100, -50, 50], 5, 0)

# Vehicle1.Go_to_Goal(20,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
# Vehicle2.Go_to_Goal(20,0,0,0)
# Vehicle3.Go_to_Goal(20,0,0,0)
# Vehicle4.Go_to_Goal(20,0,0,0)
# Vehicle5.Go_to_Goal(20,0,0,0)

# Vehicle1.Set_Position([ 200,-150, 50])
# Vehicle2.Set_Position([-200, 300, 50])
# Vehicle3.Set_Position([ 210, 110, 50])
# Vehicle4.Set_Position([-200, 100, 50])
# Vehicle5.Set_Position([-50 , 300, 50])

    # Real Muret Flight
    # arena_version = 12
    # vehicle_id_list =   [27]
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [2.0] # Imaginary source_strength
    # vehicle_goal_list = [([-200., 300., 250.], 5, 0.0)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[250.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[200., -150., 250.]]
    # vehicle_next_goal_list = [ [[-200., 300., 250.], [250., 90., 250.], [-200., 100., 250.], [-50., 300., 250.], [100., -50., 250.], ]  ]


    # arena_version = 13
    # vehicle_id_list =   [27]
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [2.0] # Imaginary source_strength
    # vehicle_goal_list = [([-200., 100., 250.], 5, 0.0)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[250.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[200., -150., 250.]]
    # vehicle_next_goal_list = [ [[-200., 100., 250.], [150., 0., 250.], [-200., 50., 250.], [-50., 100., 250.], [100., -50., 250.], ]  ]
 
    arena_version = 15
    vehicle_id_list =   [120]
    vehicle_source_list = [0.95] # Source_strength
    vehicle_imaginary_source_list = [1.5] # Imaginary source_strength
    vehicle_goal_list = [([-200., 100., 250.], 5, 0.0)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    vehicle_goto_goal_list =[[250.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    vehicle_pos_list = [[200., -150., 250.]]
    vehicle_next_goal_list = [ [[-200., 100., 250.], [150., 0., 250.], [-200., -50., 250.], [-10., 120., 250.], [100., -50., 250.], ]  ]

 
    # arena_version = 16
    # vehicle_id_list =   [120]
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [2.0] # Imaginary source_strength
    # vehicle_goal_list = [([-200., 300., 250.], 5, 0.0)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[250.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[200., -150., 250.]]
    # vehicle_next_goal_list = [ [[-200., 300., 250.], [210., 50., 250.], [-200., 100., 250.], [100., 250., 250.], [100., -50., 250.], ]  ]



    # Muret Fixed-Wing Flight
    # arena_version = 8
    # vehicle_id_list =   [14]
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [2.0] # Imaginary source_strength
    # vehicle_goal_list = [([-70., 320., 250.], 5, 0.0)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[250.,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[0., 0., 250.]]
    # vehicle_next_goal_list = [ [[-70., 320., 250.], [-70., 320., 250.], [-70., 320., 250.], [-70., 320., 250.], ]  ]
    # vehicle_next_goal_list = [ [[350., 350., 250.], [0, 0, 250.], [350, -350, 250], [0, 0, 250], ]  ]


    vehicle_parameter_dict={}

    if args.running_on == 'ground' :
        try:
            mc = MissionControl(interface=interface)
            mc.assign(mission_plan_dict)
            mc.assign_vehicle_properties()
            mc.create_Arena(arena_version=arena_version, radius = 5.0, panel_size=1., force_init=True)
            mc.assign_path_plan_properties(vehicle_id_list, vehicle_source_list, vehicle_imaginary_source_list, vehicle_goal_list, vehicle_goto_goal_list, vehicle_next_goal_list)
            # import pdb
            # pdb.set_trace()

            time.sleep(1.5)

            experiment_start_time = time.time()
            while True:
                t0=time.time()
                # mc.run_every_vehicle(velocity_limit=0.5, method='None')
                mc.run_every_vehicle(velocity_limit=1.5, flight_height=10., method='None') # direct - projection
                for _id in mc._vehicle_id_list:
                    _index = mc._vehicle_id_list.index(_id)
                    rc = mc.vehicles[_index]
                    V_des = mc.flow_vels[_index].copy()
                    logger.log(drone=_index,
                               timestamp=time.time()-experiment_start_time,
                               state= np.hstack([rc._position_enu, rc._velocity_enu, rc._quat, rc._euler,  np.zeros(7)]),#obs[str(j)]["state"],
                               control=np.hstack([rc.velocity_desired, V_des, rc.velocity_corrected, np.zeros(3)]),
                               sim=False
                               # control=np.hstack([TARGET_VEL[j, wp_counters[j], 0:3], np.zeros(9)])
                               )
                exe_duration = time.time()-t0
                # time.sleep(max(0., 0.0999-exe_duration))
                time.sleep(max(0., 0.0999-exe_duration))
                # print(1./(time.time()-t0) , 'Hz' )

        except (KeyboardInterrupt, SystemExit):
            logger.save(flight_type='fixed_wing_outdoor')
            mission_end_plan_dict={'Resurrect7' :{'start':None, 'duration':10, 'finalized':False}, 'safe2land'  :{'start':None, 'duration':15, 'finalized':False} }
            mc.assign(mission_end_plan_dict)  # mc.assign_vehicle_properties()
            time.sleep(0.5)
            for i in range(10):
                mc.run_every_vehicle()
                time.sleep(0.5)
            print('Shutting down...')
            # mc.set_nav_mode()
            mc.shutdown()
            time.sleep(0.6)
            exit()


if __name__ == '__main__':
    main()
