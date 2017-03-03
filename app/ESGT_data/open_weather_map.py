'''
python 2.7.10

Author Boa-Lin Lai


protopye --

resouce from:
  http://api.openweathermap.org/data/2.5/weather?id=4180439&mode=json&units=imperial&APPID=
  http://api.openweathermap.org/data/2.5/forecast?id=4180439&mode=json&units=imperial&APPID=
  http://opeinweathermap.org/

'''
import datetime
import json
from urllib2 import urlopen


class OpenWeatherMap:
    def __init__(self, api_key):
    # use Atlanta as default
        self._api_key = api_key
        self._city_id = '4180439'
        self._current_weather_api = 'http://api.openweathermap.org/data/2.5/weather?id='
        self._forecast_weather_api = 'http://api.openweathermap.org/data/2.5/forecast?id='
    def time_converter(self, time):
        converted_time = datetime.datetime.fromtimestamp(
                         int(time)
                         ).strftime('%I:%M %p')
        return converted_time

    def set_city_id(self, new_id):
        self._city_id = new_id
    def set_api_key(self, new_api_key):
        self._api_key = new_api_key
    def url_builder(self, api):
        """
          current weather url builder, use differt api data
        """
        unit = 'imperial'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
        # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz
        full_api_url = api + str(self._city_id) + '&mode=json&units=' + unit + '&APPID=' + self._api_key
        return full_api_url
    def data_fetch(self,full_api_url):
        url = urlopen(full_api_url)
        # output = url.read().decode('utf-8')
        output = url.read()
        raw_api_dict = json.loads(output)
        #raw_api_dict = json.loads(url.read())
        url.close()
        return raw_api_dict
    def get_json(self):
        """
           return json string for database to use
        """
        current_weather_data = self.data_fetch(self.url_builder(self._current_weather_api))
        forecast_weather_data = self.data_fetch(self.url_builder(self._forecast_weather_api))
        # we only need the first day forcast
        data = self.data_organizer(current_weather_data,forecast_weather_data)
        json_array = json.dumps(data)
        return json_array

    def data_organizer(self,raw_current_api_dict,raw_forecast_api_dict):
        '''
          This part revised the dictonary content
        '''
        day_list =  raw_forecast_api_dict['list'][:8]
        temp_max_list = []
        temp_min_list = []
        rain_stat = 0
        for day_dict in day_list:
          # 8 data for a day 24 hrs /3 hrs = 8 data
          temp_max_list.append(day_dict.get('main').get('temp_max'))
          temp_min_list.append(day_dict.get('main').get('temp_min'))
          if(day_dict.get('rain')): rain_stat += day_dict.get('rain').get('3h')
          #potential bug
        data = dict(
          city=raw_current_api_dict.get('name'), # same
          country=raw_current_api_dict.get('sys').get('country'),
          temp=raw_current_api_dict.get('main').get('temp'),
          temp_max=max(temp_max_list),
          temp_min=min(temp_min_list),
          rain = rain_stat,
          humidity=raw_current_api_dict.get('main').get('humidity'),
          pressure=raw_current_api_dict.get('main').get('pressure'),
          sky=raw_current_api_dict['weather'][0]['main'],
          icon=raw_current_api_dict.get('weather')[0].get('icon'),
          sunrise=self.time_converter(raw_current_api_dict.get('sys').get('sunrise')),
          sunset=self.time_converter(raw_current_api_dict.get('sys').get('sunset')),
          wind=raw_current_api_dict.get('wind').get('speed'),
          wind_deg=raw_current_api_dict.get('deg'),
          dt=self.time_converter(raw_current_api_dict.get('dt')),
          cloudiness=raw_current_api_dict.get('clouds').get('all')
        )
        return data

if __name__ == '__main__':
    try:
        w = OpenWeatherMap()
        print w.get_json()
    except IOError:
        print('no internet')
