import os, sys, logging
logging.basicConfig(stream=sys.stderr)

if os.name == 'posix':
	PROJECT_DIR = '/usr/local/lib/python2.7/dist-packages/DreamScreenWeatherApp'
else:
	PROJECT_DIR = 'c:/Python27/Lib/site-packages/DreamScreenWeatherApp'

sys.path.append(PROJECT_DIR)
from service import app as application
