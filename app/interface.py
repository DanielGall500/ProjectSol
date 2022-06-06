from data_collector import DataCollector
from data_manager import DBManager
from avg_min_max_graph import AvgMinMaxGraph
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output 
import plotly.express as px
import plotly.graph_objects as go 

#URL & Parameters 
url = 'https://api.nasa.gov/insight_weather/'
api_key = "fkkjfgveRAJ2BOVq7gaUAbBbM8omgKo0IRaDEGTj"
feedtype = "json"
ver = "1.0"

json_storage_file = "./json_storage/insight_data_storage.json"

#Store these parameters in their own dictionary
params = dict(api_key=api_key, feedtype=feedtype, ver=ver)

#Collect & Save Data
collector = DataCollector()
response = collector.get(url, params)
collector.save_to_json_file(response, json_storage_file)

#Manage Data
db_manager = DBManager(response)

AT_pref = {
	"title" : "Atmospheric Temperature",
	"x_title" : "Sol",
	"y_title" : "Degrees (Celsius)"
}

PRE_pref = {
	"title" : "Atmospheric Pressure",
	"x_title" : "Sol",
	"y_title" : "Pressure (Pascal)"
}

HWS_pref = {
	"title" : "Wind Speeds",
	"x_title" : "Sol",
	"y_title" : "Wind Speed (m/s)"
}

PREF = {
	'AT' : AT_pref,
	'PRE': PRE_pref,
	'HWS': HWS_pref
}


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

	html.H6("Mars InSight Data Summary"),

	dcc.Dropdown (
		id='data-dropdown',
		options=[
			{'label': 'Atmospheric Temperature', 'value': 'AT'},
            {'label': 'Atmospheric Pressure', 'value': 'PRE'},
            {'label': 'Wind Data', 'value': 'HWS'}
            ],
            value='AT'
        ),

	html.Div(id='output-container'),

	dcc.Graph(id='bar-chart')

	])

@app.callback(
	Output('output-container', 'children'),
	[Input('data-dropdown', 'value')])

def update_output(input_value):
	return 'Output: {}'.format(input_value)

@app.callback(
	Output('bar-chart', 'figure'),
	[Input('data-dropdown', 'value')])

def update_bar(table_id):
	table = db_manager.get_table(table_id)

	prefs = PREF[table_id]

	ttl = prefs["title"]
	x_ttl = prefs["x_title"]
	y_ttl = prefs["y_title"]

	sols = [db_manager.id_to_sol(x) for x in table.iloc[:,0]]
	data = table.iloc[:,1:]

	graph_creator = AvgMinMaxGraph()
	graph = graph_creator.create(
		sols, data, ttl, x_ttl, y_ttl)

	return graph


if __name__ == '__main__':
	app.run_server(debug=True)














