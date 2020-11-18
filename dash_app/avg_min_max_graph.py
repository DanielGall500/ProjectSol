import plotly.express as px
import plotly.graph_objects as go 

class AvgMinMaxGraph:

	graph = go.Figure()

	line_width = 2
	line_colour = "black"

	#Key For Each Attribute
	min_key = "mn"
	avg_key = "av"
	max_key = "mx"
	sol_key = "sol_id"

	#Minimum Attribute Properties
	min_prop = {
		"colour" : "darkblue",
		"size"   : 10,
		"name"  : "Minimum Temperature"
	}

	#Average Attribute Properties
	avg_prop = {
		"colour" : "darkorange",
		"size"   : 20,
		"name"  : "Average Temperature"
	}

	#Maximum Attribute Properties
	max_prop = {
		"colour" : "orangered",
		"size"   : 10,
		"name"  : "Maximum Temperature"
	}

	def __init__(self):
		return None

	def create(self, data, title, x_title, y_title):

		self.graph = go.Figure()

		sol_key = 'sol_id'
		sols = [str(x) for x in data[sol_key]]

		self.__plot_min_max_avg_graph(sols, data)

		self.__add_connection_lines(data, sol_key)

		self.__give_titles(title, x_title, y_title)

		return self.graph


	#Plot multiple scatter plots for minimum, average and maximum
	def __plot_min_max_avg_graph(self, x_axis, data):
		plot_min = self.__plot_points(x_axis, data[self.min_key], self.min_prop)
		self.graph.add_trace(plot_min)

		plot_avg = self.__plot_points(x_axis, data[self.avg_key], self.avg_prop)
		self.graph.add_trace(plot_avg)

		plot_max = self.__plot_points(x_axis, data[self.max_key], self.max_prop)
		self.graph.add_trace(plot_max)

	#Update the preferences for your graph
	def __give_titles(self, title, x_title, y_title):
		self.graph.update_layout(
		title=title, 
		xaxis_title=x_title,
		yaxis_title=y_title,
		xaxis_showgrid=False, 
		yaxis_showgrid=False,
		xaxis_type="category")

	#Draw lines between the min,average and maximum
	def __add_connection_lines(self, data, xaxis_key):
		for i,row in data.iterrows():
			print ("--{},{}".format(i,row[xaxis_key]))
			self.graph.add_shape(
				dict(
					type="line",
					x0=i,
					x1=i,
					y0=row[self.min_key],
					y1=row[self.max_key],
					line=dict(
						color=self.line_colour,
						width=self.line_width)
					),
				layer="below"
				)

	#Plot points on a scatter plot
	def __plot_points(self, x_axis, data, properties):
		colour = properties["colour"]
		size = properties["size"]
		name = properties["name"]

		return go.Scatter(x=x_axis,y=data,mode="markers",
			showlegend=True,marker=dict(color=colour,size=size),
			name=name)
