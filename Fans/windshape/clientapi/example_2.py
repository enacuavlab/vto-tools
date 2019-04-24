# Start all fans at 

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
wcapi.startRPMFeature()

wcapi.startLogOBC()

# Start a single Power Supply Unit (PSU)
wcapi.startPSUs()
time.sleep(1)

# Start all fans to 10%
wcapi.setPWM(10)

t_start = time.time()
while time.time()-t_start < 20:
	print wcapi.getRPM()
	time.sleep(1)

wcapi.setPWM(0)
time.sleep(3)

wcapi.stopLogOBC()

wcapi.stopRPMFeature()

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


