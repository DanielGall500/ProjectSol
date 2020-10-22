import pandas as pd
import requests 


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

#NASA URL & Parameters 
url = 'https://api.nasa.gov/insight_weather/'
api_key = "fkkjfgveRAJ2BOVq7gaUAbBbM8omgKo0IRaDEGTj"
feedtype = "json"
ver = "1.0"

#Set Parameters
params = dict(api_key=key,
			feedtype=feedtype,
			ver=ver)

#Retrieve Data
resp = requests.get(url=url, params=params)

#Convert To JSON Format
data = resp.json()

#Was Data Retrieval Successful?
successful_resp = successful_response(resp)


















