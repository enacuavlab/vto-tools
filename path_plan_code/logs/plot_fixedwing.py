import os, sys
import numpy as np
import time
import matplotlib.pyplot as plt
import argparse

from scipy.spatial.transform import Rotation




import pdb

sys.path.insert(0, '../')
from path_plan_w_panel import ArenaMap

def read(filename):
    with np.load(filename, 'rb') as log:
        timestamp= log['timestamps']
        controls = log['controls']
        states = log['states']
    return timestamp, states, controls 

def plot_wind_states(timestamp, states, controls):

    # fig_0 = plt.figure(figsize=(5,5) )
    # for _v in range(states.shape[0]):
    #     time = timestamp[_v]
    #     pos_e = states[_v,0,:]
    #     pos_n = states[_v,1,:]
    #     pos_u = states[_v,2,:]

    #     # plt.scatter(pos_e, pos_n)
    #     plt.grid()
    #     plt.plot(pos_e, pos_n)

    fig_1 = plt.figure(figsize=(10,5) )
    for _v in range(states.shape[0]):
        time = timestamp[_v]
        vel_e = states[_v,3,:]
        vel_n = states[_v,4,:]
        vel_u = states[_v,5,:]

        plt.grid()
        plt.plot(time,vel_e, label='Vel_E')
        plt.plot(time,vel_n, label='Vel_N')
        # plt.plot(time,vel_u)

    fig_2 = plt.figure(figsize=(10,5) )
    for _v in range(states.shape[0]):
        time = timestamp[_v]
        vel_e  = controls[_v,6,:]
        vel_we = controls[_v,7,:]
        vel_n  = controls[_v,8,:]
        vel_wn = controls[_v,9,:]

        plt.grid()
        plt.plot(time,vel_e , label='Vel_E')
        plt.plot(time,vel_n , label='Vel_N')
        plt.plot(time,vel_we, label='Wind_Vel_E')
        plt.plot(time,vel_wn, label='Wind_Vel_N')
        plt.legend()

    plt.show()

def plot_trajectory(timestamp, states, controls):

    # fig_0 = plt.figure(figsize=(5,5) )
    # for _v in range(states.shape[0]):
    #     time = timestamp[_v]
    #     pos_e = states[_v,0,:]
    #     pos_n = states[_v,1,:]
    #     pos_u = states[_v,2,:]

    #     # plt.scatter(pos_e, pos_n)
    #     plt.grid()
    #     plt.plot(pos_e, pos_n)

    fig_1 = plt.figure(figsize=(10,5) )
    for _v in range(states.shape[0]):
        time = timestamp[_v]
        vel_e = states[_v,3,:]
        vel_n = states[_v,4,:]
        vel_u = states[_v,5,:]

        plt.grid()
        plt.plot(time,vel_e)
        plt.plot(time,vel_n)
        plt.plot(time,vel_u)

    # fig_1_1 = plt.figure(figsize=(10,5) )
    # for _v in range(states.shape[0]):
    #     time = timestamp[_v]
    #     phi  = states[_v,9,:]
    #     theta= states[_v,10,:]
    #     psi  = states[_v,11,:]


    #     plt.grid()
    #     plt.plot(time,phi, label='Phi')
    #     plt.plot(time,theta, label='Theta')
    #     plt.plot(time,psi, label='Psi')


    fig_1_2 = plt.figure(figsize=(10,5) )
    # pdb.set_trace()
    euler = np.zeros((states.shape[0],3,states.shape[2]))
    for _v in range(1):
    # for _v in range(states.shape[0]):
        time = timestamp[_v]
        qx = states[_v,6,:]
        qy = states[_v,7,:]
        qz = states[_v,8,:]
        qw = states[_v,9,:]

        plt.plot(time,qx, label='qx')
        plt.plot(time,qy, label='qy')
        plt.plot(time,qz, label='qz')
        plt.plot(time,qw, label='qw')
        plt.grid(); plt.legend()
        i=0
        for _qx,_qy,_qz,_qw in zip(qx,qy,qz,qw):
            quat = np.array([_qx,_qy,_qz,_qw])
            rot = Rotation.from_quat(quat)
            euler[_v,:,i] = rot.as_euler('xyz', degrees=True)
            i+=1

    fig_1_3 = plt.figure(figsize=(10,5) )
    plt.plot(time,euler[0,0,:], label='phi')
    plt.plot(time,euler[0,1,:], label='theta')
    plt.plot(time,euler[0,2,:], label='psi')
    plt.grid(); plt.legend()


    fig_1_4 = plt.figure(figsize=(10,5) )
    plt.plot(euler[0,2,:],euler[0,0,:], label='phi')
    plt.plot(euler[0,2,:],euler[0,1,:], label='theta')
    plt.xlabel('psi')
    plt.grid(); plt.legend()


    fig_2 = plt.figure(figsize=(10,5) )
    for _v in range(states.shape[0]):
        time = timestamp[_v]
        vel_e = controls[_v,0,:]
        vel_n = controls[_v,1,:]
        vel_u = controls[_v,2,:]

        plt.grid()
        plt.plot(time,vel_e)
        plt.plot(time,vel_n)
        plt.plot(time,vel_u)

    fig_2_5 = plt.figure(figsize=(10,5) )
    for _v in range(states.shape[0]):
        time = timestamp[_v]
        pos_e = states[_v,0,:]
        pos_n = states[_v,1,:]
        pos_u = states[_v,2,:]

        plt.plot(time, pos_e)
        plt.plot(time, pos_n)
        plt.plot(time, pos_u)

    fig_3 = plt.figure(figsize=(10,5) )
    for _v in range(states.shape[0]):
        time = timestamp[_v]
        vel_e = controls[_v,3,:]
        vel_n = controls[_v,4,:]
        vel_u = controls[_v,5,:]

        plt.grid()
        plt.plot(time,vel_e)
        plt.plot(time,vel_n)
        plt.plot(time,vel_u)

    Arena = ArenaMap(version = 2)
    Arena.Inflate(radius = 0.2)
    ArenaR = ArenaMap(version = 2)

    fig4 = plt.figure(figsize=(5,5))
    minx = 0 # min(min(building.vertices[:,0].tolist()),minx)
    maxx = 60 # max(max(building.vertices[:,0].tolist()),maxx)
    miny = 0 # min(min(building.vertices[:,1].tolist()),miny)
    maxy = 60 # max(max(building.vertices[:,1].tolist()),maxy)
    #plt.figure(figsize=(20,10))
    plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
    for building in Arena.buildings:
        plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
        plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
    for buildingR in ArenaR.buildings:
        plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
        plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
    for _v in range(states.shape[0]):
        time = timestamp[_v]
        pos_e = states[_v,0,:]
        pos_n = states[_v,1,:]
        pos_u = states[_v,2,:]

        # plt.scatter(pos_e, pos_n)
        plt.plot(pos_e, pos_n)

    # plt.plot(Vehicle1.path[:,0],Vehicle1.path[:,1],'r',linewidth = 2)
    # plt.plot(Vehicle1.path[0,0],Vehicle1.path[0,1],'o')
    # plt.plot(Vehicle1.goal[0],Vehicle1.goal[1],'x')
    # plt.plot(Vehicle2.path[:,0],Vehicle2.path[:,1],'b',linewidth = 2)
    # plt.plot(Vehicle2.path[0,0],Vehicle2.path[0,1],'o')
    # plt.plot(Vehicle2.goal[0],Vehicle2.goal[1],'x') 
    #Steamline_Calculator(Vehicle_list,0,Arena,resolution = 30)
    plt.xlim([minx, maxx])
    plt.ylim([miny, maxy])
    # plt.show()
    plt.show()


def plot_wind_diff(timestamp, states, controls, timestamp2, states2, controls2, arena_version=102):
    Arena = ArenaMap(version = arena_version)
    Arena.Inflate(radius = 0.2)
    ArenaR = ArenaMap(version = arena_version)
    minx = -275 # min(min(building.vertices[:,0].tolist()),minx)
    maxx = 275 # max(max(building.vertices[:,0].tolist()),maxx)
    miny = -150 # min(min(building.vertices[:,1].tolist()),miny)
    maxy = 375 # max(max(building.vertices[:,1].tolist()),maxy)
    colorlist = ['r','b','g']
    labellist1 = ['_nolegend_','Simulation','_nolegend_']
    labellist2 = ['_nolegend_','Experiment','_nolegend_']
    labellist3 = ['_nolegend_','Velocity Vector','_nolegend_']
    plt.figure(figsize=(5,5))
    plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
    for building in Arena.buildings:
        plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
        plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
    for buildingR in ArenaR.buildings:
        plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
        plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
    for _v in range(states.shape[0]):
        time = timestamp[_v]

        pos_e  = states[_v,0,:]
        pos_n  = states[_v,1,:]

        pos_e2 = states2[_v,0,:]
        pos_n2 = states2[_v,1,:]

        vel_e = states[_v,3,:]
        vel_n = states[_v,4,:]

        cont_vel_e = controls[_v,0,:]
        cont_vel_n = controls[_v,1,:]

        X = pos_e[1::100]
        Y = pos_n[1::100]
        U = cont_vel_e[1::100]
        V = cont_vel_n[1::100]

        plt.plot(pos_e2, pos_n2, color=colorlist[_v], linewidth = 0.5, linestyle ='--',alpha = 0.5, label=labellist1[_v])
        plt.plot(pos_e,  pos_n,  color=colorlist[1], linewidth = 0.5, label=labellist2[_v])
        # plt.quiver(X, Y, U, V, color='k', linewidth = 1, units='xy', scale=1, width = 0.075, headwidth = 2, headlength = 3, headaxislength = 3, alpha = 1, label=labellist3[_v])
        plt.legend(loc = 'lower left',fontsize='small')
    plt.xlabel('East-direction --> (m)')
    plt.ylabel('North-direction --> (m)')
    plt.xlim([minx, maxx])
    plt.ylim([miny, maxy])
    plt.show()

def plot_wind(timestamp, states, controls, arena_version=102):
    Arena = ArenaMap(version = arena_version)
    Arena.Inflate(radius = 5.)
    ArenaR = ArenaMap(version = arena_version)
    minx = -275 # min(min(building.vertices[:,0].tolist()),minx)
    maxx = 275 # max(max(building.vertices[:,0].tolist()),maxx)
    miny = -150 # min(min(building.vertices[:,1].tolist()),miny)
    maxy = 375 # max(max(building.vertices[:,1].tolist()),maxy)
    colorlist = ['r','b','g']
    labellist1 = ['_nolegend_','Simulation','_nolegend_']
    labellist2 = ['_nolegend_','Experiment','_nolegend_']
    labellist3 = ['_nolegend_','Velocity Vector','_nolegend_']
    plt.figure(figsize=(5,5))
    plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
    for building in Arena.buildings:
        plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
        plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
    for buildingR in ArenaR.buildings:
        plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
        plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
    for _v in range(states.shape[0]):
        time = timestamp[_v]

        pos_e  = states[_v,0,:]
        pos_n  = states[_v,1,:]

        vel_e = states[_v,3,:]
        vel_n = states[_v,4,:]

        cont_vel_e = controls[_v,0,:]
        cont_vel_n = controls[_v,1,:]

        X = pos_e[1::100]
        Y = pos_n[1::100]
        U = cont_vel_e[1::100]
        V = cont_vel_n[1::100]

        # plt.plot(pos_e2, pos_n2, color=colorlist[_v], linewidth = 0.5, linestyle ='--',alpha = 0.5, label=labellist1[_v])
        plt.plot(pos_e,  pos_n,  '-*', color=colorlist[1], linewidth = 0.5, label=labellist2[_v])
        # plt.quiver(X, Y, U, V, color='k', linewidth = 1, units='xy', scale=1, width = 0.075, headwidth = 2, headlength = 3, headaxislength = 3, alpha = 1, label=labellist3[_v])
        plt.legend(loc = 'lower left',fontsize='small')
    plt.xlabel('East-direction --> (m)')
    plt.ylabel('North-direction --> (m)')
    plt.xlim([minx, maxx])
    plt.ylim([miny, maxy])
    plt.show()



def main():
    parser = argparse.ArgumentParser(description='Flight Log Plotter')
    parser.add_argument('--file',            default=None,     type=str,       help='Flight log filename', metavar='')
    parser.add_argument('--arena',           default=201,      type=int,       help='Arena Version', metavar='')
    parser.add_argument('--f1',              default=None,     type=str,       help='Flight log filename', metavar='')
    parser.add_argument('--f2',              default=None,     type=str,       help='Flight log filename', metavar='')
    parser.add_argument('--save',            default=False,    type=bool,      help='Whether to save the plots to a file or not)', metavar='')
    
    ARGS = parser.parse_args()

    # filename = 'save-voliere-flight-02.28.2022_17.48.34.npy'
    
    # timestamp, states, controls = read(ARGS.file)

    # plot_trajectory(timestamp, states, controls)
    if ARGS.f2 == None:
        timestamp, states, controls = read(ARGS.f1)
        plot_wind(timestamp, states, controls, arena_version=ARGS.arena)
    else:
        timestamp, states, controls = read(ARGS.f1)
        timestamp2, states2, controls2 = read(ARGS.f2)
        plot_wind_diff(timestamp, states, controls, timestamp2, states2, controls2, arena_version=ARGS.arena)
    # plot_wind_states(timestamp, states, controls)

  


if __name__ == '__main__':
    main()
