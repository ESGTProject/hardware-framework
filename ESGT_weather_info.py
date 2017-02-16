'''
python 2.7.10

Author Boa-Lin Lai

module install (pyowm):

protopye --

resouce from:
  https://github.com/csparpa/pyowm/blob/master/pyowm/docs/usage-examples.md
  http://openweathermap.org/

'''
import datetime
import json
from urllib2 import urlopen


class ESGT_weather_info:
    def __init__(self):
    # use Atlanta as default
      self.api_key = 'cca7a9afe7f521c4228b4071ea77e58e'
      self.city_id = '4180439'
      self.current_weather_api = 'http://api.openweathermap.org/data/2.5/weather?id='    
      self.forecast_weather_api = 'http://api.openweathermap.org/data/2.5/forecast?id='
    def time_converter(self, time):
      converted_time = datetime.datetime.fromtimestamp(
          int(time)
      ).strftime('%I:%M %p')
      return converted_time

    def url_builder(self, api):
      '''
        current weather url builder, use differt api data 
      '''
      unit = 'imperial'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
      # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz
      full_api_url = api + str(self.city_id) + '&mode=json&units=' + unit + '&APPID=' + self.api_key
      print full_api_url
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
      current_weather_data = self.data_fetch(self.url_builder(self.current_weather_api))
      forecast_weather_data = self.data_fetch(self.url_builder(self.forecast_weather_api))
      # we only need the first day forcast
      #for day in forecast_weather_data: # the first day dat
      #  # is day a dictonary?
      day_list =  forecast_weather_data['list'][:8]
      #day_data = json.loads(forecast_weather_data['list'])
      for l in day_list:
        print 1
      data = self.data_organizer(current_weather_data,forecast_weather_data)
      json_array = json.dumps(data)
      print json_array
      return json_array

    def data_organizer(self,raw_current_api_dict,raw_forecast_api_dict):
        '''
          This part revised the dictonary content
        '''
        data = dict(
          city=raw_current_api_dict.get('name'), # same
          country=raw_current_api_dict.get('sys').get('country'),
          temp=raw_current_api_dict.get('main').get('temp'),
          temp_max=raw_current_api_dict.get('main').get('temp_max'),
          temp_min=raw_current_api_dict.get('main').get('temp_min'),
          humidity=raw_current_api_dict.get('main').get('humidity'),
          pressure=raw_current_api_dict.get('main').get('pressure'),
          sky=raw_current_api_dict['weather'][0]['main'],
          sunrise=self.time_converter(raw_current_api_dict.get('sys').get('sunrise')),
          sunset=self.time_converter(raw_current_api_dict.get('sys').get('sunset')),
          wind=raw_current_api_dict.get('wind').get('speed'),
          wind_deg=raw_current_api_dict.get('deg'),
          dt=self.time_converter(raw_current_api_dict.get('dt')),
          cloudiness=raw_current_api_dict.get('clouds').get('all')
        )
        return data
def data_output(data):
    m_symbol = '\xb0' + 'C'
    print('---------------------------------------')
    print('Current weather in: {}, {}:'.format(data['city'], data['country']))
    print(data['temp'], m_symbol, data['sky'])
    print('Max: {}, Min: {}'.format(data['temp_max'], data['temp_min']))
    print('')
    print('Wind Speed: {}, Degree: {}'.format(data['wind'], data['wind_deg']))
    print('Humidity: {}'.format(data['humidity']))
    print('Cloud: {}'.format(data['cloudiness']))
    print('Pressure: {}'.format(data['pressure']))
    print('Sunrise at: {}'.format(data['sunrise']))
    print('Sunset at: {}'.format(data['sunset']))
    print('')
    print('Last update from the server: {}'.format(data['dt']))
    print('---------------------------------------')


if __name__ == '__main__':
    try:
         w = ESGT_weather_info()
         print w.get_json()
    except IOError:
        print('no internet')
