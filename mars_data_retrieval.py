import pandas as pd
import requests 
import os 
import json
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import numpy as np 


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

def successful_response(response):
	return (response.status_code is 200)

def save_response(response, to_file):
	with open(to_file, "w") as f:
		for chunk in resp.iter_content(chunk_size=128):
			f.write(chunk)

dataframes = {}

def save_data(name, rows, columns):
	df = pd.DataFrame(data=rows, columns=columns)
	dataframes[name] = df



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

#Atmospheric Temperature

atm_temp = [data[sol]["AT"] for sol in sols]
atm_temp_df = pd.DataFrame(atm_temp)

atm_temp_df.insert(0, "sol_id", sols)

mars_dfs["AT"] = atm_temp_df

#Horizontal Wind Speed
hws = [data[sol]["HWS"] for sol in sols]
hws_df = pd.DataFrame(hws)
mars_dfs["HWS"] = hws_df


#Atmospheric Pressure
atm_pre = [data[sol]["PRE"] for sol in sols]
pre_df = pd.DataFrame(atm_pre)
mars_dfs["PRE"] = pre_df

#Wind Direction

wd_pt_cols = ["compass_degrees", "compass_point", "compass_right", "compass_up", "ct"]

wd_options = [str(x) for x in data[sol]["WD"] if x is not "most_common"]


#WD: Most Common
wd_most_common = [[data[s]["WD"]["most_common"][k] for k in wd_pt_cols] for s in sols]
df_wd_most_common = pd.DataFrame(wd_most_common)

mars_dfs["WD"] = {}
mars_dfs["WD"]["most_common"] = df_wd_most_common

#WD: Rose Axes
rose_axes_dict = {}
axis_dict = {}

for sol in sols:
	sol_list = []
	for axis in wd_options:
		try:
			axis_data = data[sol]["WD"][axis]
			axis_data["ax"] = axis
			sol_list.append(axis_data)
		except KeyError:
			continue

	rose_axes_dict[sol] = pd.DataFrame(sol_list)
mars_dfs["WD"] = rose_axes_dict

AT = mars_dfs["AT"]

print AT





















