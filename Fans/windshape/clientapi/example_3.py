

import src.windControlAPI
import time

#------------------------------------------------------------------------------
# WINDCONTROL APP INITIALIZATION
#------------------------------------------------------------------------------

# Start WindControl App and initiate communication with the server
wcapi = src.windControlAPI.WindControlApp(verbose_comm=False)

# Initialize comminication with server
#wcapi.prepareServerLink()

time.sleep(1)

# Start communication with server
wcapi.startServerLink()

# Request the the control token (only one client can have the control)
wcapi.requestToken()

#------------------------------------------------------------------------------
# EXAMPLE
#------------------------------------------------------------------------------

# Enable RPM counting at the boards
#wcapi.startRPMFeature()
#time.sleep(5)

wcapi.startLogOBC()

# Start a single Power Supply Unit (PSU)
wcapi.startPSUs()
time.sleep(1)

#start all fans t0 10%
wcapi.setPWM(10)
time.sleep(1)

t_start = time.time()
while time.time()-t_start < 10:
	#print wcapi.rpmVSpwm(fan_layer=0, acc_range=0.6)
	time.sleep(1)

wcapi.stopLogOBC()

#------------------------------------------------------------------------------
# PROPERLY STOP APP
#------------------------------------------------------------------------------
wcapi.shutdown()

# Release the token 
# (will be released automatically if the app is closed)
wcapi.releaseToken()

# Terminate the communication threads 
# (will be terminated automatically if the app is closed)
wcapi.stopServerLink()


