import os
import csv
import time
import datetime

def log(facility):

	print "[THD INIT] Logging thread started."
	time.sleep(0.01)
	
	directory = ""
	log_files = []
	t_init = 0
	while facility.stop_flag == 0:
		t_start = time.time()

		# Open a new file a write header
		if facility.cmd_logging == True and facility.state_logging == False:
			directory = createLogRepository()
			print "Log rep created", directory
			log_files = createLogFiles(facility, directory)
			t_init = time.time()
			facility.state_logging = True
		
		# This case happens when the logger is open. Add new row to each file
		if facility.cmd_logging == True and facility.state_logging == True:
			logModulesData(facility, log_files, t_init)

		# This case happens when the logger is being closed.
		if facility.cmd_logging == False and facility.state_logging == True:
			stopLogging(facility)

		used = time.time() - t_start
		if used < 1.0/facility.frequency:
			time.sleep(float(1.0/facility.frequency - used))

	print "[THD END] Logging thread ended."
	time.sleep(0.01)


def createLogRepository():
	
	# Get the date
	formated_date = datetime.datetime.today().strftime('%Y-%m-%d')

	# Itterate until valid directory name is found
	i = 0
	directory_valid = False

	abs_path = "/var/www/html"

	# If logs doesn't exist, or is logs exists but is a file, then create a new directory
	if os.path.exists(abs_path+"/logs") == False or os.path.isfile(abs_path+"/logs") == True:
		os.makedirs(abs_path+"/logs")

	current_log_number = 1
	for item in os.listdir(abs_path+"/logs"):
		try: 
			_, log = item.split("_")
			log_number = int(log[3:])
			if log_number >= current_log_number:
				current_log_number = log_number+1
		except:
			pass
	
	directory = abs_path+"/logs/"+str(formated_date)+"_LOG"+str(current_log_number)
	os.makedirs(directory)

	return directory

def createLogFiles(facility, directory):

	log_files = []
	for module in facility.fan_walls[0].modules_flat:
		# Current log file
		log_file = directory+"/module_"+str(module.id)+".csv"
		#module.logFile = logFile  

		headerLines = []
		headerLines.append("Module ID:   "+str(module.id)+"\n")
		headerLines.append("MAC address: "+str(module.mac_addr)+"\n")
		headerLines.append("IP address:  "+str(module.ip_addr)+"\n")
		headerLines.append("Position X:  "+str(module.pos_x)+"\n")
		headerLines.append("Position Y:  "+str(module.pos_y)+"\n")
		headerLines.append("Date:        "+datetime.datetime.today().strftime('%Y-%m-%d')+"\n")
		headerLines.append("Time:        "+datetime.datetime.now().strftime('%H:%M:%S')+"\n")
		#time.strftime('%H:%M:%S', time.gmtime(12345))+"\n")

		pwmstr = ""
		rpmstr = ""
		for i in range(18):
			pwmstr += "pwm"+str(i+1)+", "
			rpmstr += "rpm"+str(i+1)+", "
		pwmstr = pwmstr[:-2]
		rpmstr = rpmstr[:-2]

		headerLines.append("time, is_powered, is_flashing, is_connected, is_rebooting, "+pwmstr+", "+rpmstr+"\n")

		if log_file:
			with open(log_file, 'w') as f:
				for line in headerLines:
					f.write(line)

		log_files.append(log_file)

	
	return log_files

def logModulesData(facility, log_files, t_init):
	for i, module in enumerate(facility.fan_walls[0].modules_flat):
		logstr  = ("%.6f" % (time.time()-t_init))+","
		logstr += str(int(module.state_powered))+","
		logstr += str(int(module.state_flashing))+","
		logstr += str(int(module.is_connected))+","
		logstr += str(int(module.cmd_reboot))+","
		logstr += str(module.getPWMstr())+","
		logstr += str(module.getRPMstr())
		logstr += '\n'
		
		# This way of logging is not optimal. It opens and closes the file every time !!!
		# @TODO Use buffers to store data and only save in the file from time to time.
		if log_files[i]:
			with open(log_files[i], 'a') as f:
				f.write(logstr)

def stopLogging(facility):
	facility.state_logging = False
