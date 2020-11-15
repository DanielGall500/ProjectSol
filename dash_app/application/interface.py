from data_collector import DataCollector
from data_manager import DBManager

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
tbl_id = db_manager.get_tbl_id(DBManager.Table.Temp)
tbl = db_manager.get_table(tbl_id)

print (tbl)















