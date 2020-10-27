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

class Datasets(enum.Enum):
	Temp = 0
	W_Speed = 1
	W_Dir = 2
	Pressure = 3

dataframes = {}
sets = {}
set_ids = ["AT", "HWS", "WD", "PRE"]

for i,ele in enumerate(set_ids):
	sets[Datasets(i)] = ele

def save_data(name, rows, columns):
	df = pd.DataFrame(data=rows, columns=columns)
	dataframes[name] = df

def get_set_id(ds):
	return sets[ds]

def get_set(sol, ds):
	set_id = get_set_id(ds)
	return data[sol][set_id]

def get_df(df_id):
	return dataframes[df_id]

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

def get_sol_day(sol_id):
	return dataframes["SOLS"]

def organise_std_data(ds_id, sol_ids):
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

#DB: Sols
sols_per_week = 7
sol_ids = range(0,sols_per_week)
days_into_year = data["sol_keys"]

db_Sols_r = zip(sol_ids, days_into_year)
db_Sols_c = ["sol_id", "days_into_year"]

save_data("SOLS", db_Sols_r, db_Sols_c)

#Atmospheric Temperature
atm_temp_rows, atm_temp_cols = organise_std_data(Datasets.Temp, sol_ids)
save_data("TEMP", atm_temp_rows, atm_temp_cols)

#Wind Speed
wspeed_rows, wspeed_cols = organise_std_data(Datasets.W_Speed, sol_ids)
save_data("WSPEED", wspeed_rows, wspeed_cols)

#Atmospheric Pressure
pre_rows, pre_cols = organise_std_data(Datasets.Pressure, sol_ids)
save_data("PRESSURE", pre_rows, pre_cols)

#Wind Direction: Ordinals
#Relation Key: {sol_id, ordinal}
wd_rows = []

wd_cols = ["sol_id", "ordinal", 
"compass_point", "compass_degrees", 
"compass_right", "compass_up", "ct"]

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
wd_com_cols = ["sol_id", "compass_point", 
"compass_degrees", "compass_right", "compass_up", "ct"]

#TODO: CLEANING

for sol in sol_ids:
	day_of_year = days_into_year[sol]
	ds = get_set(day_of_year, Datasets.W_Dir)["most_common"]

	add_sol_id(ds, sol)

	ordered_row = order_row(ds, wd_com_cols)
	wd_com_rows.append(ordered_row)

save_data("WIND_DIR_MOST_COMMON", wd_com_rows, wd_com_cols)

#Plotly time!

#Atmospheric Temperature Graph 
sol_key = "sol_id"
min_key = "mn"
max_key = "mx"
avg_key = "av"
atmospheric_temp_df_key = "TEMP"
sols_df_key = "SOLS"

temp_graph_title = "Avg-Min-Max Mars Atmospheric Temperature"

min_temp_colour = "darkblue"
avg_temp_colour = "darkorange"
max_temp_colour = "orangered"

min_temp_title = "Minimum Temperature"
avg_temp_title = "Average Temperature"
max_temp_title = "Maximum Temperature"

xaxis_title = "Sol (Number Of Days Into Mars Year)"
yaxis_title = "Temperature (Degrees Celsius)"

min_temp_size = 10
avg_temp_size = 20
max_temp_size = 10

line_width = 2
line_colour = "black"

def plot_temperatures(sols, temp, colour, line_size, name):
	return go.Scatter(x=sols,y=temp,mode="markers",
		showlegend=True,marker=dict(color=colour,size=line_size),
		name=name)

temp_set = get_df(atmospheric_temp_df_key)

mins = temp_set[min_key]
maxs = temp_set[max_key]
avgs = temp_set[avg_key]

sols = get_df(sols_df_key)["days_into_year"]

temp_graph = go.Figure()

plot_min = plot_temperatures(sols, mins, min_temp_colour, min_temp_size, min_temp_title)
temp_graph.add_trace(plot_min)

plot_avg = plot_temperatures(sols, avgs, avg_temp_colour, avg_temp_size, avg_temp_title)
temp_graph.add_trace(plot_avg)

plot_max = plot_temperatures(sols, maxs, max_temp_colour, max_temp_size, max_temp_title)
temp_graph.add_trace(plot_max)

for i,row in temp_set.iterrows():
	temp_graph.add_shape(
		dict(
			type="line",
			x0=row[sol_key],
			x1=row[sol_key],
			y0=row[min_key],
			y1=row[max_key],
			line=dict(
				color=line_colour,
				width=line_width)
			),
		layer="below"
		)

temp_graph.update_layout(title=temp_graph_title, 
	xaxis_showgrid=False, 
	yaxis_showgrid=False,
	xaxis_title=xaxis_title,
	yaxis_title=yaxis_title,
	xaxis_type="category")

temp_graph.show()

"""
pressure_set = get_df("PRESSURE")

x = pressure_set["sol_id"]
y = pressure_set["av"]

fig = px.bar(x=x,y=y, labels={ 'x' : "Sol", 'y' : "Pressure" }, range_y=[745,755])
fig.show()
"""

"""
wspeed_set = get_df("WSPEED")

x = wspeed_set["sol_id"]
y = wspeed_set["av"]

fig = px.bar(x=x,y=y, labels={ 'x' : "Sol", 'y' : "Wind Speed" })
fig.show()
"""

"""
temp_set = get_df("TEMP")
pressure_set = get_df("PRESSURE")

x = temp_set["av"]
y = pressure_set["av"]

fig = px.line(x=x, y=y, title="Temperature Compared With Atmospheric Pressure")
fig.show()
"""

"""
wdir_set = get_df("WIND_DIRECTION")

first_sol = wdir_set.loc[wdir_set["sol_id"] == 0]
first_sol = first_sol[["compass_point", "ct"]]

order = { "compass_point" : ["N","NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"] }

fig = px.bar_polar(first_sol, theta="compass_point", r="ct", category_orders=order, template="seaborn")
fig.show()
"""




















