"""
  main json interface for database
  
  implemented features:
      weather
      sensors

  Boa-Lin Lai

"""

from ESGT_weather_info import ESGT_weather_info
from ESGT_sensor_info import ESGT_sensor_info
class ESGT_json(object):
    def __init__(self):
        self._weather =  ESGT_weather_info()
        self._sensor = ESGT_sensor_info()
    def get_weather_json(self):
        return self._weather.get_json()
    def get_weather_json_by_city_id(self, city_id):
        self._weather.set_city_id(city_id)
        return self._weather.get_json()
    #def get_sensor_json(self):
    #def get_sensor_json_by_name(self, name):
if __name__ == '__main__':
    try:
        json_data = ESGT_json()
        print json_data.get_weather_json()
        print json_data.get_weather_json_by_city_id(1668341) # Taipei, TW
    except IOError:
        print('no internet')
