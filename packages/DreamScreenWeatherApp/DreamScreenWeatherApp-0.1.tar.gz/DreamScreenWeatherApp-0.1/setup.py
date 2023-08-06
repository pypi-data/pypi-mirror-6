from setuptools import setup, find_packages

package_data_files = [ "*.wsgi", "etc/*", "templates/*", "instance/*", "logs/*" ]
data_files = [ "instance/*", "logs/*", "static/*" ]

setup(name='DreamScreenWeatherApp',
      version='0.1',
      author='John Tashiro',
      author_email='jtashiro@fiospace.com',
      license='GPL',
      description='HP DreamScreen weather data provider',
      packages=['DreamScreenWeatherApp'],
      package_data = {'DreamScreenWeatherApp' : package_data_files },
#      data_files =  ('DreamScreenWeatherApp/instance', ['instance/weatherservice-config.py']),
     )
     