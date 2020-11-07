import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import enum
import requests
from dash.dependencies import Input,Output
import dash_bootstrap_components as dbc

#URL & Parameters 
url = 'https://api.nasa.gov/insight_weather/'
api_key = "fkkjfgveRAJ2BOVq7gaUAbBbM8omgKo0IRaDEGTj"
feedtype = "json"
ver = "1.0"

#Store these parameters in their own dictionary
params = dict(api_key=api_key, feedtype=feedtype, ver=ver)

def is_successful(response):
	return response.ok

#Send out our request and save the response
resp = requests.get(url=url, params=params)

#Ensure the response is what we're looking for
request_successful = is_successful(resp)
print ("Request Successful: %s" % (request_successful))

#The full URL that we retrieved the data from
url = resp.url

#The encoding of the information sent to us
enc = resp.encoding

#The time from first sending the request to receiving a response
time_elapsed = resp.elapsed

#The beginning of the data we've received 
start_of_data = resp.text[:200]

print ("URL: %s \n\nEncoding: %s \n\nTime Elapsed: %s \n\nBeginning Of Data:\n%s" %
      (url, enc, time_elapsed, start_of_data))

data = resp.json()
print ("Type: %s" % (type(data)))

def save_to_json_file(response, to_file):
	with open(to_file, "wb") as f:
		for chunk in response.iter_content(chunk_size=128):
			f.write(chunk) 
		f.close()
        
json_file = "./json_storage/insight_data_storage.json"
save_to_json_file(resp, json_file) 


import json

previously_stored_json_path = "./json_storage/previously_stored_mars_data.json"

with open(previously_stored_json_path) as json_file:
    data = json.load(json_file)


data_attributes = []

for i,attr in enumerate(data):
    data_attributes.append(attr)
    print ("Attribute %d: %s" % (i+1,attr))


#First, we'll save all Sols into a list
sols = data["sol_keys"]

#Choose the first sol as our example
example_sol = sols[0]
example_sol_data = data[example_sol]

print("Example Sol: %s\n" % (example_sol))

sol_attributes = []
for i,attr in enumerate(example_sol_data):
    sol_attributes.append(attr)
    print ("Attribute %d: %s" % (i+1,attr))




#Store our validity data
validity_data = data["validity_checks"]

#Example Sol's Validity Checks 
example_validity = validity_data[example_sol]

#We only require validation for the sensors onboard.
sensors = ["PRE","AT","HWS","WD"]

#Iterate Through The Validity Checks Of Each Sensor
for i,sensor in enumerate(sensors):
    print ("Inspecting Validity Attributes Of %s" % (sensor))
    
    for attr in example_validity[sensor]:
        print ("Attribute: %s" % (attr))
    print('\n')



for sol in sols:
    validity = validity_data[sol]
    
    print("\nNext Sol: %s" % (sol))
    
    for sensor in sensors:
        is_valid = validity[sensor]["valid"]
        
        print("Validity of %s For Sol %s: %s" % (sensor,sol, is_valid))


#Remove Validity Checks & Sol Keys
data.pop("validity_checks", None)

#Remove Time Information
for sol in sols:
    data[sol].pop("First_UTC", None)
    data[sol].pop("Last_UTC", None)
    
    data[sol]["WD"].pop("most_common")



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

def get_tbl_id(table):
    return table_ref[table]



import pandas as pd
import sqlite3 as sql

def connect_to_db(name):
    return sql.connect("db/" + table_name)

#Save a table to the relational database
def save_data(name, rows, columns):
    db_conn = connect_to_db(name)
    df = pd.DataFrame(data=rows, columns=columns)
    df.to_sql(name,db_conn,index=False,if_exists='replace')
    db_conn.close()

#Retrieve an entire table from the database
def get_table(tbl):
    db_conn = connect_to_db(tbl)
    sql_cmd = "SELECT * FROM %s" % (tbl)
    df = pd.read_sql(sql_cmd,db_conn)
    db_conn.close()
    return df

#Execute a custom SQL query on a table
def query_table(tbl,query):
    db_conn = connect_to_db(tbl)
    cur = db_conn.cursor()
    exe = cur.execute(query)
    rows = [row for row in exe]
    db_conn.close()
    return rows



"""
Sols Table
Name: SOLS
2 Attributes: Unique Sol ID | Number of Days into the Year
"""
table_name = get_tbl_id(Table.Sols)

#The data we're already given about sols
days_into_year = data["sol_keys"]

#Unique Sol ID: Starting from 0
unique_ids = [i for i in range(0,len(days_into_year))]

#Attach our two rows together
rows = zip(unique_ids, days_into_year)

#Create the columns
cols = ["sol_id", "days_into_year"]

#Save our data to our relational database
save_data(table_name, rows, cols)

get_table(table_name)




#Last seven days on Mars
recent_sols = get_table(get_tbl_id(Table.Sols))["sol_id"]

#Convert Sol ID => Day Of The Year
def id_to_sol(sol_id):
    query = "SELECT days_into_year FROM Sols WHERE sol_id=%s" % (sol_id)
    tbl = "Sols"
    return str(query_table(tbl,query)[0][0])

def structure_sensor_data(sensor_id, recent_sols):
    sensor_rows = []
    sensor_cols = ["sol_id", "av", "mn", "mx", "ct"]
    
    for sol_id in recent_sols:
        day = id_to_sol(sol_id)
        
		#Retrieve Sensor Data For Day x
        sensor_row = data[day][sensor_id]
        
        #Add the Sol ID to the row
        sensor_row["sol_id"] = sol_id
        
        sensor_rows.append(sensor_row)

    return sensor_rows, sensor_cols



#Atmospheric Temperature
table_id = get_tbl_id(Table.Temp)
atm_temp_rows, atm_temp_cols = structure_sensor_data(table_id,recent_sols)
save_data(table_id, atm_temp_rows, atm_temp_cols)

#Wind Speed
table_id = get_tbl_id(Table.W_Speed)
wspeed_rows, wspeed_cols = structure_sensor_data(table_id, recent_sols)
save_data(table_id, wspeed_rows, wspeed_cols)

#Atmospheric Pressure
table_id = get_tbl_id(Table.Pressure)
pre_rows, pre_cols = structure_sensor_data(table_id,recent_sols)
save_data(table_id, pre_rows, pre_cols)

#View Our Tables
print(get_table(get_tbl_id(Table.Temp)))
print(get_table(get_tbl_id(Table.W_Speed)))
print(get_table(get_tbl_id(Table.Pressure)))



#Wind Direction: Ordinals
#Relation Key: {sol_id, ordinal_id}

table_id = get_tbl_id(Table.W_Dir)

wd_rows = []

"""
The columns for this table will be
very different to the other tables.
"""
wd_cols = ["sol_id", "ordinal_id", "compass_point", "compass_degrees", 
"compass_right", "compass_up", "ct"]

for sol in recent_sols:
    day = id_to_sol(sol)

    #Get all of our compass data for that day 
    ds = data[day]["WD"]
    ordinals = ds.keys()

    #For each direction on a wind rose
    for ordinal in ordinals:
        #Row for Day x, Ordinal y
        next_row = ds[ordinal]
        
        #Super Key: { sol_id, ordinal_id }
        next_row["sol_id"] = sol
        next_row["ordinal_id"] = ordinal

        wd_rows.append(next_row)

save_data(table_id, wd_rows, wd_cols)


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

temp_set = get_table(get_tbl_id(Table.Temp))

sols = get_table(get_tbl_id(Table.Sols))["days_into_year"]

fig = go.Figure()

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

plot_min_max_avg_graph(fig, sols, min_prop, avg_prop, max_prop)
add_connection_lines(fig, temp_set, sol_key, min_key, max_key, line_colour, line_width)
update_graph(fig, temp_graph_title, xaxis_title, yaxis_title)


#Wind Rose
wind_rose_fig = go.Figure()

wdir_set = get_table(get_tbl_id(Table.W_Dir))

first_sol = wdir_set.loc[wdir_set["sol_id"] == 0]
first_sol = first_sol[["compass_point", "ct"]]

order = { "compass_point" : ["N","NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"] }

wind_rose_fig = px.bar_polar(first_sol, theta="compass_point", r="ct", category_orders=order, template="seaborn")



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

temp_table = get_tbl_id(Table.Temp)
at_tmp = get_table(temp_table)

app.layout = html.Div(children=[
	html.H1(children='The Mars InSight Lander',
		style = {
		'textAlign' : 'center'
		}),

	html.H2(children='A Live Data Display',
		style = {
		'textAlign' : 'center'
		}),

	
	dcc.Interval(id="year_progress",n_intervals=0,interval=669),
	dbc.Progress(id="progress"),


	html.Label('Graph'),
	dcc.Dropdown(
		id='dropdown',
		options=[
		{'label' : 'Atmospheric Temperature', 'value' : 'AT'},
		{'label' : 'Atmospheric Pressure', 'value' : 'PRE'},
		{'label' : 'Wind Speed', 'value' : 'HWS'}
		],
		value='AT',
		multi=False),

	dcc.Graph(
		id='example_graph',
		figure=fig),

	dcc.Slider(
		id='wind_rose_slider',
		min=0,
		max=6,
		value=0),

	dcc.Graph(
		id='wind_rose',
		figure=wind_rose_fig)
	])

@app.callback(
	Output('example_graph', 'figure'),
	[Input('dropdown', 'value')])
def update_figure(option):
	fig = go.Figure()
	temp_set = get_table(option)
	sols = get_table(get_tbl_id(Table.Sols))["days_into_year"]

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

	plot_min_max_avg_graph(fig, sols, min_prop, avg_prop, max_prop)
	add_connection_lines(fig, temp_set, sol_key, min_key, max_key, line_colour, line_width)
	update_graph(fig, option, xaxis_title, yaxis_title)

	return fig

@app.callback(
	Output('wind_rose','figure'),
	[Input('wind_rose_slider','value')])
def update_wind_rose(value):
	wind_rose_fig = go.Figure()

	wdir_set = get_table(get_tbl_id(Table.W_Dir))

	first_sol = wdir_set.loc[wdir_set["sol_id"] == value]
	first_sol = first_sol[["compass_point", "ct"]]

	order = { "compass_point" : ["N","NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"] }

	wind_rose_fig = px.bar_polar(first_sol, theta="compass_point", r="ct", category_orders=order, template="seaborn")

	return wind_rose_fig



if __name__ == '__main__':
	app.run_server(debug=True)

