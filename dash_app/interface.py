from data_collector import DataCollector
from data_manager import DBManager
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output 
import plotly.express as px

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
	'y_min': -40,
	'y_max': -80
}

PRE_pref = {
	'y_min' : 700,
	'y_max' : 800
}

HWS_pref = {
	'y_min' : 0,
	'y_max' : 10
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
	mn = prefs['y_min']
	mx = prefs['y_max']

	fig = px.bar(table, x='sol_id', y='av')
	fig.update_yaxes(range=[mn,mx])

	return fig


if __name__ == '__main__':
	app.run_server(debug=True)














