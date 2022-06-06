import pandas as pd
import sqlite3 as sql
import numpy as np
import enum
import sys

class DBManager:

	response = None

	#An enum to reference which table we're referring to
	class Table(enum.Enum):
	    Sols = 0
	    Temp = 1
	    W_Speed = 2
	    W_Dir = 3
	    Pressure = 4
	    
	table_ref = {
	    Table.Sols : "Sols",
	    Table.Temp : "AT",
	    Table.W_Speed : "HWS",
	    Table.W_Dir : "WD",
	    Table.Pressure : "PRE"
	}	

	def __init__(self, response):
		self.response = response

		"""
		Sols Table
		Name: SOLS
		2 Attributes: Unique Sol ID | Number of Days into the Year
		"""
		data = response.json()
		sols = np.array(data["sol_keys"])

		#The data we're already given about sols
		#sols = sols_tbl["sol_keys"]

		#Unique Sol ID: Starting from 0
		#unique_ids = [i for i in range(0,len(num_sols))]
		unique_ids = np.arange(0, len(sols))

		rows = np.dstack((unique_ids,sols))[0]

	
		#Save our data to our relational database
		table_name = "SOLS"
		self.save_data(table_name, rows, ["sol_id","days_into_year"])

		#Atmospheric Temperature
		table_id = self.get_tbl_id(self.Table.Temp)
		atm_temp_rows, atm_temp_cols = self.structure_sensor_data(data,table_id,unique_ids)
		print ("Temp: " + str(len(atm_temp_rows)))
		self.save_data(table_id, atm_temp_rows, atm_temp_cols)

		#Wind Speed
		table_id = self.get_tbl_id(self.Table.W_Speed)
		wspeed_rows, wspeed_cols = self.structure_sensor_data(data,table_id, unique_ids)
		self.save_data(table_id, wspeed_rows, wspeed_cols)

		#Atmospheric Pressure
		table_id = self.get_tbl_id(self.Table.Pressure)
		pre_rows, pre_cols = self.structure_sensor_data(data,table_id,unique_ids)
		self.save_data(table_id, pre_rows, pre_cols)

		#Wind Direction: Ordinals
		#Relation Key: {sol_id, ordinal_id}
		table_id = self.get_tbl_id(self.Table.W_Dir)

		wd_rows = []

		wd_cols = ["sol_id", "ordinal_id", "compass_point", "compass_degrees", 
		"compass_right", "compass_up", "ct"]

		for sol in unique_ids:
		    day = self.id_to_sol(sol)

		    #Get all of our compass data for that day 
		    ds = data[day]["WD"]

		    ordinals = ds.keys()

		    #For each direction on a wind rose
		    for ordinal in ordinals:

		    	next_row = ds[ordinal]

		    	if(next_row is None):
		    		continue

		    	next_row["sol_id"] = sol
		    	next_row["ordinal_id"] = ordinal

		    	wd_rows.append(next_row)

		self.save_data(table_id, wd_rows, wd_cols)

		for sol in data:
			print(sol)


	def connect_to_db(self, name):
	    return sql.connect("db/" + name)

	#Save a table to the relational database
	def save_data(self, name, rows, columns):
	    db_conn = self.connect_to_db("INSIGHT_DATA")
	    df = pd.DataFrame(data=rows, columns=columns)
	    df.to_sql(name,db_conn,index=False,if_exists='replace')
	    db_conn.close()

	    """
	    db_conn = self.connect_to_db("INSIGHT_DATA")
	    sql_cmd = "SELECT * FROM %s" % (name)
	    df = pd.read_sql(sql_cmd, db_conn)
	    print ("DF: " + df)
	    """

	def get_tbl_id(self, table):
	    return self.table_ref[table]

	#Retrieve an entire table from the database
	def get_table(self, tbl):
	    db_conn = self.connect_to_db("INSIGHT_DATA")
	    sql_cmd = "SELECT * FROM %s" % (tbl)
	    df = pd.read_sql(sql_cmd,db_conn)
	    db_conn.close()
	    return df

	#Execute a custom SQL query on a table
	def query_table(self, tbl,query):
	    db_conn = self.connect_to_db(tbl)
	    cur = db_conn.cursor()
	    exe = cur.execute(query)
	    rows = [row for row in exe]
	    db_conn.close()
	    return rows

	#Convert Sol ID => Day Of The Year
	def id_to_sol(self, sol_id):
	    query = "SELECT days_into_year FROM Sols WHERE sol_id=%s" % (sol_id)
	    tbl = "INSIGHT_DATA"
	    return str(self.query_table(tbl,query)[0][0])

	def structure_sensor_data(self, data, sensor_id, recent_sols):
	    sensor_rows = []
	    sensor_cols = ["sol_id", "av", "mn", "mx", "ct"]
	    
	    for sol_id in recent_sols:
	        day = self.id_to_sol(sol_id)

	        print("\n\nSol %s\n\n" % (sol_id))
	        for sensor in data[day]:
	        	print (sensor)

	        if sensor_id in data[day]:
	        	print ("In Data")
	        	sensor_row = data[day][sensor_id]
				#Add the Sol ID to the row
		        sensor_row["sol_id"] = sol_id

		       	print (sensor_row)

		        
		        sensor_rows.append(sensor_row)

	    return sensor_rows, sensor_cols







