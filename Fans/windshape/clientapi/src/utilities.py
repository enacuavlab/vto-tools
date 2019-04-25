"""
Copyright (C) WindShape LLC - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential. 
                     _ _ _ _       _ _____ _               
                    | | | |_|___ _| |   __| |_ ___ ___ ___  
                    | | | | |   | . |__   |   | .'| . | -_| 
                    |_____|_|_|_|___|_____|_|_|__,|  _|___| 
                                                  |_|        
 
WindShape LLC, Geneva, February 2019 

Developer team:
	Guillaume Catry <guillaume.catry@windshape.ch>
	Nicolas Bosson <nicolas.bosson@windshape.ch>

Contributors:
	Adrien Fleury, Alejandro Stefan Zavala, Federico Conzelmann
"""

import re

def ignoreComments(line, keep_space):
		#print("Before : " + line)
		# Remove everything that is written after "#" or "//" or "$" character (comments)
		line = line.split("#")[0]
		line = line.split("//")[0]
		#line = line.split("$")[0]

		# Remove special characters
		if keep_space == 0:
			line = re.sub('[\t!@#\0\\n ]','',line)

		elif keep_space == 1:
			line = re.sub('[\t!@#\0\n]','',line)

		line = line.strip()

		#print("After : " + line)
		return line


def formatAttrs(attrs):
	for attr in attrs:
		attr[0] = re.sub('[\t!@#\0\\n ]','',attr[0])
		attr[2] = re.sub('[\t!@#\0\\n ]','',attr[2])
	return attrs

	
def readConfig(conf_path, keyword, keep_space):
	current_keyword = None
	keyword_cher    = "%"
	read_flag = 0

	reads = []

	conf_file =  open(conf_path, "r")
	for i, line in enumerate(conf_file.readlines()):

		line = ignoreComments(line, keep_space)
		
		# Read keyword if any
		if line:
			if line[0] == keyword_cher:
				current_keyword = line[1:]

				if current_keyword == "END" and read_flag == 1:
					break

			# Get
			elif current_keyword == keyword:
				reads.append(line.split(","))
				read_flag = 1

	conf_file.close()

	return reads