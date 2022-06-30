import numpy as np
from numpy import linalg
import math
import matplotlib.pyplot as plt
import pyclipper
from shapely.geometry import Point, Polygon
from datetime import datetime
from itertools import compress

import pdb

"""##Building Code"""

class Building():
    def __init__(self,vertices): # Buildings(obstacles) are defined by coordinates of their vertices.
        self.vertices = np.array(vertices)
        self.panels = np.array([])
        self.nop  = None           # Number of Panels
        self.K = None              # Coefficient Matrix
        self.K_inv = None
        self.gammas = {}           # Vortex Strenghts
        #self.solution = np.array([])

    def inflate(self,safetyfac = 1.1, rad = 1e-4): 
        rad = rad * safetyfac
        scale = 1e6
        pco = pyclipper.PyclipperOffset() 
        pco.AddPath( (self.vertices[:,:2] * scale).astype(int).tolist() , pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)

        inflated  =  np.array ( pco.Execute( rad*scale )[0] ) / scale
        height = self.vertices[0,2]
        points = np.hstack(( inflated , np.ones((inflated.shape[0],1)) *height ))
        Xavg = np.mean(points[:,0:1])
        Yavg = np.mean(points[:,1:2])
        angles = np.arctan2( ( Yavg*np.ones(len(points[:,1])) - points[:,1] ) , ( Xavg*np.ones(len(points[:,0])) - points[:,0] ) )  
        sorted_angles = sorted(zip(angles, points), reverse = True)
        points_sorted = np.vstack([x for y, x in sorted_angles])
        self.vertices = points_sorted

    def panelize(self,size):
        # Divides obstacle edges into smaller line segments, called panels.
        for index,vertice in enumerate(self.vertices):
            xyz1 = self.vertices[index]                                 # Coordinates of the first vertice
            xyz2 = self.vertices[ (index+1) % self.vertices.shape[0] ]  # Coordinates of the next vertice
            s    = ( (xyz1[0]-xyz2[0])**2 +(xyz1[1]-xyz2[1])**2)**0.5   # Edge Length
            n    = math.ceil(s/size)                                    # Number of panels given desired panel size, rounded up

            if n == 1:
                raise ValueError('Size too large. Please give a smaller size value.')
            if self.panels.size == 0:
                self.panels = np.linspace(xyz1,xyz2,n)[1:]
            else:
            # Divide the edge into "n" equal segments:
                self.panels = np.vstack((self.panels,np.linspace(xyz1,xyz2,n)[1:]))
        
         
    def calculate_coef_matrix(self, method = 'Vortex'):
# Calculates coefficient matrix.
        if method == 'Vortex':
            self.nop = self.panels.shape[0]    # Number of Panels
            self.pcp = np.zeros((self.nop,2))  # Controlpoints: at 3/4 of panel
            self.vp  = np.zeros((self.nop,2))  # Vortex point: at 1/4 of panel
            self.pl  = np.zeros((self.nop,1))  # Panel Length
            self.pb  = np.zeros((self.nop,1))  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

            XYZ2 = self.panels                      # Coordinates of end point of panel 
            XYZ1 = np.roll(self.panels,1,axis=0)    # Coordinates of the next end point of panel

            self.pcp  = XYZ2 + (XYZ1-XYZ2)*0.75 # Controlpoints point at 3/4 of panel. #self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]                                                   
            self.vp   = XYZ2 + (XYZ1-XYZ2)*0.25 # Vortex point at 1/4 of panel.
            self.pb   = np.arctan2( ( XYZ2[:,1] - XYZ1[:,1] ) , ( XYZ2[:,0] - XYZ1[:,0] ) )  + np.pi/2
            self.K = np.zeros((self.nop,self.nop))
            for m in range(self.nop ):
                for n in range(self.nop ):
                    self.K[m,n] = ( 1 / (2*np.pi)  
                                    * ( (self.pcp[m][1]-self.vp[n][1] ) * np.cos(self.pb[m] ) - ( self.pcp[m][0] - self.vp[n][0] ) * np.sin(self.pb[m] ) ) 
                                    / ( (self.pcp[m][0]-self.vp[n][0] )**2 + (self.pcp[m][1] - self.vp[n][1] )**2 ) )
            # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
            self.K_inv = np.linalg.inv(self.K)
        elif method == 'Source':
            self.nop = self.panels.shape[0]    # Number of Panels
            self.pcp = np.zeros((self.nop,2))  # Controlpoints: at 3/4 of panel
            self.vp  = np.zeros((self.nop,2))  # Vortex point: at 1/4 of panel
            self.pl  = np.zeros((self.nop,1))  # Panel Length
            self.pb  = np.zeros((self.nop,1))  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

            XYZ2 = self.panels                      # Coordinates of end point of panel 
            XYZ1 = np.roll(self.panels,1,axis=0)    # Coordinates of the next end point of panel
        
        # From Katz & Plotkin App D, Program 3
            self.pcp  = XYZ1 + (XYZ2-XYZ1)*0.5 # Controlpoints point at 1/2 of panel. #self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]                                                   
            self.pb   = np.arctan2( ( XYZ2[:,1] - XYZ1[:,1] ) , ( XYZ2[:,0] - XYZ1[:,0] ) )  # Panel Angle
            self.K = np.zeros((self.nop,self.nop))
            self.K = np.zeros((self.nop,self.nop))
            for m in range(self.nop ):
                for n in range(self.nop ):
                    # Convert collocation point to local panel coordinates:
                    xt  = self.pcp[m][0] - XYZ1[n][0]
                    yt  = self.pcp[m][1] - XYZ1[n][1]
                    x2t = XYZ2[n][0] - XYZ1[n][0]
                    y2t = XYZ2[n][1] - XYZ1[n][1]
                    x   =  xt * np.cos(self.pb[n]) + yt  * np.sin(self.pb[n])
                    y   = -xt * np.sin(self.pb[n]) + yt  * np.cos(self.pb[n])
                    x2  = x2t * np.cos(self.pb[n]) + y2t * np.sin(self.pb[n])
                    y2  = 0
                    # Find R1,R2,TH1,TH2:
                    R1  = (     x**2 +      y**2)**0.5
                    R2  = ((x-x2)**2 + (y-y2)**2)**0.5
                    TH1 = np.arctan2( ( y    ) , ( x    ) )
                    TH2 = np.arctan2( ( y-y2 ) , ( x-x2 ) )

                    #R1 = ((XYZ1[m][0]-self.pcp[n][0])**2 + (XYZ1[m][1]-self.pcp[n][1])**2 )**0.5
                    #R2 = ((XYZ2[m][0]-self.pcp[n][0])**2 + (XYZ2[m][1]-self.pcp[n][1])**2 )**0.5
                    #T1 = np.arctan2((XYZ1[m][1]-self.pcp[n][1]),(XYZ1[m][0]-self.pcp[n][0])) + self.pb[m]
                    #T2 = np.arctan2((XYZ2[m][1]-self.pcp[n][1]),(XYZ2[m][0]-self.pcp[n][0])) + self.pb[m]

                    # Compute Velocity in Local Ref. Frame
                    if m == n:
                        # Diagonal elements: Effect of a panel on itself.
                        up = 0
                        vp = 0.5
                    else:
                        # Off-diagonal elements: Effect of other panels on a panel.
                        up = np.log(R1/R2)/(2*np.pi)
                        vp = (TH2-TH1)/(2*np.pi)
                    # Return to global ref. frame
                    U =  up * np.cos(-self.pb[n]) + vp * np.sin(-self.pb[n]) 
                    V = -up * np.sin(-self.pb[n]) + vp * np.cos(-self.pb[n])
                    # Coefficient Matrix:
                    #self.K[m,n] = -U * np.sin(self.pb[m]) + V * np.cos(self.pb[m])
                    self.K[m,n] = -up * np.sin(self.pb[n]-self.pb[m]) + vp * np.cos(self.pb[n]-self.pb[m])
            # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
            self.K_inv = np.linalg.inv(self.K)  
        elif method == 'Hybrid':
            self.nop = self.panels.shape[0]    # Number of Panels
            self.pcp = np.zeros((self.nop,2))  # Controlpoints: at 3/4 of panel
            self.vp  = np.zeros((self.nop,2))  # Vortex point: at 1/4 of panel
            self.pl  = np.zeros((self.nop,1))  # Panel Length
            self.pb  = np.zeros((self.nop,1))  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

            XYZ2 = self.panels                      # Coordinates of end point of panel 
            XYZ1 = np.roll(self.panels,1,axis=0)    # Coordinates of the next end point of panel

            self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]                                                   
            self.pl   = ( ( XYZ1[:,0]-XYZ2[:,0] )**2 +( XYZ1[:,1]-XYZ2[:,1] )**2 )**0.5 
            self.pb   = np.arctan2( ( XYZ2[:,1] - XYZ1[:,1] ) , ( XYZ2[:,0] - XYZ1[:,0] ) ) + (np.pi/2)
            self.K = np.zeros((self.nop,self.nop))
            self.K = np.zeros((self.nop,self.nop))
    # Calculates coefficient matrix.
            self.K = np.zeros((self.nop,self.nop))
            for m in range(self.nop ):
                for n in range(self.nop ):
                    if m == n:
                        # Diagonal elements: Effect of a panel on itself.
                        self.K[m,n] = -2/(np.pi*self.pl[n])
                    else:
                        # Off-diagonal elements: Effect of other panels on a panel.
                        self.K[m,n] = ( self.pl[n] / (2*np.pi)  
                                        * ( (self.pcp[m][1]-self.pcp[n][1] ) * np.cos(self.pb[m] ) - ( self.pcp[m][0] - self.pcp[n][0] ) * np.sin(self.pb[m] ) ) 
                                        / ( (self.pcp[m][0]-self.pcp[n][0] )**2 + (self.pcp[m][1] - self.pcp[n][1] )**2 ) )
            # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
            self.K_inv = np.linalg.inv(self.K)         
    '''
    def vel_sink_calc(self,vehicle):
    # Calculates velocity induced on each panel by a sink element.
        vel_sink = np.zeros((self.nop,2)) 
        for m in range(self.nop):
            vel_sink[m,0] = (-vehicle.sink_strength*(self.pcp[m][0]-vehicle.goal[0]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))
            vel_sink[m,1] = (-vehicle.sink_strength*(self.pcp[m][1]-vehicle.goal[1]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))
        self.vel_sink[vehicle.ID] =  vel_sink   

    def vel_source_calc(self,vehicle,othervehicles):
    # Calculates velocity induced on each panel by source elements.
        vel_source = np.zeros((self.nop,2)) 
        for othervehicle in othervehicles:
            for m in range(self.nop):
                    vel_source[m,0] += (othervehicle.source_strength*(self.pcp[m][0]-othervehicle.position[0]))/(2*np.pi*((self.pcp[m][0]-othervehicle.position[0])**2+(self.pcp[m][1]-othervehicle.position[1])**2))
                    vel_source[m,1] += (othervehicle.source_strength*(self.pcp[m][1]-othervehicle.position[1]))/(2*np.pi*((self.pcp[m][0]-othervehicle.position[0])**2+(self.pcp[m][1]-othervehicle.position[1])**2))
        self.vel_source[vehicle.ID] =  vel_source 
        
    '''
    
    def gamma_calc(self,vehicle,othervehicles,arenamap,method = 'Vortex'):
    # Calculates unknown vortex strengths by solving panel method eq.  
        #cycletime = datetime.now()

        vel_sink   = np.zeros((self.nop,2)) 
        vel_source = np.zeros((self.nop,2))
        vel_source_imag = np.zeros((self.nop,2)) 
        RHS        = np.zeros((self.nop,1))
        #currenttime = datetime.now()
        #print( " New array generation: "  + str(currenttime - cycletime ) )

        if method == 'Vortex':
            vel_sink[:,0] = (-vehicle.sink_strength*(self.pcp[:,0]-vehicle.goal[0]))/(2*np.pi*((self.pcp[:,0]-vehicle.goal[0])**2+(self.pcp[:,1]-vehicle.goal[1])**2))
            vel_sink[:,1] = (-vehicle.sink_strength*(self.pcp[:,1]-vehicle.goal[1]))/(2*np.pi*((self.pcp[:,0]-vehicle.goal[0])**2+(self.pcp[:,1]-vehicle.goal[1])**2))

            vel_source_imag[:,0] = (vehicle.imag_source_strength*(self.pcp[:,0]-vehicle._position_enu[0]))/(2*np.pi*((self.pcp[:,0]-vehicle._position_enu[0])**2+(self.pcp[:,1]-vehicle._position_enu[1])**2))
            vel_source_imag[:,1] = (vehicle.imag_source_strength*(self.pcp[:,1]-vehicle._position_enu[1]))/(2*np.pi*((self.pcp[:,0]-vehicle._position_enu[0])**2+(self.pcp[:,1]-vehicle._position_enu[1])**2))

            for i,othervehicle in enumerate(othervehicles) :
                    
                    vel_source[:,0] += (othervehicle.source_strength*(self.pcp[:,0]-othervehicle._position_enu[0]))/(2*np.pi*((self.pcp[:,0]-othervehicle._position_enu[0])**2+(self.pcp[:,1]-othervehicle._position_enu[1])**2))
                    vel_source[:,1] += (othervehicle.source_strength*(self.pcp[:,1]-othervehicle._position_enu[1]))/(2*np.pi*((self.pcp[:,0]-othervehicle._position_enu[0])**2+(self.pcp[:,1]-othervehicle._position_enu[1])**2))


            RHS[:,0]  = -vehicle.V_inf[0]  * np.cos(self.pb[:])  \
                                    -vehicle.V_inf[1]  * np.sin(self.pb[:])  \
                                    -vel_sink[:,0]     * np.cos(self.pb[:])  \
                                    -vel_sink[:,1]     * np.sin(self.pb[:])  \
                                    -vel_source[:,0]   * np.cos(self.pb[:])  \
                                    -vel_source[:,1]   * np.sin(self.pb[:])  \
                                    -vel_source_imag[:,0]  * np.cos(self.pb[:])  \
                                    -vel_source_imag[:,1]  * np.sin(self.pb[:])  \
                                    -arenamap.windT * arenamap.wind[0] * np.cos(self.pb[:]) \
                                    -arenamap.windT * arenamap.wind[1] * np.sin(self.pb[:]) +vehicle.safety
                                    #-2                * np.cos(self.pb[m])  \
                                    #-0                * np.sin(self.pb[m])#\

            #for m in range(self.nop):
                # Calculates velocity induced on each panel by a sink element.
                
                

                #currenttime = datetime.now()
                #print( " Calculations for panel " + str(m) + " sink:"   + str(currenttime - cycletime ) )
                # Calculates velocity induced on each panel by source elements.
                
                # Right Hand Side of panel method eq.
                    # Normal comp. of freestream +  Normal comp. of velocity induced by sink + Normal comp. of velocity induced by sources
                #currenttime = datetime.now()
                #print( " Calculations for panel " + str(m) + " sources:"   + str(currenttime - cycletime ) )


                

                #currenttime = datetime.now()
                #print( " Calculations for panel " + str(m) + " rhs:"   + str(currenttime - cycletime ) )
            self.gammas[vehicle.ID] = np.matmul(self.K_inv,RHS)
        elif method == 'Source':
            for m in range(self.nop):
                # Calculates velocity induced on each panel by a sink element.
                vel_sink[m,0] = (-vehicle.sink_strength*(self.pcp[m][0]-vehicle.goal[0]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))
                vel_sink[m,1] = (-vehicle.sink_strength*(self.pcp[m][1]-vehicle.goal[1]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))

                # Calculates velocity induced on each panel by source elements.
                for othervehicle in othervehicles:
                    vel_source[m,0] += (othervehicle.source_strength*(self.pcp[m][0]-othervehicle._position_enu[0]))/(2*np.pi*((self.pcp[m][0]-othervehicle._position_enu[0])**2+(self.pcp[m][1]-othervehicle._position_enu[1])**2))
                    vel_source[m,1] += (othervehicle.source_strength*(self.pcp[m][1]-othervehicle._position_enu[1]))/(2*np.pi*((self.pcp[m][0]-othervehicle._position_enu[0])**2+(self.pcp[m][1]-othervehicle._position_enu[1])**2))
                # Right Hand Side of panel method eq.
                    # Normal comp. of freestream +  Normal comp. of velocity induced by sink + Normal comp. of velocity induced by sources
                RHS[m]  = -vehicle.V_inf[0] * np.cos(self.pb[m] + (np.pi/2))  \
                                    -vehicle.V_inf[1] * np.sin(self.pb[m] + (np.pi/2))  \
                                    -vel_sink[m,0]    * np.cos(self.pb[m] + (np.pi/2))  \
                                    -vel_sink[m,1]    * np.sin(self.pb[m] + (np.pi/2))  \
                                    -vel_source[m,0]  * np.cos(self.pb[m] + (np.pi/2))  \
                                    -vel_source[m,1]  * np.sin(self.pb[m] + (np.pi/2))  \
                                    -arenamap.windT * arenamap.wind[0] * np.cos(self.pb[m] + (np.pi/2)) \
                                    -arenamap.windT * arenamap.wind[1] * np.sin(self.pb[m] + (np.pi/2)) + vehicle.safety
            self.gammas[vehicle.ID] = np.matmul(self.K_inv,RHS)      
            
        #currenttime = datetime.now()
        #print( " Calculations for panel  gammas:"   + str(currenttime - cycletime ) )