from math import radians
from time import sleep
import numpy as np
from numpy import linalg as la
import queue

import time

class Controller:
    def __init__(self,L=1e-1,beta=1e-2,k1=1e-3,k2=1e-3,k3=1e-3,ktheta=0.5,s=1.5):
        self.L    = L
        self.beta = beta
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.ktheta = ktheta
        self.s = s


class ParametricTrajectory:
    def __init__(self, XYZ_off=np.array([0.,0.,2.]), XYZ_center=np.array([1.1, 1.1, -0.2]),
                 XYZ_delta=np.array([0., np.pi/2, 0.]), XYZ_w=np.array([1,1,1]), alpha=np.pi/4, controller=Controller()):
        self.XYZ_off = XYZ_off
        self.XYZ_center = XYZ_center
        self.XYZ_delta = XYZ_delta
        self.XYZ_w = XYZ_w
        self.alpha = alpha
        self.ctr = controller

    def get_vector_field(self,x,y,z,w):
        cx,cy,cz = self.XYZ_center
        wx,wy,wz = self.XYZ_w
        deltax,deltay,deltaz = self.XYZ_delta
        xo,yo,zo = self.XYZ_off
        alpha = self.alpha

        wb = w*self.ctr.beta
        L = self.ctr.L
        beta = self.ctr.beta
        k1 = self.ctr.k1
        k2 = self.ctr.k2
        k3 = self.ctr.k3
        s = self.ctr.s

        #f
        nrf1 = cx*np.cos(wx*wb + deltax)
        nrf2 = cy*np.cos(wy*wb + deltay)
        f3 = cz*np.cos(wz*wb + deltaz) + zo

        nrf1d = -wx*cx*np.sin(wx*wb + deltax)
        nrf2d = -wy*cy*np.sin(wy*wb + deltay)
        f3d = -wz*cz*np.sin(wz*wb + deltaz)

        nrf1dd = -wx*wx*cx*np.cos(wx*wb + deltax)
        nrf2dd = -wy*wy*cy*np.cos(wy*wb + deltay)
        f3dd = -wz*wz*cz*np.cos(wz*wb + deltaz)

        f1 = np.cos(alpha)*nrf1 - np.sin(alpha)*nrf2 + xo
        f2 = np.sin(alpha)*nrf1 + np.cos(alpha)*nrf2 + yo

        f1d = np.cos(alpha)*nrf1d - np.sin(alpha)*nrf2d
        f2d = np.sin(alpha)*nrf1d + np.cos(alpha)*nrf2d

        f1dd = np.cos(alpha)*nrf1dd - np.sin(alpha)*nrf2dd
        f2dd = np.sin(alpha)*nrf1dd + np.cos(alpha)*nrf2dd

        #phi
        phi1 = L*(x - f1)
        phi2 = L*(y - f2)
        phi3 = L*(z - f3)
        # print(f'Phi 1: {phi1:.4f}, Phi 2:{phi2:.4f}, Phi 3:{phi3:.4f}')

        #Chi, J
        Chi = L*np.array([[-f1d*L*L*beta -k1*phi1],
                          [-f2d*L*L*beta -k2*phi2],
                          [-f3d*L*L*beta -k3*phi3],
                          [-L*L + beta*(k1*phi1*f1d + k2*phi2*f2d + k3*phi3*f3d)]])

        # j44 = beta*beta*(k1*(phi1*f1dd-L*f1d*f1d) + k2*(phi2*f2dd-L*f2d*f2d) + k3*(phi3*f3dd-L*f3d*f3d))
        # J = L*np.array([[-k1*L,        0,      0, -(beta*L)*(beta*L*f1dd-k1*f1d)],
                       # [     0,    -k2*L,      0, -(beta*L)*(beta*L*f2dd-k2*f2d)],
                       # [     0,      0,    -k3*L, -(beta*L)*(beta*L*f3dd-k3*f3d)],
                       # [beta*L*k1*f1d, beta*L*k2*f2d, beta*L*k3*f3d,         j44]])

        #G, Fp, Gp
        # G = np.array([[1,0,0,0],
                      # [0,1,0,0],
                      # [0,0,0,0],
                      # [0,0,0,0]])

        # Fp = np.array([[0, -1, 0, 0],
                       # [1,  0, 0, 0]])

        # Gp = np.array([[0, -1, 0, 0],
                       # [1,  0, 0, 0],
                       # [0,  0, 0, 0],
                       # [0,  0, 0, 0]])

    #     h = np.array([[np.cos(theta)],[np.sin(theta)]])
    #     ht = h.transpose()

        # Chit = Chi.transpose()
        # Chinorm = np.sqrt(Chi.transpose().dot(Chi))[0][0]
        # Chih = Chi / Chinorm

    #     u_theta = (-(1/(Chit.dot(G).dot(Chi))*Chit.dot(Gp).dot(np.eye(4) - Chih.dot(Chih.transpose())).dot(J).dot(X_dot)) - ktheta*ht.dot(Fp).dot(Chi) / np.sqrt(Chit.dot(G).dot(Chi)))[0][0]

        u_x = Chi[0][0]*s / np.sqrt(Chi[0][0]*Chi[0][0] + Chi[1][0]*Chi[1][0])
        u_y = Chi[1][0]*s / np.sqrt(Chi[0][0]*Chi[0][0] + Chi[1][0]*Chi[1][0])
        u_z = Chi[2][0]*s / np.sqrt(Chi[0][0]*Chi[0][0] + Chi[1][0]*Chi[1][0])
        u_w = Chi[3][0]*s / np.sqrt(Chi[0][0]*Chi[0][0] + Chi[1][0]*Chi[1][0])
        
        return np.array([u_x, u_y, u_z]), np.array([u_w])


class TrajectoryEllipse:
    def __init__(self, XYoff, rot, a, b ,s=1, ke=1):
        self.XYoff = XYoff
        self.a, self.b = a, b
        self.s,self.ke = s, ke
        self.rot = rot
        self.traj_points = np.zeros((2, 200))
        self.mapgrad_X = []
        self.mapgrad_Y = []
        self.mapgrad_U = []
        self.mapgrad_V = []
        
    def get_vector_field(self, X, Y, Z, s=None, ke=None):
        if s==None : s=self.s
        if ke==None : ke=self.ke
        Xel = (X-self.XYoff[0])*np.cos(self.rot)- (Y-self.XYoff[1])*np.sin(self.rot)
        Yel = (X-self.XYoff[0])*np.sin(self.rot)+ (Y-self.XYoff[1])*np.cos(self.rot)
        nx = 2*Xel*np.cos(self.rot)/self.a**2 + 2*Yel*np.sin(self.rot)/self.b**2
        ny = -2*Xel*np.sin(self.rot)/self.a**2+ 2*Yel*np.cos(self.rot)/self.b**2

        tx = s*ny
        ty = -s*nx

        e = (Xel/self.a)**2 + (Yel/self.b)**2 - 1

        U = tx -ke*e*nx
        V = ty -ke*e*ny

        norm = np.sqrt(U**2 + V**2)

        U = U/norm
        V = V/norm
        return np.array([U, V, 2])

    def draw_trajectory(self, delta=np.pi/2):
        t = np.linspace(-np.pi,np.pi,300)
        x = self.a*np.sin(t)
        y = self.b*np.cos(t)
        return x,y


#         i = 0
#         for t in self.float_range(0, 1, 0.005):
#             self.traj_points[:, i] = self.param_point(t)
#             i = i + 1

#     def param_point(self, t):
#         angle = 2*np.pi*t
#         return self.XYoff \
#                 + np.array([self.a*np.cos(angle)*np.cos(-self.rot) - \
#                 self.b*np.sin(angle)*np.sin(-self.rot), \
#                 self.a*np.cos(angle)*np.sin(-self.rot) + \
#                 self.b*np.sin(angle)*np.cos(-self.rot)])

    def vector_field(self, XYoff, area, s, ke):
        self.mapgrad_X, self.mapgrad_Y = np.mgrid[XYoff[0]-0.5*np.sqrt(area):\
                XYoff[0]+0.5*np.sqrt(area):30j, \
                XYoff[1]-0.5*np.sqrt(area):\
                XYoff[1]+0.5*np.sqrt(area):30j]

        Xel = (self.mapgrad_X-self.XYoff[0])*np.cos(self.rot)- (self.mapgrad_Y-self.XYoff[1])*np.sin(self.rot)
        Yel = (self.mapgrad_X-self.XYoff[0])*np.sin(self.rot)+ (self.mapgrad_Y-self.XYoff[1])*np.cos(self.rot)
        nx = 2*Xel*np.cos(self.rot)/self.a**2 + 2*Yel*np.sin(self.rot)/self.b**2
        ny = -2*Xel*np.sin(self.rot)/self.a**2+ 2*Yel*np.cos(self.rot)/self.b**2

        tx = s*ny
        ty = -s*nx

        e = (Xel/self.a)**2 + (Yel/self.b)**2 - 1

        self.mapgrad_U = tx -ke*e*nx
        self.mapgrad_V = ty -ke*e*ny

        norm = np.sqrt(self.mapgrad_U**2 + self.mapgrad_V**2)

        self.mapgrad_U = self.mapgrad_U/norm
        self.mapgrad_V = self.mapgrad_V/norm

def spheric_geo_fence(x,y,z, x_source=0., y_source=0., z_source=0., strength=-2):
#     if strength >0 : raise print('Are you sure ?')
    u = strength / (2 * np.pi) * (x - x_source) * ((x - x_source)**2 + (y - y_source)**2 + (z - z_source)**2)
    v = strength / (2 * np.pi) * (y - y_source) * ((x - x_source)**2 + (y - y_source)**2 + (z - z_source)**2)
    w = strength / (2 * np.pi) * (z - z_source) * ((x - x_source)**2 + (y - y_source)**2 + (z - z_source)**2)
    return np.array([u,v,w])


def repel(x,y,z, x_source=0., y_source=0., z_source=0., strength=2):
#     if strength >0 : raise print('Are you sure ?')
    u = strength / (2 * np.pi) * (x - x_source) / ((x - x_source)**2 + (y - y_source)**2 + (z - z_source)**2)
    v = strength / (2 * np.pi) * (y - y_source) / ((x - x_source)**2 + (y - y_source)**2 + (z - z_source)**2)
    w = strength / (2 * np.pi) * (z - z_source) / ((x - x_source)**2 + (y - y_source)**2 + (z - z_source)**2)
    return np.array([u,v,w])