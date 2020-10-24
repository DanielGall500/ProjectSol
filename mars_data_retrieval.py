import pandas as pd
import requests 
import os 
import json
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import numpy as np 
import enum
import sys 


"""
Atmospheric Temperature AT:
	- av
	- ct
	- mn
	- mx

Horizontal Wind Speed HWS:
	- av
	- ct
	- mn
	- mx

Atmospheric Pressure PRE:
	- av
	- ct
	- mn
	- mx

Wind Direction WD:
	- <compass_pt_no>
		- compass_degrees 
		- compass_point 
		- compass_right
		- compass_up 
		- ct

	- most_common 
		- compass_degrees 
		- compass_point 
		- compass_right
		- compass_up 
		- ct

Validity Checks (validity_checks):
	- <SOL>
		- AT
			- sol_hours_with_data
			- valid
		- HWS
			- sol_hours_with_data
			- valid
		- PRE
			- sol_hours_with_data
			- valid
		- WD
			- sol_hours_with_data
			- valid
	- sol_hours_required
	- sols_checked

Season
Time Of First Datum: First_UTC (UTC; YYYY-MM-DDTHH:MM:SSZ)
Time Of Last Datum: Last_UTC (UTC; YYYY-MM-DDTHH:MM:SSZ)
"""


dataframes = {}

def save_data(name, rows, columns):
	df = pd.DataFrame(data=rows, columns=columns)
	dataframes[name] = df

sets = {}
set_ids = ["AT", "HWS", "WD", "PRE"]

class Datasets(enum.Enum):
	Temp = 0
	W_Speed = 1
	W_Dir = 2
	Pressure = 3

for i,ele in enumerate(set_ids):
	sets[Datasets(i)] = ele


def get_set_id(ds):
	return sets[ds]

def get_set(sol, ds):
	set_id = get_set_id(ds)
	return data[sol][set_id]

def add_sol_id(ds, sol):
	ds["sol_id"] = sol

def add_ordinal_id(ds, ordinal):
	ds["ordinal"] = ordinal


def order_row(ds, col_order):
	final_set = []
	for col in col_order:
		nxt_col = ds[col]
		final_set.append(nxt_col)
	return final_set



def successful_response(response):
	return (response.status_code is 200)

def save_response(response, to_file):
	with open(to_file, "w") as f:
		for chunk in resp.iter_content(chunk_size=128):
			f.write(chunk)


save_data_file_name = "mars_data.json"
save_data_file_path = "%s/%s" % (os.getcwd(), save_data_file_name)

#NASA URL & Parameters 
url = 'https://api.nasa.gov/insight_weather/'
api_key = "fkkjfgveRAJ2BOVq7gaUAbBbM8omgKo0IRaDEGTj"
feedtype = "json"
ver = "1.0"

#Set Parameters
params = dict(api_key=api_key,
			feedtype=feedtype,
			ver=ver)

#Retrieve Data
resp = requests.get(url=url, params=params)

#Convert To JSON Format
data = resp.json()

#Was Data Retrieval Successful?
successful_resp = successful_response(resp)
save_response(resp, save_data_file_path)

#Create A Dataframe

#DB: Sols
sols_per_week = 7
sol_ids = range(0,sols_per_week)
days_into_year = data["sol_keys"]

db_Sols_r = zip(sol_ids, days_into_year)
db_Sols_c = ["sol_id", "days_into_year"]

save_data("SOLS", db_Sols_r, db_Sols_c)

def get_sol_day(sol_id):
	return dataframes["SOLS"]

def organise_std_data(ds_id):
	db_rows = []
	db_cols = ["sol_id", "av", "mn", "mx", "ct"]

	for sol in sol_ids:
		day_of_year = days_into_year[sol]

		#Retrieve & Customise Row
		ds = get_set(day_of_year, ds_id)
		add_sol_id(ds, sol)

		#Ensure row is in the correct order
		ordered_row = order_row(ds, db_cols)
		db_rows.append(ordered_row)

	return db_rows, db_cols

#Atmospheric Temperature
atm_temp_rows, atm_temp_cols = organise_std_data(Datasets.Temp)
save_data("TEMP", atm_temp_rows, atm_temp_cols)

#Wind Speed
wspeed_rows, wspeed_cols = organise_std_data(Datasets.W_Speed)
save_data("WSPEED", wspeed_rows, wspeed_cols)

#Atmospheric Pressure
pre_rows, pre_cols = organise_std_data(Datasets.Pressure)
save_data("PRESSURE", pre_rows, pre_cols)

#Wind Direction: Ordinals
#Relation Key: {sol_id, ordinal}
wd_rows = []
wd_cols = ["sol_id", "ordinal", "compass_point", "compass_degrees", "compass_right", "compass_up", "ct"]

for sol in sol_ids:
	day_of_year = days_into_year[sol]

	#All Ordinal Keys 
	ds = get_set(day_of_year, Datasets.W_Dir)
	ordinal_keys = [x for x in ds if x != "most_common"]

	for ordinal in ordinal_keys:
		ds_ord = ds[ordinal]

		add_sol_id(ds_ord, sol)
		add_ordinal_id(ds_ord, ordinal)

		#Ensure row is in the correct order
		ordered_row = order_row(ds_ord, wd_cols)
		wd_rows.append(ordered_row)

save_data("WIND_DIRECTION", wd_rows, wd_cols)

#Wind Direction: Most Common
wd_com_rows = []
wd_com_cols = ["sol_id", "compass_point", "compass_degrees", "compass_right", "compass_up", "ct"]

for sol in sol_ids:
	day_of_year = days_into_year[sol]
	ds = get_set(day_of_year, Datasets.W_Dir)["most_common"]

	add_sol_id(ds, sol)

	ordered_row = order_row(ds, wd_com_cols)
	wd_com_rows.append(ordered_row)

save_data("WIND_DIR_MOST_COMMON", wd_com_rows, wd_com_cols)



















