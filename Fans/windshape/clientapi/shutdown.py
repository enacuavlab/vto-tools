

import src.windControlAPI
import time

#------------------------------------------------------------------------------
# WINDCONTROL APP INITIALIZATION
#------------------------------------------------------------------------------

# Start WindControl App and initiate communication with the server
wcapi = src.windControlAPI.WindControlApp(verbose_comm=True)

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


time.sleep(1)


# Stop all fans
wcapi.setPWM(0)
time.sleep(3)



#------------------------------------------------------------------------------
# PROPERLY STOP APP
#------------------------------------------------------------------------------

wcapi.shutdown()

wcapi.turnComputerOff()
# Release the token 
# (will be released automatically if the app is closed)
wcapi.releaseToken()

# Terminate the communication threads 
# (will be terminated automatically if the app is closed)
wcapi.stopServerLink()


