import os

INSTALL_DIR='c:/DreamScreenWeatherApp'

os.mkdir(INSTALL_DIR)
os.mkdir(INSTALL_DIR + '/instance')
os.mkdir(INSTALL_DIR + '/logs')
with open(INSTALL_DIR + '/instance/weatherservice-config.py','w') as config_data:
   config_data.write("QUERY_URL='http://www.wunderground.com/weather-forecast/zmw:10308.1.99999'")
   
with open(INSTALL_DIR + '/start_service.bat', 'w') as start_script:
   start_script.write("python -m DreamScreenWeatherApp.service")
   
