# This is where SQL queries are written
import MySQLdb


def openDb(db_access):
	
	# Connect to local MySQL database
	con = MySQLdb.connect(host = db_access[0],    # your host, usually localhost
	                 	  user = db_access[1],         # your username
	                      passwd = db_access[2],  # your password
	                      db = db_access[3])

	cur = con.cursor()
	return con, cur


def createTable(con, cur, table, columns):
	"""
	Create a table "table" in the given database. If it already exists, first drops the table
	"""
	drop_cmd = 'DROP TABLE IF EXISTS ' + str(table).strip() + ';'

	rows_str = ""
	for line in columns:
		rows_str += str(line[0]) + " " + str(line[1]) + ", "

	rows_str = rows_str[:-2]

	create_cmd = 'CREATE TABLE ' + str(table).strip() + ' (' + rows_str +');'
	with con:
		cur.execute(drop_cmd)
		cur.execute(create_cmd)


def populateTable(con, cur, table, columns, values):
	populate_cmd = 'INSERT INTO ' + str(table).strip() + ' (' + str(columns).strip() + ') VALUES (' + str(values).strip() + ');'
	with con:
		cur.execute(populate_cmd)


def setAllValues(con, cur, table, columns, values):
	set_cmd = 'UPDATE ' + str(table).strip() +' SET ' + str(columns).strip() + ' = ' + str(values).strip() + ';'

	with con:
		cur.execute(set_cmd)


def updateModules(con, cur, facility):
	if len(facility.fan_walls[0].modules) > 0:
		attr_names = [item[0] for item in facility.fan_walls[0].module_attrs]
		#attr_types = [item[2] for item in facility.fan_walls[0].module_attrs]

		module_attrs_str = str(", ".join(attr_names))

		table = []
		for module in facility.fan_walls[0].modules_flat:
			value = []
			for attr in module.attrs:
				v = module.getAttributeValue(attr[0])
				
				if attr[2] == "str":
					l = len(v)
					if l == 0:
						value.append('NULL')

					else:
						value.append("\'" + v + "\'")

				elif attr[2] == "bool":
					if v == False:
						value.append(str(0))
					else:
						value.append(str(1))

				else:
					value.append(str(v))


			value_str = '('
			value_str += str(", ".join(value))
			value_str += ')'

			table.append(value_str)
		table_str = str(", ".join(table))


		update = []
		for attr in facility.fan_walls[0].module_attrs[1:]:
			line = '%s = VALUES(%s)' % (attr[0], attr[0])
			update.append(line)

		update_str = str(", ".join(update))

		bertha = """INSERT INTO modules (%s) VALUES  %s ON DUPLICATE KEY UPDATE %s;""" % (module_attrs_str, table_str, update_str)

		with con:
			cur.execute(bertha)


def updateSensors(con, cur, facility):
	if len(facility.sensors) > 0:
		attr_names = [item[0] for item in facility.sensor_attrs]
		#attr_types = [item[2] for item in facility.sensor_attrs]

		sensor_attrs_str = str(", ".join(attr_names))

		table = []
		for sensor in facility.sensors:
			value = []
			for attr in sensor.attrs:
				v = sensor.getAttributeValue(attr[0])

				if attr[2] == "str":
					l = len(v)
					if l == 0:
						value.append('NULL')

					else:
						value.append("\'" + v + "\'")

				elif attr[2] == "bool":
					if v == False:
						value.append(str(0))
					else:
						value.append(str(1))

				else:
					value.append(str(v))


			value_str = '('
			value_str += str(", ".join(value))
			value_str += ')'

			table.append(value_str)
		table_str = str(", ".join(table))


		update = []
		for attr in facility.sensor_attrs[1:]:
			line = '%s = VALUES(%s)' % (attr[0], attr[0])
			update.append(line)

		update_str = str(", ".join(update))

	
		bertha = """INSERT INTO sensors (%s) VALUES  %s ON DUPLICATE KEY UPDATE %s;""" % (sensor_attrs_str, table_str, update_str)

		with con:
			cur.execute(bertha)


def updateControl(con, cur, facility):
	if facility.control_panel != None:
		attr_names = [item[0] for item in facility.control_panel_attrs]
		attr_types = [item[2] for item in facility.control_panel_attrs]

		control_attrs_str = str(", ".join(attr_names))

		table = []
		if facility.control_panel != None:
			value = []
			for attr in facility.control_panel_attrs:
				v = facility.control_panel.getAttributeValue(attr[0])

				if attr[2] == "str":
					l = len(v)
					if l == 0:
						value.append('NULL')

					else:
						value.append("\'" + v + "\'")

				elif attr[2] == "bool":
					if v == False:
						value.append(str(0))
					else:
						value.append(str(1))

				else:
					value.append(str(v))


			value_str = '('
			value_str += str(", ".join(value))
			value_str += ')'

			table.append(value_str)
		table_str = str(", ".join(table))


		update = []
		for attr in facility.control_panel_attrs[1:]:
			line = '%s = VALUES(%s)' % (attr[0], attr[0])
			update.append(line)

		update_str = str(", ".join(update))

		bertha = """INSERT INTO control (%s) VALUES  %s ON DUPLICATE KEY UPDATE %s;""" % (control_attrs_str, table_str, update_str)

		with con:
			cur.execute(bertha)







