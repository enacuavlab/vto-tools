import numpy as np
from components import Commands, FlightStatus, Circle

from vector_fields import TrajectoryEllipse, ParametricTrajectory, spheric_geo_fence, repel, Controller


class Vehicle(object):
    def __init__(self, ac_id, interface):
        self._initialized = False
        self._take_off = False
        self._morphed = False
        self._morph_state = 0.
        self._fault = False
        self._land = False
        self._state = 0
        self._ac_id = ac_id
        self._interface = interface
        self._position_initial = np.zeros(3) # Initial Position for safely landing after Ctrl+C
        self._flight_height = 3.
        self._initial_heading = 0.
        self._des_heading = 0.
        self._next_goal_list = [] # empty list
        self._position = np.zeros(3) # Position
        self._velocity = np.zeros(3) # Velocity
        self._position_enu = np.zeros(3) # Position
        self._velocity_enu = np.zeros(3) # Velocity
        self._course = 0.
        self._speed = 0. # For fixed-wing, 2d norm of projected ground speed from GPS
        self._quat = np.zeros(4) # Quaternion
        self._euler = np.zeros(3) # phi-theta-psi Angles ! 
        self._w = np.zeros(3)
        self.gvf_parameter = 0
        self.sm = None  # settings manager
        self.timeout = 0
        self.battery_voltage = 12.0 # As a start... FIXME
        self.cmd = Commands(self._ac_id, self._interface)
        self.fs = FlightStatus(self._ac_id)


        self.ka = 1.6 #acceleration setpoint coeff
        self.circle_vel = 0.6 #m/s
        self.belief_map = {}

        self.t               = 0
        # self.position        = np.zeros(3)
        # self.velocity        = np.zeros(3)
        self.goal            = None
        self.goal_index      = 0
        self.source_strength = 0.
        self.imag_source_strength = 0.
        self.gamma           = 0
        self.altitude_mask   = None
        self.ID              = ac_id
        self.path            = []
        # self.state           = 0
        self.distance_to_destination = None
        self.velocitygain    = 1/50 # 1/300 or less for vortex method, 1/50 for hybrid
        self.velocity_desired = np.zeros(3)
        self.velocity_corrected = np.zeros(3)
        self.vel_err = np.zeros(3)
        self.err_last = np.zeros(3)
        self.distance_goal_reached = 2.0 # m This should chance for indoor and outdoor and for fixed wing and rotarywing !!!! FIX ME
        self.distance_goal_reached = 20.0 # FIX ME !!!

    # def Set_Position(self,pos):
    #     self.position = np.array(pos)
    #     self.path     = np.array(pos)
    #     if self.goal != None:
    #         self.distance_to_destination = np.linalg.norm(np.array(self.goal)-np.array(self.position))
    #         if self.distance_to_destination < 0.2:
    #             self.state = 1

    # def Set_Velocity(self,vel):
    #     self.velocity = vel

    def Set_Desired_Velocity(self,vel, method='direct'):
        ''' NED(U) velocity coming from flow vels of Panel method '''
        # Update the goal reached information now:
        if self.goal != None:
            self.distance_to_destination = np.linalg.norm(np.array(self.goal)-np.array(self._position_enu))
            # print('vehicle.Set_Desired_Velocity : ', self._position_enu, self.goal, 'Dist:', self.distance_to_destination)

            if self.distance_to_destination < self.distance_goal_reached:
                print('========== POINT REACHED ============')
                print('========== POINT REACHED ============')
                print('========== POINT REACHED ============')
                print('========== POINT REACHED ============')
                self.state = 1
                self.Select_Next_Goal()

        self.velocity_desired = vel
        self.correct_vel(method=method)


    def correct_vel(self, method='direct'):

        if method == 'projection':
            #Projection Method
            wind = self.velocity - self.velocity_desired
            self.vel_err = self.vel_err - (wind - np.dot(wind, self.velocity_desired/np.linalg.norm(self.velocity_desired) ) * np.linalg.norm(self.velocity_desired) ) *(1./240.)
        elif method == 'direct':
            # err = self.velocity_desired - self.velocity
            # cur_vel_enu = self._velocity_enu.copy()
            # cur_vel_enu[1] = -cur_vel_enu[1]
            dt  = 1./10.
            err = self.velocity_desired - self._velocity
            d_err = (err - self.err_last)/dt
            self.err_last = err.copy()

            self.vel_err = err*dt
            # self.vel_err = (self.velocity_desired - self.velocity)
            print(f' Vel err : {self.vel_err[0]:.3f}  {self.vel_err[1]:.3f}  {self.vel_err[2]:.3f}')
        else:
            self.vel_err = np.array([0., 0., 0.])
            d_err = np.zeros(3)
            err = np.zeros(3)

        self.velocity_corrected = self.velocity_desired + err*0.0 + self.vel_err*2.5 + d_err*0.6
        self.velocity_corrected[2] = 0.
        # print(f' Wind              : {wind[0]:.3f}  {wind[1]:.3f}  {wind[2]:.3f}')
        # print(f' Projected Vel err : {self.vel_err[0]:.3f}  {self.vel_err[1]:.3f}  {self.vel_err[2]:.3f}')
        # print(f' Desired   Vel     : {self.velocity_desired[0]:.3f}  {self.velocity_desired[1]:.3f}  {self.velocity_desired[2]:.3f}')
        # print(f' Corrected Vel     : {self.velocity_corrected[0]:.3f}  {self.velocity_corrected[1]:.3f}  {self.velocity_corrected[2]:.3f}')
        # print('   ')
        # print('   ')
        # print('   ')

    def Set_Source(self, source_strength):
        self.source_strength = source_strength

    def Set_Imaginary_Source(self, source_strength):
        self.imag_source_strength = source_strength

    def Set_Goal(self,goal,goal_strength,safety):
        self.goal          = goal
        self.sink_strength = goal_strength
        self.safety = safety

    def Set_Flight_Height(self,height):
        self._flight_height = height

    def Set_Next_Goal_List(self, next_goal_list):
        self._next_goal_list = next_goal_list

    def Select_Next_Goal(self):
        self.goal_index += 1
        self.goal_index = self.goal_index%len(self._next_goal_list)
        goal = self._next_goal_list[self.goal_index]
        self.Set_Next_Goal(goal)

    def Set_Next_Goal(self,goal, goal_strength=5):
        # Putting the state back to zero
        self.state = 0
        self.goal          = goal
        # self.sink_strength = goal_strength NOT USED FOR NOW

    def Go_to_Goal(self,altitude,AoA,t_start,Vinf):
        self.altitude = altitude                                       # Cruise altitude
        self.V_inf    = np.array([Vinf*np.cos(AoA), Vinf*np.sin(AoA)]) # Freestream velocity. AoA is measured from horizontal axis, cw (+)tive
        self.t = t_start



    def __str__(self):
        conf_str = f'A/C ID {self._ac_id}'
        return conf_str

    @property
    def id(self):
        return self._ac_id

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self,val):
        self._state = val

    def assign_properties(self):
        # while self._initialized == False :
            print('Initialization :::',self._initialized)
            ex = 0 ; ey = 0 ; ealpha = 0 ; ea = 1.1 ; eb = 1.1
            print(f'We are inside assign properties for id {self._ac_id}')
            # We have the current position of the vehicle and can set it to the circle center
            self.traj = TrajectoryEllipse(np.array([self._position[0], self._position[1]]), ealpha, ea, eb)
            self._circle = Circle(radius=1.1, cx=self._position[0], cy=self._position[1], cz=self._position[2])

            self._position_initial = self._position.copy() # Just for starting point assignement
            self._initial_heading = self._euler[2] #0. # self.sm["nav_heading"].value
            print(f'Heading initialized to : {self._initial_heading}')

            self.ctr = Controller(L=1e-1,beta=1e-2,k1=1e-3,k2=1e-3,k3=1e-3,ktheta=0.5,s=0.50)
            # self.traj_parametric = ParametricTrajectory(XYZ_off=np.array([0.,0.,2.5]),
            #                                             XYZ_center=np.array([1.3, 1.3, -0.6]),
            #                                             XYZ_delta=np.array([0., np.pi/2, 0.]),
            #                                             XYZ_w=np.array([1,1,1]),
            #                                             alpha=0.,
            #                                             controller=self.ctr)
            self.traj_parametric = ParametricTrajectory(XYZ_off=np.array([0.,0.,2.5]),
                                                        XYZ_center=np.array([1.3, 1.3, 0.]),
                                                        XYZ_delta=np.array([np.pi/2., 0. , 0.]),
                                                        XYZ_w=np.array([2,1,1]),
                                                        alpha=np.pi,
                                                        controller=self.ctr)

    def get_vector_field(self,mission_task, position=None):
        V_des = np.zeros(3)
        if position is not None:
            V_des += spheric_geo_fence(position[0], position[1], position[2], x_source=0., y_source=0., z_source=0., strength=-0.07)
        else:
            V_des += spheric_geo_fence(self._position[0], self._position[1], self._position[2], x_source=0., y_source=0., z_source=0., strength=-0.07)
        for _k in self.belief_map.keys():
            # float(self.belief_map[_k]['X'])
            V_des += repel(self._position[0], self._position[1], self._position[2], 
                    x_source=float(self.belief_map[_k]['X']), 
                    y_source=float(self.belief_map[_k]['Y']), 
                    z_source=float(self.belief_map[_k]['Z']), strength=5.0)

        return V_des

    def send_acceleration(self, V_des, A_3D=False, height_2D=2.):
        err = V_des - self._velocity#[:2]
        # print(f'Velocity error {err[0]} , {err[1]}, {err[2]}')
        acc = err*self.ka
        if A_3D :
            self.cmd.accelerate(acc[0],acc[1],-acc[2], flag=1)
        else:
            self.cmd.accelerate(acc[0],acc[1],height_2D, flag=0) # Z is fixed to have a constant altitude... FIXME for 3D !
        # return acc


    def calculate_cmd(self, mission_task):

        V_des = self.get_vector_field(self.fs.task)

        def resurrect(self):
            print('Resurrection')
            if self._fault:
                for i in range(3):
                    self.sm["M1"] = 1.0
                    print('Resurrecting M1')
                    self.sm["M2"] = 1.0
                    print('Resurrecting M2')
                    self.sm["M3"] = 1.0
                    print('Resurrecting M3')
                    self.sm["M4"] = 1.0
                    print('Resurrecting M4')
                    self.sm["M5"] = 1.0
                    print('Resurrecting M5')
                    self.sm["M6"] = 1.0
                    print('Resurrecting M6')
                self._fault = False

        def calc_energy_based_errors(self):
            pos_err = self._position_initial - self._position


        def calculate_path_following_error(verbose=False):
            x = self._position[0] - self._circle.cx
            y = self._position[1] - self._circle.cy
            z = self._position[2] - self._circle.cz

            error_r = self._circle.radius - np.sqrt(x**2+y**2)
            error = np.linalg.norm([error_r, z])
            # i=0; error=np.zeros(len(error_r))
            # for er,ez in zip(error_r, z):
            #     error[i] = la.norm([er,ez])
            #     i+=1
            # if verbose :
            #     print('Mean : ',np.mean(error),'Standart deviation: ', np.std(error))
            #     print('Path following error',np.sum(error)/i)
            return error


        def spin_heading(step=0.01):
            ss = np.sign(step)
            self._des_heading = self._des_heading + step
            if ss<0 : # CCW spin
                self._des_heading = 3.14 if self._des_heading< -3.1415 else self._des_heading
            else:
                self._des_heading = -3.14 if self._des_heading>3.1415 else self._des_heading
            self.sm["nav_heading"] = self._des_heading*2**12

        def follow_circle(height_2D=3.):
            print('We are circling!!!')
            V_des = self.traj.get_vector_field(self._position[0], self._position[1], self._position[2])*self.circle_vel
            # Getting and setting the navigation heading of the vehicles
            follow_heading = False #True
            if follow_heading:
                heading_des = (1.5707963267948966-atan2(V_des[0],V_des[1]))*2**12
                # heading_cur = self.sm["nav_heading"].value
                # print(f'Nav heading error is : {heading_des-heading_cur}')
                if self.sm:
                    self.sm["nav_heading"] = heading_des

            self.send_acceleration(V_des, A_3D=False, height_2D=height_2D)

        def follow_panel_path(height_2D=2.):
            print('  ')
            print('We are following the path plan streamlines !!!')
            # V_des = self.traj.get_vector_field(self._position[0], self._position[1], self._position[2])*self.circle_vel
            # print('  ')
            # print('NED Desired   Panel Path Velocity : ',self.velocity_desired, np.linalg.norm(self.velocity_desired))
            # print('NED Corrected Panel Path Velocity : ',self.velocity_corrected, np.linalg.norm(self.velocity_corrected))
            # print('NED VelENU    Panel Path Velocity : ',self._velocity_enu, np.linalg.norm(self._velocity_enu))
            # print('NED position : ', self._position)
            # print('ENU position : ', self._position_enu)

            # Getting and setting the navigation heading of the vehicles
            follow_heading = False #True
            if follow_heading:
                heading_des = (1.5707963267948966-atan2(V_des[0],V_des[1]))*2**12
                # heading_cur = self.sm["nav_heading"].value
                # print(f'Nav heading error is : {heading_des-heading_cur}')
                if self.sm:
                    self.sm["nav_heading"] = heading_des

            self.send_acceleration(self.velocity_corrected, A_3D=False, height_2D=height_2D)


        def follow_fixed_wing_panel_path():
            # if self.sm:
            #     print('Path plan angle : ', self.sm["path_plan_roll_angle"].value )

                # self.sm["path_plan_roll_angle"] = self.sm["path_plan_roll_angle"].value - 0.1
            # print('Vel desired : ',self.velocity_desired, ' Vel actual : ', self._velocity)
            # print('Speed : ', self._speed)
            # print('Course : ', self._course) # North is zero, rotation right is positive , rotation left is negative, switching at south 3.1415...
            # calculate the desired heading from desired velocity
            # Get desired and actual 2D velocity norms
            # vel_des_norm = np.sqrt(self.velocity_desired[0]**2 + self.velocity_desired[1]**2)
            # vel_norm = np.sqrt(self._velocity[0]**2 + self._velocity[1]**2)

            def norm_ang(x):
                while x > np.pi :
                    x -= 2*np.pi
                while x < -np.pi :
                    x += 2*np.pi
                return x

            vel = self._velocity[:2]
            vel_des = self.velocity_desired[:2]
            vel_norm     = np.linalg.norm(vel)
            vel_des_norm = np.linalg.norm(vel_des)

            # vel_err = vel_des/vel_des_norm - vel/vel_norm

            vel_unit     = vel/np.linalg.norm(vel)
            vel_des_unit = vel_des/np.linalg.norm(vel_des)

            # vel_err = vel_des/vel_des_norm - vel/vel_norm

            heading = np.arctan2(vel_unit[1], vel_unit[0])
            heading_des = np.arctan2(vel_des_unit[1], vel_des_unit[0])

            heading_err = norm_ang(heading_des-heading)


            # roll_setpoint = np.arctan(heading_err * 15. / 9.81 / np.cos(0.))

            # heading err
            # omega = np.arccos((vel.dot(vel_des))/(vel_norm*vel_des_norm))
            # calculate a roll angle to reduce the heading error 
            theta = 0.
            roll_setpoint = np.arctan(heading_err * self._speed / 9.81 / np.cos(theta)) * 0.4
            # print('Roll setpoint : ', np.degrees(roll_setpoint), )
            print(f' Heaading : {np.degrees(heading):.2f} Desired : {np.degrees(heading_des):.2f}   Err : {np.degrees(heading_err):.2f}, Roll setpoint :  {np.degrees(roll_setpoint):.2f}')

            self.sm["path_plan_roll_angle"] = np.clip(np.degrees(roll_setpoint),-55., 55.)


        def fail_motor(motor='M1', step=1.):
            if not self._fault:
                # for i in range(10):
                cur_eff = self.sm[motor].value
                print(f'Cur_eff : {cur_eff}')
                # pdb.set_trace()
                if cur_eff!=None:
                    self.sm[motor] = np.clip( (cur_eff - step) ,0. , 1.)
                    self._fault = True if self.sm[motor].value == 0.0 else False

        def recover_motor(self, motor='M1', step=0.1):
            if self._fault:
                # for i in range(10):
                self.sm[motor] = np.clip( (self.sm[motor].value + step) ,0. , 1.)
                self._fault = False if self.sm[motor].value == 1.0 else True

        def morph(gamma=1.0):
            gamma = np.clip(gamma, -1., 1.)
            self.sm["morph_common"] = gamma
            self._morph_state = gamma

        def morph_if_needed(pos_threshold=2.5, ang_threshold=1.57, safe_morph=1.0, in_circle=False):
            if in_circle:
                norm_pos_err = calculate_path_following_error()
                print('Calculating pos error in circle', norm_pos_err)
            else:
                pos_err = self._position_initial - self._position
                norm_pos_err = np.linalg.norm(pos_err)

            heading_err = self._initial_heading - self._euler[2]
            print(f'Heading  err : {heading_err}')
                # print(f'Heading  cur : {self._euler[2]}')
                # print(f'Position err : {norm_pos_err}')

            if norm_pos_err > pos_threshold or abs(heading_err) > ang_threshold :
                print('!!! Auto-Morph !!!')
                # self._morph_direction = 
                morph_cmd = safe_morph
                self.sm["morph_common"] = morph_cmd
                self._morph_state = morph_cmd

        def sequence(mtime, motor,step_var,gamma, start_time,morph_phase=5., fail_phase=15, recovery_phase=5):
            if start_time<= mtime < start_time+morph_phase:
                morph(gamma=gamma)
            if start_time+morph_phase<= mtime < start_time+morph_phase+fail_phase:
                print('Motor Failed !')
                fail_motor(motor=motor, step=step_var)
            if start_time+morph_phase+fail_phase<= mtime < start_time+morph_phase+fail_phase+recovery_phase:
                print('Recover the Motor')
                recover_motor(self, motor=motor, step=step_var)
            print(f' Gamma : {gamma:.2f}')
            time = start_time+morph_phase+fail_phase+recovery_phase
            # finished = 1 if mtime >= time
            return time #, finished


        if self.battery_voltage < 9.5:#13.8:
            print('Battery Voltage : ', self.battery_voltage)
            # morph(gamma=1.0)
            mission_task = 'land'

        if mission_task == 'morph':
            print('Morphing')
            if not self._morphed:
                morph_cmd = 1.0
                self.sm["morph_common"] = morph_cmd
                self._morph_state = morph_cmd
                self._morphed = True
                # self.sm["morph_cmd_1"] = morph_cmd
                # self.sm["morph_cmd_2"] = -morph_cmd
                # morph_period, morph_dance

        if mission_task == 'debug_mode':
            print(f'Debug Mode')
            pos_err = self._position_initial - self._position

            # norm_pos_err = np.linalg.norm(pos_err)
            # print(f'Position err : {norm_pos_err}')
            spin_heading(step=0.01)

            heading_err = self._des_heading - self._euler[2]

            # print(f'Heading  err : {heading_err}')
            # print(f'Heading  cur : {self._euler[2]}')

            # print(f'W  cur : {self._euler[0]:.3f}  ,  {self._euler[1]:.3f}  ,  {self._euler[2]:.3f}')
            # print(f' QUAT ::: {self._quat[0]:.2f}  ,  {self._quat[1]:.2f}  ,  {self._quat[2]:.2f}  ,  {self._quat[3]:.2f}')

        if mission_task == 'follow_path_plan':
            follow_panel_path(height_2D=self._flight_height)


        if mission_task == 'follow_fixed_wing_path_plan':
            follow_fixed_wing_panel_path()


        if mission_task == 'Explore_robustness':
            print(f'Exploring Robustness at : {self._morph_state}')

            self._morph_state = np.clip((self._morph_state - 0.005), -1.0, 1.0)  # 0.005 @ 10Hz gives 40s for Y-X-Y transition
            self.sm["morph_common"] = self._morph_state

            # morph_if_needed(pos_threshold=1.5, ang_threshold=1.0, safe_morph=0.6)
            morph_if_needed(pos_threshold=2.5, ang_threshold=1.57, safe_morph=1.0, in_circle=False)


        if mission_task == 'Explore_robustness_circle_step':
            mtime = self.fs.get_current_task_time()
            step_var=1.0
            motor="M6"
            if 0<= mtime < 2.:
                morph(gamma=1.0)
                motor_list=['M1','M2','M3','M4','M5','M6']
                for _M in motor_list:
                    self.sm[_M] = 1.0
            
            start_time = sequence(mtime, motor, step_var, gamma=1.0,  start_time=5.,         morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=0.8,  start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=0.6,  start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=0.3,  start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=0.2,  start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=0.1,  start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=0.0,  start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.1, start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.2, start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.3, start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.6, start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.8, start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)
            start_time = sequence(mtime, motor, step_var, gamma=-1.0, start_time=start_time, morph_phase=1., fail_phase=15., recovery_phase=0.)

            follow_circle(height_2D=4.)

            morph_if_needed(pos_threshold=2.5, ang_threshold=1.57, safe_morph=1.0, in_circle=True)



        if mission_task == 'Explore_robustness_hover_step':
            mtime = self.fs.get_current_task_time()
            step_var=1.0
            motor="M6"
            if 0<= mtime < 2.:
                morph(gamma=1.0)
                motor_list=['M1','M2','M3','M4','M5','M6']
                for _M in motor_list:
                    self.sm[_M] = 1.0

            start_time = sequence(mtime, motor, step_var, gamma=1.0,  start_time=2.,         morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=0.8,  start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=0.6,  start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=0.3,  start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=0.2,  start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=0.1,  start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=0.0,  start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.1, start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.2, start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.3, start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.6, start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=-0.8, start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)
            start_time = sequence(mtime, motor, step_var, gamma=-1.0, start_time=start_time, morph_phase=5., fail_phase=15., recovery_phase=8.)


            morph_if_needed(pos_threshold=2.6, ang_threshold=1.57)
            # morph_if_needed(pos_threshold=2.5, ang_threshold=1.57, safe_morph=1.0, in_circle=False)

            # if 2<= mtime < 12.:
            #     print('Motor Failed !')
            #     fail_motor(motor=motor, step=step_var)
            # # if 6<= mtime < 30.:
            # #     print('Morphing towards 0 !')
            # #     morph(gamma=(self._morph_state - 0.005) )
            # if 12<= mtime < 14.:
            #     print('Recover the Motor')
            #     recover_motor(self, motor=motor, step=step_var)

            # if 14<= mtime < 16.:
            #     morph(gamma=0.6)
            # if 16<= mtime < 26.:
            #     print('Motor Failed !')
            #     fail_motor(motor=motor, step=step_var)
            # if 26<= mtime < 28.:
            #     print('Recover the Motor')
            #     recover_motor(self, motor=motor, step=step_var)

            # if 28<= mtime < 30.:
            #     morph(gamma=0.3)
            # if 30<= mtime < 40.:
            #     print('Motor Failed !')
            #     fail_motor(motor=motor, step=step_var)
            # if 40<= mtime < 42.:
            #     print('Recover the Motor')
            #     recover_motor(self, motor=motor, step=step_var)

            # if 42<= mtime < 44.:
            #     morph(gamma=0.2)
            # if 44<= mtime < 54.:
            #     print('Motor Failed !')
            #     fail_motor(motor=motor, step=step_var)
            # if 54<= mtime < 56.:
            #     print('Recover the Motor')
            #     recover_motor(self, motor=motor, step=step_var)

            # if 56<= mtime < 58.:
            #     morph(gamma=0.1)
            # if 58<= mtime < 68.:
            #     print('Motor Failed !')
            #     fail_motor(motor=motor, step=step_var)
            # if 68<= mtime < 70.:
            #     print('Recover the Motor')
            #     recover_motor(self, motor=motor, step=step_var)

            # if 70<= mtime < 72.:
            #     morph(gamma=0.0)
            # if 72<= mtime < 82.:
            #     print('Motor Failed !')
            #     fail_motor(motor=motor, step=step_var)
            # if 82<= mtime < 84.:
            #     print('Recover the Motor')
            #     recover_motor(self, motor=motor, step=step_var)



            # Periodically do the below things :

            # spin_heading(step=0.03)
            # morph_if_needed(pos_threshold=2.5, ang_threshold=1.57)



        if mission_task == 'M1_fault':
            print('Fault on M1')
            fail_motor('M1')

        if mission_task == 'M2_fault':
            print('Fault on M2')
            if not self._fault:
                for i in range(2):
                    self.sm["M2"] = 0.0
                self._fault=True

        if mission_task == 'M3_fault':
            print('Fault on M3')
            if not self._fault:
                for i in range(2):
                    self.sm["M3"] = 0.0
                self._fault=True

        if mission_task == 'M4_fault':
            print('Fault on M4')
            if not self._fault:
                for i in range(2):
                    self.sm["M4"] = 0.0
                self._fault=True

        if mission_task == 'M5_fault':
            print('Fault on M5')
            if not self._fault:
                for i in range(2):
                    self.sm["M5"] = 0.0
                self._fault=True

        if mission_task == 'M6_fault':
            print('Fault on M6')
            if not self._fault:
                for i in range(2):
                    self.sm["M6"] = 0.0
                self._fault=True

        if mission_task == 'Resurrect1':
            resurrect(self)
        if mission_task == 'Resurrect2':
            resurrect(self)
        if mission_task == 'Resurrect3':
            resurrect(self)
        if mission_task == 'Resurrect4':
            resurrect(self)
        if mission_task == 'Resurrect5':
            resurrect(self)
        if mission_task == 'Resurrect6':
            resurrect(self)
        if mission_task == 'Resurrect7':
            resurrect(self)


        if mission_task == 'takeoff':
            print('TAKE-OFF!!!')
            if not self._take_off :
                self.cmd.jump_to_block(2)
                time.sleep(0.5)
                self.cmd.jump_to_block(3)
                self._take_off = True

        elif mission_task == 'circle':
            print('We are circling!!!')
            V_des += self.traj.get_vector_field(self._position[0], self._position[1], self._position[2])*self.circle_vel
            # Getting and setting the navigation heading of the vehicles
            follow_heading = True
            if follow_heading:
                heading_des = (1.5707963267948966-atan2(V_des[0],V_des[1]))*2**12
                # heading_cur = self.sm["nav_heading"].value
                # print(f'Nav heading error is : {heading_des-heading_cur}')
                if self.sm:
                    self.sm["nav_heading"] = heading_des

            self.send_acceleration(V_des)

        elif mission_task == 'parametric_circle':
            print('We are circling with parametric circle !!!')
            # now = time.time() #self.fs.get_current_task_time()
            # dt = now-self.fs._current_task_last_time
            # self._current_task_last_time = now
            V_des_increment,uw = self.traj_parametric.get_vector_field(self._position[0], self._position[1], self._position[2], self.gvf_parameter)
            # import pdb
            # pdb.set_trace()
            # print(f'Shape of V_des : {V_des_increment.shape}')
            # print(f'dt : {0.1}, parameter : {self.gvf_parameter} ')
            V_des += V_des_increment 
            self.gvf_parameter += -uw[0]*0.1 #dt

            # Getting and setting the navigation heading of the vehicles
            # print(f'Nav heading value is : {self.sm["nav_heading"]}')
            # if self.sm:
            #     self.sm["nav_heading"] = (1.5707963267948966-atan2(V_des[0],V_des[1]))*2**12
            # self.sm["nav_heading"] = 0.0

            self.send_acceleration(V_des, A_3D=True)

        # print(self.belief_map.keys())
        elif mission_task == 'nav2land':
            print('We are going for landing!!!')
            self.send_acceleration(V_des) # This is 2D with fixed 2m altitude height AGL
            if self.fs._current_task_time > 3. : self.cmd.jump_to_block(5)


        elif mission_task == 'land':
            print('We are landing!!!')
            if not self._land :
                self.cmd.jump_to_block(12)
                self._land = True

        elif mission_task == 'safe2land':
            V_des = self.get_vector_field(self.fs.task, position=self._position_initial)
            self.send_acceleration(V_des)
        # else mission_task == 'kill' :


    def run(self):
        # while True:
        print(f'Running the vehicle {self._ac_id} in {self.fs.task} state ')
        self.calculate_cmd(self.fs.task)
