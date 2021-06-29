
"""
This script provides the environment for a quadrotor runway inspection simulation.

Three 4-dof quadrotors are tasked with inspecting a runway. They must learn to 
work together as a team. Each cell of the runway needs to be inspected by any of 
the three quadrotors. Rewards are only given when a new cell has been inspected.

Each quadrotor knows where the other ones are. They all use the same policy network.
They also all know the state of the runway and they all receive rewards when a 
new cell is explored.

Altitude is considered but heading is not considered.

All dynamic environments I create will have a standardized architecture. The
reason for this is I have one learning algorithm and many environments. All
environments are responsible for:
    - dynamics propagation (via the step method)
    - initial conditions   (via the reset method)
    - reporting environment properties (defined in __init__)
    - seeding the dynamics (via the seed method)
    - animating the motion (via the render method):
        - Rendering is done all in one shot by passing the completed states
          from a trial to the render() method.

Outputs:
    Reward must be of shape ()
    State must be of shape (OBSERVATION_SIZE,)
    Done must be a bool

Inputs:
    Action input is of shape (ACTION_SIZE,)

Communication with agent:
    The agent communicates to the environment through two queues:
        agent_to_env: the agent passes actions or reset signals to the environment
        env_to_agent: the environment returns information to the agent

Reward system:
        - A reward of +1 is given for finding an unexplored runway element
        - Penaltys may be given for collisions or proportional to the distance 
          between the quadrotors.

State clarity:
    - TOTAL_STATE contains all relevant information describing the problem, and all the information needed to animate the motion
      TOTAL_STATE is returned from the environment to the agent.
      A subset of the TOTAL_STATE, called the 'observation', is passed to the policy network to calculate acitons. This takes place in the agent
      The TOTAL_STATE is passed to the animator below to animate the motion.
      The chaser and target state are contained in the environment. They are packaged up before being returned to the agent.
      The total state information returned must be as commented beside self.TOTAL_STATE_SIZE.


Started May 19, 2020
@author: Kirk Hovell (khovell@gmail.com)
"""
import numpy as np
import os
import signal
import multiprocessing
import queue
from scipy.integrate import odeint # Numerical integrator
from shapely.geometry import Polygon, LineString

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection # to shade the runway in a 3D plot
from mpl_toolkits.mplot3d import Axes3D

"""
Note: 
    - 
"""

class Environment:

    def __init__(self):
        ##################################
        ##### Environment Properties #####
        ##################################
        self.NUMBER_OF_QUADS                  = 1 # Number of quadrotors working together to complete the task
        self.BASE_STATE_SIZE                  = self.NUMBER_OF_QUADS * 6 # [my_x, my_y, my_z, my_Vx, my_Vy, my_Vz, other1_x, other1_y, other1_z, other1_Vx, other1_Vy, other1_Vz, other2_x, other2_y, other2_z, other2_Vx, other2_Vy, other2_Vz]  
        self.INDOORS                          = True # True = indoors; False = outdoors
        if self.INDOORS:
            self.RUNWAY_WIDTH                     = 4 # [m] in Y (West)
            self.RUNWAY_LENGTH                    = 4 # [m] in X (North)
        else:
            self.RUNWAY_WIDTH                     = 12.5 # [m] in Y (West)
            self.RUNWAY_LENGTH                    = 124 # [m] in X (North)        
        self.RUNWAY_WIDTH_ELEMENTS            = 4 # 4[elements]
        self.RUNWAY_LENGTH_ELEMENTS           = 8 # 8[elements]
        self.IRRELEVANT_STATES                = [2,5] # indices of states who are irrelevant to the policy network
        self.ACTION_SIZE                      = 2 # [my_x_dot_dot, my_y_dot_dot]
        self.NORMALIZE_STATE                  = True # Normalize state on each timestep to avoid vanishing gradients
        self.RANDOMIZE                        = True # whether or not to RANDOMIZE the state & target location
        self.POSITION_RANDOMIZATION_SD        = np.array([self.RUNWAY_LENGTH*2/3, self.RUNWAY_WIDTH*2/3, 1.0]) # [m, m, m]
        self.INITIAL_QUAD_POSITION            = np.array([.0, .0, 3.0]) # [m, m, m]         
        self.MIN_V                            =  0.
        self.MAX_V                            =  self.RUNWAY_LENGTH_ELEMENTS*self.RUNWAY_WIDTH_ELEMENTS
        self.N_STEP_RETURN                    =   2
        self.DISCOUNT_FACTOR                  =   0.95**(1/self.N_STEP_RETURN)
        self.TIMESTEP                         =   0.2 # [s]
        self.DYNAMICS_DELAY                   =   3 # [timesteps of delay] how many timesteps between when an action is commanded and when it is realized
        self.AUGMENT_STATE_WITH_ACTION_LENGTH =   3 # [timesteps] how many timesteps of previous actions should be included in the state. This helps with making good decisions among delayed dynamics.
        self.MAX_NUMBER_OF_TIMESTEPS          = 300 # per episode
        self.ADDITIONAL_VALUE_INFO            = False # whether or not to include additional reward and value distribution information on the animations
        self.TOP_DOWN_VIEW                    = True # Animation property
        self.SKIP_FAILED_ANIMATIONS           = True # Error the program or skip when animations fail?

        # Test time properties
        self.TEST_ON_DYNAMICS                 = True # Whether or not to use full dynamics along with a PD controller at test time
        self.KINEMATIC_NOISE                  = False # Whether or not to apply noise to the kinematics in order to simulate a poor controller
        self.KINEMATIC_NOISE_SD               = [0.02, 0.02, 0.02] # The standard deviation of the noise that is to be applied to each element in the state
        self.FORCE_NOISE_AT_TEST_TIME         = False # [Default -> False] Whether or not to force kinematic noise to be present at test time

        # PD Controller Gains
        self.KI                               = 0.5 # Integral gain for the integral-linear acceleration controller
        
        # Physical properties
        self.LENGTH                           = 0.3  # [m] side length
        self.MASS                             = 0.5   # [kg]
        
        # Target collision properties
        self.COLLISION_DISTANCE               = self.LENGTH # [m] how close chaser and target need to be before a penalty is applied
        self.COLLISION_PENALTY                = 15           # [rewards/second] penalty given for colliding with target  

        # Additional properties
        self.ACCELERATION_PENALTY             = 0.0 # [factor] how much to penalize all acceleration commands
        if self.INDOORS:  
            self.VELOCITY_LIMIT                   = 4 # [m/s] maximum allowable velocity, a hard cap is enforced if this velocity is exceeded. Note: Paparazzi must also supply a hard velocity cap        
            self.MINIMUM_CAMERA_ALTITUDE          = 0 # [m] minimum altitude above the runway to get a reliable camera shot. If below this altitude, the runway element is not considered explored
            self.MAXIMUM_CAMERA_ALTITUDE          = 10 # [m] maximum altitude above the runway to get a reliable camera shot. If above this altitude, the runway element is not considered explored
            self.PROXIMITY_PENALTY_MAXIMUM        = 1 # how much to penalize closeness of the quadrotors to encourage them not to bunch up; penalty = -PROXIMITY_PENALTY_MAXIMUM*exp(-distance/PROXIMITY_PENALTY_FACTOR)
            self.PROXIMITY_PENALTY_FACTOR         = 0.43 # how much the penalty decays with distance -> a penalty of 0.01 when they are 2 m apart. To change: = -distance/ln(desired_penalty)
            self.LOWER_ACTION_BOUND               = np.array([-2.0, -2.0]) # [m/s^2, m/s^2, m/s^2]
            self.UPPER_ACTION_BOUND               = np.array([ 2.0,  2.0]) # [m/s^2, m/s^2, m/s^2]
            self.LOWER_STATE_BOUND_PER_QUAD       = np.array([ -3. - self.RUNWAY_LENGTH/2, -3. - self.RUNWAY_WIDTH/2,  0., -self.VELOCITY_LIMIT, -self.VELOCITY_LIMIT, -self.VELOCITY_LIMIT]) # [m, m, m, m/s, m/s, m/s]
            self.UPPER_STATE_BOUND_PER_QUAD       = np.array([  3. + self.RUNWAY_LENGTH/2,  3. + self.RUNWAY_WIDTH/2, 10.,  self.VELOCITY_LIMIT,  self.VELOCITY_LIMIT,  self.VELOCITY_LIMIT]) # [m, m, m, m/s, m/s, m/s]
        
        else:
            self.VELOCITY_LIMIT                   = 10 # [m/s] maximum allowable velocity, a hard cap is enforced if this velocity is exceeded. Note: Paparazzi must also supply a hard velocity cap
            self.MINIMUM_CAMERA_ALTITUDE          = 0 # [m] minimum altitude above the runway to get a reliable camera shot. If below this altitude, the runway element is not considered explored
            self.MAXIMUM_CAMERA_ALTITUDE          = 2000 # [m] maximum altitude above the runway to get a reliable camera shot. If above this altitude, the runway element is not considered explored
            self.PROXIMITY_PENALTY_MAXIMUM        = 1 # how much to penalize closeness of the quadrotors to encourage them not to bunch up; penalty = -PROXIMITY_PENALTY_MAXIMUM*exp(-distance/PROXIMITY_PENALTY_FACTOR)
            self.PROXIMITY_PENALTY_FACTOR         = 4.3 # how much the penalty decays with distance -> a penalty of 0.01 when they are 20 m apart. To change: = -distance/ln(desired_penalty)
            self.LOWER_ACTION_BOUND               = np.array([-3.0, -3.0]) # [m/s^2, m/s^2, m/s^2]
            self.UPPER_ACTION_BOUND               = np.array([ 3.0,  3.0]) # [m/s^2, m/s^2, m/s^2]
            self.LOWER_STATE_BOUND_PER_QUAD       = np.array([ -10. - self.RUNWAY_LENGTH/2, -10. - self.RUNWAY_WIDTH/2,  0., -self.VELOCITY_LIMIT, -self.VELOCITY_LIMIT, -self.VELOCITY_LIMIT]) # [m, m, m, m/s, m/s, m/s]
            self.UPPER_STATE_BOUND_PER_QUAD       = np.array([  10. + self.RUNWAY_LENGTH/2,  10. + self.RUNWAY_WIDTH/2, 20.,  self.VELOCITY_LIMIT,  self.VELOCITY_LIMIT,  self.VELOCITY_LIMIT]) # [m, m, m, m/s, m/s, m/s]      
            

        # Generate Polygons for runway tiles
        # The size of each runway grid element
        each_runway_length_element = self.RUNWAY_LENGTH/self.RUNWAY_LENGTH_ELEMENTS
        each_runway_width_element  = self.RUNWAY_WIDTH/self.RUNWAY_WIDTH_ELEMENTS
        self.tile_polygons = []
        for i in range(self.RUNWAY_LENGTH_ELEMENTS):
            this_row = []
            for j in range(self.RUNWAY_WIDTH_ELEMENTS):
                # make the polygon
                this_row.append(Polygon([[each_runway_length_element*i     - self.RUNWAY_LENGTH/2, each_runway_width_element*j     - self.RUNWAY_WIDTH/2],
                                         [each_runway_length_element*(i+1) - self.RUNWAY_LENGTH/2, each_runway_width_element*j     - self.RUNWAY_WIDTH/2],
                                         [each_runway_length_element*(i+1) - self.RUNWAY_LENGTH/2, each_runway_width_element*(j+1) - self.RUNWAY_WIDTH/2],
                                         [each_runway_length_element*i     - self.RUNWAY_LENGTH/2, each_runway_width_element*(j+1) - self.RUNWAY_WIDTH/2]]))
                
            self.tile_polygons.append(this_row)


        # Performing some calculations  
        self.RUNWAY_STATE_SIZE                = self.RUNWAY_WIDTH_ELEMENTS * self.RUNWAY_LENGTH_ELEMENTS # how big the runway "grid" is                                                   
        self.TOTAL_STATE_SIZE                 = self.BASE_STATE_SIZE + self.RUNWAY_STATE_SIZE
        self.LOWER_STATE_BOUND                = np.concatenate([np.tile(self.LOWER_STATE_BOUND_PER_QUAD, self.NUMBER_OF_QUADS), np.tile(self.LOWER_ACTION_BOUND, self.AUGMENT_STATE_WITH_ACTION_LENGTH), np.zeros(self.RUNWAY_STATE_SIZE)]) # lower bound for each element of TOTAL_STATE
        self.UPPER_STATE_BOUND                = np.concatenate([np.tile(self.UPPER_STATE_BOUND_PER_QUAD, self.NUMBER_OF_QUADS), np.tile(self.UPPER_ACTION_BOUND, self.AUGMENT_STATE_WITH_ACTION_LENGTH),  np.ones(self.RUNWAY_STATE_SIZE)]) # upper bound for each element of TOTAL_STATE        
        self.OBSERVATION_SIZE                 = self.TOTAL_STATE_SIZE - len(self.IRRELEVANT_STATES)*self.NUMBER_OF_QUADS # the size of the observation input to the policy

    ###################################
    ##### Seeding the environment #####
    ###################################
    def seed(self, seed):
        np.random.seed(seed)

    ######################################
    ##### Resettings the Environment #####
    ######################################
    def reset(self, use_dynamics, test_time):
        # This method resets the state and returns it
        """ NOTES:
               - if use_dynamics = True -> use dynamics
               - if test_time = True -> do not add "exploration noise" to the kinematics or actions
        """        

        # Logging whether it is test time for this episode
        self.test_time = test_time
        
        self.quad_positions = np.zeros([self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)])

        # If we are randomizing the initial conditions and state
        if self.RANDOMIZE:
            # Randomizing initial state
            for i in range(self.NUMBER_OF_QUADS):
                self.quad_positions[i] = self.INITIAL_QUAD_POSITION + np.random.uniform(low = -1, high = 1, size = len(self.POSITION_RANDOMIZATION_SD))*self.POSITION_RANDOMIZATION_SD
        else:
            # Constant initial state
            for i in range(self.NUMBER_OF_QUADS):
                self.quad_positions[i] = self.INITIAL_QUAD_POSITION

        # Quadrotors' initial velocity is not randomized
        self.quad_velocities = np.zeros([self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)])
        
        # Initializing the previous velocity and control effort for the integral-acceleration controller
        self.previous_quad_velocities = np.zeros([self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)])
        self.previous_linear_control_efforts = np.zeros([self.NUMBER_OF_QUADS, self.ACTION_SIZE + 1])  
        
        # Initializing the previous quad position (used for runway exploration calculation)
        self.previous_quad_positions = self.quad_positions
        
        if use_dynamics:            
            self.dynamics_flag = True # for this episode, dynamics will be used
        else:
            self.dynamics_flag = False # the default is to use kinematics

        # Resetting the time
        self.time = 0.
        
        # Resetting the runway state
        self.runway_state = np.zeros([self.RUNWAY_LENGTH_ELEMENTS, self.RUNWAY_WIDTH_ELEMENTS])
        self.previous_runway_value = 0
        
        # Resetting the action delay queue        
        if self.DYNAMICS_DELAY > 0:
            self.action_delay_queue = queue.Queue(maxsize = self.DYNAMICS_DELAY + 1)
            for i in range(self.DYNAMICS_DELAY):
                self.action_delay_queue.put(np.zeros([self.NUMBER_OF_QUADS, self.ACTION_SIZE + 1]), False)

    #####################################
    ##### Step the Dynamics forward #####
    #####################################
    def step(self, actions):

        # Stepping the environment forward one time step.
        # Returns initial condition on first row then next TIMESTEP on the next row
        #########################################
        ##### PROPAGATE KINEMATICS/DYNAMICS #####
        #########################################
        if self.dynamics_flag:
            ############################
            #### PROPAGATE DYNAMICS ####
            ############################

            # Next, calculate the control effort
            control_efforts = self.controller(actions)    

            # Anything additional that needs to be sent to the dynamics integrator
            dynamics_parameters = [control_efforts, self.MASS, self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)]

            # Propagate the dynamics forward one timestep
            next_states = odeint(dynamics_equations_of_motion, np.concatenate([self.quad_positions.reshape(-1), self.quad_velocities.reshape(-1)]), [self.time, self.time + self.TIMESTEP], args = (dynamics_parameters,), full_output = 0)

            # Saving the new state
            self.quad_positions  = next_states[1,:self.NUMBER_OF_QUADS*len(self.INITIAL_QUAD_POSITION)].reshape([self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)])
            self.quad_velocities = next_states[1,self.NUMBER_OF_QUADS*len(self.INITIAL_QUAD_POSITION):].reshape([self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)])
            # Note: the controller is supposed to limit the quad velocity at test time
            
        else:

            # Additional parameters to be passed to the kinematics
            kinematics_parameters = [actions, self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)]

            ###############################
            #### PROPAGATE KINEMATICS #####
            ###############################
            next_states = odeint(kinematics_equations_of_motion, np.concatenate([self.quad_positions.reshape(-1), self.quad_velocities.reshape(-1)]), [self.time, self.time + self.TIMESTEP], args = (kinematics_parameters,), full_output = 0)

            # Saving the new state
            self.quad_positions  = next_states[1,:self.NUMBER_OF_QUADS*len(self.INITIAL_QUAD_POSITION)].reshape([self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)])
            self.quad_velocities = next_states[1,self.NUMBER_OF_QUADS*len(self.INITIAL_QUAD_POSITION):].reshape([self.NUMBER_OF_QUADS, len(self.INITIAL_QUAD_POSITION)])
            self.quad_velocities = np.clip(self.quad_velocities, -self.VELOCITY_LIMIT, self.VELOCITY_LIMIT) # clipping the linear velocity to be within the limits

        # Done the differences between the kinematics and dynamics
        # Increment the timestep
        self.time += self.TIMESTEP
                
        # Update the state of the runway
        self.check_runway()

        # Calculating the reward for this state-action pair
        reward = self.reward_function(actions)

        # Check if this episode is done
        done = self.is_done()

        # Return the (reward, done)
        return reward, done

    def controller(self, actions):
        # This function calculates the control effort based on the state and the
        # desired acceleration (action)
        
        ###############################################################
        ### Acceleration control (integral-acceleration controller) ###
        ###############################################################
        desired_linear_accelerations = actions
        
        current_velocities = self.quad_velocities
        current_linear_accelerations = (current_velocities - self.previous_quad_velocities)/self.TIMESTEP # Approximating the current acceleration [a_x, a_y, a_z]
        
        # Checking whether our velocity is too large AND the acceleration is trying to increase said velocity... in which case we set the desired_linear_acceleration to zero.
        desired_linear_accelerations[(np.abs(current_velocities) > self.VELOCITY_LIMIT) & (np.sign(desired_linear_accelerations) == np.sign(current_velocities))] = 0        
        
        # Calculating acceleration error
        linear_acceleration_error = desired_linear_accelerations - current_linear_accelerations
        
        # Integral-acceleration control
        linear_control_effort = self.previous_linear_control_efforts + self.KI * linear_acceleration_error
        
        # Saving the current velocity for the next timetsep
        self.previous_quad_velocities = current_velocities
        
        # Saving the current control effort for the next timestep
        self.previous_linear_control_efforts = linear_control_effort
        
        return linear_control_effort

    def check_runway(self):
        # This method updates the runway state based off the current quadrotor positions
        """ The runway is 
        self.RUNWAY_WIDTH (East)
        self.RUNWAY_LENGTH (North)
        self.RUNWAY_WIDTH_ELEMENTS
        self.RUNWAY_LENGTH_ELEMENTS
        
        """

        
        """ New runway method where each tile is a Polygon and the motion from the last timestep is a LineString and 
            the intersecting tiles are considered explored. This fixes the experimental problems where corners of tiles
            were being flown over but not considered explored
        """
        # Generate quadrotor LineStrings
        for i in range(self.NUMBER_OF_QUADS):
            quad_line = LineString([self.quad_positions[i,:-1], self.previous_quad_positions[i,:-1]])
            
            for j in range(self.RUNWAY_LENGTH_ELEMENTS):
                for k in range(self.RUNWAY_WIDTH_ELEMENTS):                    
                    # If this element has already been explored, skip it
                    if self.runway_state[j,k] == 0 and quad_line.intersects(self.tile_polygons[j][k]):
                        self.runway_state[j,k] = 1
                        #print("Quad %i traced the line %s and explored runway element length = %i, width = %i with coordinates %s" %(i,list(quad_line.coords),j,k,self.tile_polygons[j][k].bounds))
            
        # Storing current quad positions for the next timestep
        self.previous_quad_positions = self.quad_positions
       
    
    def check_quad_distances(self):
        # Checks the scalar distance from each quad to its neighbours in X and Y ONLY (altitude is ignored)
        # If there are more than 2 quads, the distance of the nearest one is returned
        
        # Initializing the distances (to large numbers incase there is only one quad)
        minimum_distances = np.ones(self.NUMBER_OF_QUADS)*1000.0
        
        # For this quad
        for i in range(self.NUMBER_OF_QUADS):         
            # Check all the other quads
            for j in range(i + 1, self.NUMBER_OF_QUADS + i):
                this_distance = np.linalg.norm([self.quad_positions[i,0] - self.quad_positions[j % self.NUMBER_OF_QUADS,0], self.quad_positions[i,1] - self.quad_positions[j % self.NUMBER_OF_QUADS,1]])

                # Replace the minimum distance with this if it's smaller
                if this_distance < minimum_distances[i]:
                    minimum_distances[i] = this_distance

        return minimum_distances

    def reward_function(self, action):
        # Returns the reward for this TIMESTEP as a function of the state and action
        
        # Initializing the rewards to zero for all quads
        rewards = np.zeros(self.NUMBER_OF_QUADS)
        
        # Give rewards according to the change in runway state. A newly explored tile will yield a reward of +1
        rewards += np.sum(self.runway_state) - self.previous_runway_value
        
        # Storing the current runway state for the next timestep
        self.previous_runway_value = np.sum(self.runway_state)

        # Penalizing acceleration commands (to encourage fuel efficiency)
        rewards -= np.sum(self.ACCELERATION_PENALTY*np.abs(action), axis = 1)

        # Penalizing quadrotor proximity (to discourage grouping)
        rewards -= self.PROXIMITY_PENALTY_MAXIMUM*np.exp(-self.check_quad_distances()/self.PROXIMITY_PENALTY_FACTOR)

        return rewards

    def is_done(self):
        # Checks if this episode is done or not
        """
            NOTE: THE ENVIRONMENT MUST RETURN done = True IF THE EPISODE HAS
                  REACHED ITS LAST TIMESTEP
        """
        # Initializing
        done = False
        
        # If we've explored the entire runway
        if np.sum(self.runway_state) == self.RUNWAY_STATE_SIZE:
            done = True

        # If we've run out of timesteps
        if round(self.time/self.TIMESTEP) == self.MAX_NUMBER_OF_TIMESTEPS:
            done = True

        return done


    def generate_queue(self):
        # Generate the queues responsible for communicating with the agent
        self.agent_to_env = multiprocessing.Queue(maxsize = 1)
        self.env_to_agent = multiprocessing.Queue(maxsize = 1)

        return self.agent_to_env, self.env_to_agent
    

    def run(self):
        ###################################
        ##### Running the environment #####
        ###################################
        """
        This method is called when the environment process is launched by main.py.
        It is responsible for continually listening for an input action from the
        agent through a Queue. If an action is received, it is to step the environment
        and return the results.
        """
        # Instructing this process to treat Ctrl+C events (called SIGINT) by going SIG_IGN (ignore).
        # This permits the process to continue upon a Ctrl+C event to allow for graceful quitting.
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Loop until the process is terminated
        while True:
            # Blocks until the agent passes us an action
            actions, *test_time = self.agent_to_env.get()        

            if np.any(type(actions) == bool):
                # The signal to reset the environment was received
                self.reset(actions, test_time[0])
                
                # Return the TOTAL_STATE           
                self.env_to_agent.put((self.quad_positions, self.quad_velocities, self.runway_state))

            else:
                # Delay the action by DYNAMICS_DELAY timesteps. The environment accumulates the action delay--the agent still thinks the sent action was used.
                if self.DYNAMICS_DELAY > 0:
                    self.action_delay_queue.put(actions,False) # puts the current action to the bottom of the stack
                    actions = self.action_delay_queue.get(False) # grabs the delayed action and treats it as truth.                
                
                ################################
                ##### Step the environment #####
                ################################    
                rewards, done = self.step(actions)

                # Return (TOTAL_STATE, reward, done, guidance_position)
                self.env_to_agent.put((self.quad_positions, self.quad_velocities, self.runway_state, rewards, done))

###################################################################
##### Generating kinematics equations representing the motion #####
###################################################################
def kinematics_equations_of_motion(state, t, parameters):
    """ 
    Returns the first derivative of the state
    The state is [position, velocity]; its derivative is [velocity, acceleration]
    """
    
    # Unpacking the action from the parameters
    actions = parameters[0]
    NUMBER_OF_QUADS = parameters[1]
    QUAD_POSITION_LENGTH = parameters[2]
    
    # state = quad_positions, quad_velocities concatenated
    #quad_positions  = state[:NUMBER_OF_QUADS*QUAD_POSITION_LENGTH]
    quad_velocities = state[NUMBER_OF_QUADS*QUAD_POSITION_LENGTH:]
    
    # Flattening the accelerations into a column
    accelerations = actions.reshape(-1) # [x_dot_dot, y_dot_dot, x_dot_dot, y_dot_dot....]

    # Building the derivative matrix.
    derivatives = np.concatenate([quad_velocities, accelerations])

    return derivatives


#####################################################################
##### Generating the dynamics equations representing the motion #####
#####################################################################
def dynamics_equations_of_motion(state, t, parameters):
    """ 
    Returns the first derivative of the state
    The state is [position, velocity]; its derivative is [velocity, acceleration]
    """
    # Unpacking the parameters
    control_efforts, mass, NUMBER_OF_QUADS, QUAD_POSITION_LENGTH = parameters

    # Unpacking the state
    #quad_positions  = state[:NUMBER_OF_QUADS*QUAD_POSITION_LENGTH]
    quad_velocities = state[NUMBER_OF_QUADS*QUAD_POSITION_LENGTH:]
    
    # Calculating accelerations = F/m
    accelerations = control_efforts.reshape(-1)/mass

    # Building derivatives array
    derivatives = np.concatenate([quad_velocities, accelerations]) #.squeeze()?

    return derivatives


##########################################
##### Function to animate the motion #####
##########################################
def render(states, actions, instantaneous_reward_log, cumulative_reward_log, critic_distributions, target_critic_distributions, projected_target_distribution, bins, loss_log, episode_number, filename, save_directory):
    """
    states = [# timesteps, # quads, total_state_size]
    action = [# timesteps, # quads, action_size]
    instantaneous_reward_log = [# timesteps, # quads]
    cumulative_reward_log = [# timesteps, # quads]
    
    ===FOR QUAD 0 ONLY===
    critic_distributions
    target_critic_distributions
    projected_target_distribution
    
    
    Animate a variable number of quadrotors inspecting a runway.
    - Plot 3D cube of any number of quads
    - Plot the runway and shade in elements as they become discovered (as listed in the state)
    
    """

    # Load in a temporary environment, used to grab the physical parameters
    temp_env = Environment()

    # Checking if we want the additional reward and value distribution information
    extra_information = temp_env.ADDITIONAL_VALUE_INFO

    # Extracting physical properties
    length = temp_env.LENGTH

    ### Calculating quadrotor corner locations through time ###
    
    # Corner locations in body frame    
    quad_body_body_frame = length/2.*np.array([[[1],[-1],[1]],
                                              [[-1],[-1],[1]],
                                              [[-1],[-1],[-1]],
                                              [[1],[-1],[-1]],
                                              [[1],[-1],[1]],
                                              [[1],[1],[1]],
                                              [[-1],[1],[1]],
                                              [[-1],[-1],[1]],
                                              [[-1],[-1],[-1]],
                                              [[-1],[1],[-1]],
                                              [[-1],[1],[1]],
                                              [[-1],[1],[-1]],
                                              [[1],[1],[-1]],
                                              [[1],[1],[1]],
                                              [[1],[1],[-1]],
                                              [[1],[-1],[-1]]]).squeeze()

    # Generating figure window
    figure = plt.figure(constrained_layout = True)
    figure.set_size_inches(5, 4, True)

    if extra_information:
        grid_spec = gridspec.GridSpec(nrows = 2, ncols = 3, figure = figure)
        subfig1 = figure.add_subplot(grid_spec[0,0], projection = '3d', aspect = 'equal', autoscale_on = False, xlim3d = (temp_env.LOWER_STATE_BOUND_PER_QUAD[0], temp_env.UPPER_STATE_BOUND_PER_QUAD[0]), ylim3d = (temp_env.LOWER_STATE_BOUND_PER_QUAD[1], temp_env.UPPER_STATE_BOUND_PER_QUAD[1]), zlim3d = (temp_env.LOWER_STATE_BOUND_PER_QUAD[2], temp_env.UPPER_STATE_BOUND_PER_QUAD[2]), xlabel = 'X (m)', ylabel = 'Y (m)', zlabel = 'Z (m)')
        subfig2 = figure.add_subplot(grid_spec[0,1], xlim = (np.min([np.min(instantaneous_reward_log[:,0]), 0]) - (np.max(instantaneous_reward_log[:,0]) - np.min(instantaneous_reward_log[:,0]))*0.02, np.max([np.max(instantaneous_reward_log[:,0]), 0]) + (np.max(instantaneous_reward_log[:,0]) - np.min(instantaneous_reward_log[:,0]))*0.02), ylim = (-0.5, 0.5))
        subfig3 = figure.add_subplot(grid_spec[0,2], xlim = (np.min(loss_log)-0.01, np.max(loss_log)+0.01), ylim = (-0.5, 0.5))
        subfig4 = figure.add_subplot(grid_spec[1,0], ylim = (0, 1.02))
        subfig5 = figure.add_subplot(grid_spec[1,1], ylim = (0, 1.02))
        subfig6 = figure.add_subplot(grid_spec[1,2], ylim = (0, 1.02))

        # Setting titles
        subfig1.set_xlabel("X (m)",    fontdict = {'fontsize': 8})
        subfig1.set_ylabel("Y (m)",    fontdict = {'fontsize': 8})
        subfig2.set_title("Timestep Reward",    fontdict = {'fontsize': 8})
        subfig3.set_title("Current loss",       fontdict = {'fontsize': 8})
        subfig4.set_title("Q-dist",             fontdict = {'fontsize': 8})
        subfig5.set_title("Target Q-dist",      fontdict = {'fontsize': 8})
        subfig6.set_title("Bellman projection", fontdict = {'fontsize': 8})

        # Changing around the axes
        subfig1.tick_params(labelsize = 8)
        subfig2.tick_params(which = 'both', left = False, labelleft = False, labelsize = 8)
        subfig3.tick_params(which = 'both', left = False, labelleft = False, labelsize = 8)
        subfig4.tick_params(which = 'both', left = False, labelleft = False, right = True, labelright = False, labelsize = 8)
        subfig5.tick_params(which = 'both', left = False, labelleft = False, right = True, labelright = False, labelsize = 8)
        subfig6.tick_params(which = 'both', left = False, labelleft = False, right = True, labelright = True, labelsize = 8)

        # Adding the grid
        subfig4.grid(True)
        subfig5.grid(True)
        subfig6.grid(True)

        # Setting appropriate axes ticks
        subfig2.set_xticks([np.min(instantaneous_reward_log[:,0]), 0, np.max(instantaneous_reward_log[:,0])] if np.sign(np.min(instantaneous_reward_log[:,0])) != np.sign(np.max(instantaneous_reward_log[:,0])) else [np.min(instantaneous_reward_log[:,0]), np.max(instantaneous_reward_log[:,0])])
        subfig3.set_xticks([np.min(loss_log), np.max(loss_log)])
        subfig4.set_xticks([bins[i*5] for i in range(round(len(bins)/5) + 1)])
        subfig4.tick_params(axis = 'x', labelrotation = -90)
        subfig4.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.])
        subfig5.set_xticks([bins[i*5] for i in range(round(len(bins)/5) + 1)])
        subfig5.tick_params(axis = 'x', labelrotation = -90)
        subfig5.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.])
        subfig6.set_xticks([bins[i*5] for i in range(round(len(bins)/5) + 1)])
        subfig6.tick_params(axis = 'x', labelrotation = -90)
        subfig6.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.])

    else:
        subfig1 = figure.add_subplot(1, 1, 1, projection = '3d', aspect = 'equal', autoscale_on = False, xlim3d = (temp_env.LOWER_STATE_BOUND_PER_QUAD[0], temp_env.UPPER_STATE_BOUND_PER_QUAD[0]), ylim3d = (temp_env.LOWER_STATE_BOUND_PER_QUAD[1], temp_env.UPPER_STATE_BOUND_PER_QUAD[1]), zlim3d = (temp_env.LOWER_STATE_BOUND_PER_QUAD[2], temp_env.UPPER_STATE_BOUND_PER_QUAD[2]), xlabel = 'X (m)', ylabel = 'Y (m)', zlabel = 'Z')
        
    # Since matplotlib doesn't have 'aspect = 'equal'' implemented, I have to manually
    # do it. I adjust the limits so that they're the same length in all directions,
    # centred at the right location.
    x_limits = subfig1.get_xlim3d()
    y_limits = subfig1.get_ylim3d()
    z_limits = subfig1.get_zlim3d()
    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)
    plot_radius = 0.5*max([x_range, y_range, z_range])
    subfig1.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    subfig1.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    subfig1.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])        
    
    # Setting the proper view
    if temp_env.TOP_DOWN_VIEW:
        subfig1.view_init(90,180)
    else:
        subfig1.view_init(25, 190)  
    
    # Defining the runway element coordinates
    runway_elements = []
    width_vertices = np.linspace(-temp_env.RUNWAY_WIDTH/2, temp_env.RUNWAY_WIDTH/2, temp_env.RUNWAY_WIDTH_ELEMENTS + 1)
    length_vertices = np.linspace(-temp_env.RUNWAY_LENGTH/2, temp_env.RUNWAY_LENGTH/2, temp_env.RUNWAY_LENGTH_ELEMENTS + 1)
    for i in range(temp_env.RUNWAY_LENGTH_ELEMENTS):
        for j in range(temp_env.RUNWAY_WIDTH_ELEMENTS):
            runway_element_vertices = np.array([[length_vertices[i],width_vertices[j]],
                                                [length_vertices[i],width_vertices[j+1]],
                                                [length_vertices[i+1],width_vertices[j+1]],
                                                [length_vertices[i+1],width_vertices[j]],
                                                [length_vertices[i],width_vertices[j]]])
            runway_elements.append(runway_element_vertices)
    full_runway = np.array([[length_vertices[0],width_vertices[0]],
                            [length_vertices[0],width_vertices[-1]],
                            [length_vertices[-1],width_vertices[-1]],
                            [length_vertices[-1],width_vertices[0]],
                            [length_vertices[0],width_vertices[0]]])
    runway_plot, = subfig1.plot([], [], [], color = 'k', linestyle = '-', linewidth = 3)
    runway_plot.set_data(full_runway[:,0], full_runway[:,1])
    runway_plot.set_3d_properties(np.zeros(5)) 

    # Defining plotting objects that change each frame
    quad_bodies = []
    all_colours = cm.rainbow(np.linspace(0,1,temp_env.NUMBER_OF_QUADS))
    for i in range(temp_env.NUMBER_OF_QUADS):
        this_quad_body, = subfig1.plot([], [], [], color = all_colours[i], linestyle = '-', linewidth = 2, zorder=10) # Note, the comma is needed
        quad_bodies.append(this_quad_body)

    if extra_information:
        reward_bar           = subfig2.barh(y = 0, height = 0.2, width = 0)
        loss_bar             = subfig3.barh(y = 0, height = 0.2, width = 0)
        q_dist_bar           = subfig4.bar(x = bins, height = np.zeros(shape = len(bins)), width = bins[1]-bins[0])
        target_q_dist_bar    = subfig5.bar(x = bins, height = np.zeros(shape = len(bins)), width = bins[1]-bins[0])
        projected_q_dist_bar = subfig6.bar(x = bins, height = np.zeros(shape = len(bins)), width = bins[1]-bins[0])
        time_text            = subfig1.text2D(x = 0.2, y = 0.91, s = '', fontsize = 8, transform=subfig1.transAxes)
        reward_text          = subfig1.text2D(x = 0.0,  y = 1.02, s = '', fontsize = 8, transform=subfig1.transAxes)
    else:        
        time_text    = subfig1.text2D(x = 0.1, y = 0.9, s = '', fontsize = 8, transform=subfig1.transAxes)
        reward_text  = subfig1.text2D(x = 0.62, y = 0.9, s = '', fontsize = 8, transform=subfig1.transAxes)
        episode_text = subfig1.text2D(x = 0.4, y = 0.96, s = '', fontsize = 8, transform=subfig1.transAxes)
        episode_text.set_text('Episode ' + str(episode_number))

    # Function called repeatedly to draw each frame
    def render_one_frame(frame, *fargs):
        temp_env = fargs[0] # Extract environment from passed args

        # Shade the runway, where appropriate
        runway_state = states[frame,0,-temp_env.RUNWAY_STATE_SIZE:]
        if frame > 0:
            last_runway_state = states[frame-1,0,-temp_env.RUNWAY_STATE_SIZE:]
        else:
            last_runway_state = np.zeros(len(runway_state))
            
        for i in range(len(runway_state)):
            # Only update the runway if it's changed
            if runway_state[i] == 1 and last_runway_state[i] == 0:
                these_vertices = [list(zip(runway_elements[i][:,0], runway_elements[i][:,1], np.zeros(5)))]
                subfig1.add_collection3d(Poly3DCollection(these_vertices, color='grey', alpha = 0.5), zs = 0, zdir='z')
                print("Runway element changed! Frame: %i, Previous reward: %f, Current reward: %f" %(frame, cumulative_reward_log[frame-1,0], cumulative_reward_log[frame,0]))
        
        # Draw the quads
        for i in range(temp_env.NUMBER_OF_QUADS):
            quad_bodies[i].set_data(quad_body_body_frame[:,0] + states[frame,i,0], quad_body_body_frame[:,1] + states[frame,i,1])
            quad_bodies[i].set_3d_properties(quad_body_body_frame[:,2] + states[frame,i,2])
            
        # Update the time text
        time_text.set_text('Time = %.1f s' %(frame*temp_env.TIMESTEP))
        
        # Update the reward text
        reward_text.set_text('Quad 0 reward = %.1f' %cumulative_reward_log[frame,0])

        # If we want extra information AND we aren't on the last state (because the last state doesn't have value information)
        if extra_information and (frame < len(states)-1):
            # Updating the instantaneous reward bar graph
            reward_bar[0].set_width(instantaneous_reward_log[frame,0])
            # And colouring it appropriately
            if instantaneous_reward_log[frame,0] < 0:
                reward_bar[0].set_color('r')
            else:
                reward_bar[0].set_color('g')

            # Updating the loss bar graph
            loss_bar[0].set_width(loss_log[frame])

            # Updating the q-distribution plot
            for this_bar, new_value in zip(q_dist_bar, critic_distributions[frame,:]):
                this_bar.set_height(new_value)

            # Updating the target q-distribution plot
            for this_bar, new_value in zip(target_q_dist_bar, target_critic_distributions[frame, :]):
                this_bar.set_height(new_value)

            # Updating the projected target q-distribution plot
            for this_bar, new_value in zip(projected_q_dist_bar, projected_target_distribution[frame, :]):
                this_bar.set_height(new_value)
#
        # Since blit = True, must return everything that has changed at this frame
        return time_text, quad_bodies 

    # Generate the animation!
    fargs = [temp_env] # bundling additional arguments
    animator = animation.FuncAnimation(figure, render_one_frame, frames = np.linspace(0, len(states)-1, len(states)).astype(int),
                                       blit = False, fargs = fargs)

    """
    frames = the int that is passed to render_one_frame. I use it to selectively plot certain data
    fargs = additional arguments for render_one_frame
    interval = delay between frames in ms
    """
    # Save the animation!
    if temp_env.SKIP_FAILED_ANIMATIONS:
        try:
            # Save it to the working directory [have to], then move it to the proper folder
            animator.save(filename = filename + '_episode_' + str(episode_number) + '.mp4', fps = 30, dpi = 100)
            # Make directory if it doesn't already exist
            os.makedirs(os.path.dirname(save_directory + filename + '/videos/'), exist_ok=True)
            # Move animation to the proper directory
            os.rename(filename + '_episode_' + str(episode_number) + '.mp4', save_directory + filename + '/videos/episode_' + str(episode_number) + '.mp4')
        except:
            print("Skipping animation for episode %i due to an error" %episode_number)
            # Try to delete the partially completed video file
            try:
                os.remove(filename + '_episode_' + str(episode_number) + '.mp4')
            except:
                pass
    else:
        # Save it to the working directory [have to], then move it to the proper folder
        animator.save(filename = filename + '_episode_' + str(episode_number) + '.mp4', fps = 30, dpi = 100)
        # Make directory if it doesn't already exist
        os.makedirs(os.path.dirname(save_directory + filename + '/videos/'), exist_ok=True)
        # Move animation to the proper directory
        os.rename(filename + '_episode_' + str(episode_number) + '.mp4', save_directory + filename + '/videos/episode_' + str(episode_number) + '.mp4')

    del temp_env
    plt.close(figure)