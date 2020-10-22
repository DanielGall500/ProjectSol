import pandas as pd
import requests 
import os 
import json


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

#df = pd.read_json(save_data_file_path)

mars_dfs = {}

sols = [str(n) for n in data["sol_keys"]]

#Atmospheric Temperature
atm_temp = [data[sol]["AT"] for sol in sols]
atm_temp_df = pd.DataFrame(atm_temp)
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

wd_options = [str(x) for x in data[sol]["WD"]]


#WD: Most Common
wd_most_common = [[data[s]["WD"]["most_common"][k] for k in wd_pt_cols] for s in sols]
df_wd_most_common = pd.DataFrame(wd_most_common)

mars_dfs["WD"] = {}
mars_dfs["WD"]["most_common"] = df_wd_most_common

#WD: 
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
			print ("Null")

	rose_axes_dict[sol] = pd.DataFrame(sol_list)
mars_dfs["WD"] = rose_axes_dict

print mars_dfs["WD"]



"""
wd_compass_pt_no = [[data[sol]["WD"][str(wind_rose_num)] for wind_rose_num in range(1,16)] for sol in sols]

print wd_compass_pt_no

wd_most_common = [data[sol]["WD"]["most_common"] for sol in sols]

wd_dict = {"compass_pt_no" : pd.DataFrame(wd_compass_pt_no),
		"most_common" : d.DataFrame(wd_most_common) }


print wd_df


mars_dfs["WD"] = wd_df
"""



















