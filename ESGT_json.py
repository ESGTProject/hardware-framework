from ESGT_weather_info import ESGT_weather_info
#TODO import the sensor class in here
class ESGT_json(object):
    def __init__(self):
        self._weather =  ESGT_weather_info()
        #TODO get json data for weather
    def get_weather_json(self):
        return self._weather.get_json()
    def get_weather_json_by_city_id(self, city_id):
        self._weather.set_city_id(city_id)
        return self._weather.get_json()
if __name__ == '__main__':
    try:
        json_data = ESGT_json()
        print json_data.get_weather_json()
        print json_data.get_weather_json_by_city_id(1668341) # Taipei, TW
    except IOError:
        print('no internet')
