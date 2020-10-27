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

xaxis_title = "Sol (Number Of Days Into A Mars Year)"
yaxis_title = "Temperature (Degrees Celsius)"

line_width = 2
line_colour = "black"

temp_set = get_df(atmospheric_temp_df_key)

sols = get_df(sols_df_key)["days_into_year"]

temp_graph = go.Figure()

def add_connection_lines(graph, data, xaxis_key, min_key, max_key, line_colour, line_width):
	for i,row in data.iterrows():
		graph.add_shape(
			dict(
				type="line",
				x0=row[xaxis_key],
				x1=row[xaxis_key],
				y0=row[min_key],
				y1=row[max_key],
				line=dict(
					color=line_colour,
					width=line_width)
				),
			layer="below"
			)

def update_graph(graph, title, x_title, y_title):
	graph.update_layout(
	title=title, 
	xaxis_title=x_title,
	yaxis_title=y_title,
	xaxis_showgrid=False, 
	yaxis_showgrid=False,
	xaxis_type="category")

def plot_points(xaxis, properties):

	data = properties["data"]
	colour = properties["colour"]
	size = properties["size"]
	name = properties["name"]

	return go.Scatter(x=xaxis,y=data,mode="markers",
		showlegend=True,marker=dict(color=colour,size=size),
		name=name)

def plot_min_max_avg_graph(graph, x_axis, min_properties, avg_properties, max_properties):
	plot_min = plot_points(x_axis, min_properties)
	graph.add_trace(plot_min)

	plot_avg = plot_points(x_axis, avg_properties)
	graph.add_trace(plot_avg)

	plot_max = plot_points(x_axis, max_properties)
	graph.add_trace(plot_max)

min_prop = {
	"data"   : temp_set[min_key],
	"colour" : "darkblue",
	"size"   : 10,
	"name"  : "Minimum Temperature"
}

avg_prop = {
	"data"   : temp_set[avg_key],
	"colour" : "darkorange",
	"size"   : 20,
	"name"  : "Average Temperature"
}

max_prop = {
	"data"   : temp_set[max_key],
	"colour" : "orangered",
	"size"   : 10,
	"name"  : "Maximum Temperature"
}

plot_min_max_avg_graph(temp_graph, sols, min_prop, avg_prop, max_prop)
add_connection_lines(temp_graph, temp_set, sol_key, min_key, max_key, line_colour, line_width)
update_graph(temp_graph, temp_graph_title, xaxis_title, yaxis_title)

#temp_graph.show()

#Atmospheric Pressure
atmospheric_pressure_df_key = "PRESSURE"

pressure_graph_title = "Avg-Min-Max Mars Atmospheric Pressure"

xaxis_title = "Sol (Number Of Days Into A Mars Year)"
yaxis_title = "Pressure (Pascals)"

pressure_set = get_df(atmospheric_pressure_df_key)

sols = get_df(sols_df_key)["days_into_year"]

pressure_graph = go.Figure()

min_prop = {
	"data"   : pressure_set[min_key],
	"colour" : "darkblue",
	"size"   : 10,
	"name"  : "Minimum Pressure"
}

avg_prop = {
	"data"   : pressure_set[avg_key],
	"colour" : "darkorange",
	"size"   : 20,
	"name"  : "Average Pressure"
}

max_prop = {
	"data"   : pressure_set[max_key],
	"colour" : "orangered",
	"size"   : 10,
	"name"  : "Maximum Pressure"
}

plot_min_max_avg_graph(pressure_graph, sols, min_prop, avg_prop, max_prop)
add_connection_lines(pressure_graph, pressure_set, sol_key, min_key, max_key, line_colour, line_width)
update_graph(pressure_graph, pressure_graph_title, xaxis_title, yaxis_title)


#Wind Speed 
#Question why are there NO winds picked up by TWINS?
wspeed_df_key = "WSPEED"

wspeed_graph_title = "Avg-Min-Max Mars Wind Speed"

xaxis_title = "Sol (Number Of Days Into A Mars Year)"
yaxis_title = "Wind Speed (m/s)"

wspeed_set = get_df(wspeed_df_key)

print wspeed_set

sols = get_df(sols_df_key)["days_into_year"]

wspeed_graph = go.Figure()

min_prop = {
	"data"   : wspeed_set[min_key],
	"colour" : "darkblue",
	"size"   : 10,
	"name"  : "Minimum Wind Speed"
}

avg_prop = {
	"data"   : wspeed_set[avg_key],
	"colour" : "darkorange",
	"size"   : 20,
	"name"  : "Average Wind Speed"
}

max_prop = {
	"data"   : wspeed_set[max_key],
	"colour" : "orangered",
	"size"   : 10,
	"name"  : "Maximum Wind Speed"
}

plot_min_max_avg_graph(wspeed_graph, sols, min_prop, avg_prop, max_prop)
add_connection_lines(wspeed_graph, wspeed_set, sol_key, min_key, max_key, line_colour, line_width)
update_graph(wspeed_graph, wspeed_graph_title, xaxis_title, yaxis_title)

wspeed_graph.show()


"""
wdir_set = get_df("WIND_DIRECTION")

first_sol = wdir_set.loc[wdir_set["sol_id"] == 0]
first_sol = first_sol[["compass_point", "ct"]]

order = { "compass_point" : ["N","NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"] }

fig = px.bar_polar(first_sol, theta="compass_point", r="ct", category_orders=order, template="seaborn")
fig.show()
"""




















