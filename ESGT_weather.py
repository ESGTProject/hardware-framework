'''
python 2.7.10

Author Boa-Lin Lai

module install (pyowm):

pip install pyowm

protopye --

resouce from:
  https://github.com/csparpa/pyowm/blob/master/pyowm/docs/usage-examples.md
  http://openweathermap.org/

'''
from pyowm import OWM
class ESGT_weather:
  def __init__(self):
    self.API_key = 'cca7a9afe7f521c4228b4071ea77e58e'
    # now is hardcode, might change later 
    self.owm = OWM(self.API_key)
    self.obs = self.owm.weather_at_id(4180439)
    self.w = self.obs.get_weather()    
    self.l = self.obs.get_location()
    # 4180439 is the city code for Atlanta,GA, will 
  def print_city_info(self):
    '''
      print the info of city to varify the correctnes of data
    ''' 
    print('city name: ' + self.l.get_name())
    print('lon: ' + str(self.l.get_lon()) + ', lat: ' + str(self.l.get_lat()))
  def print_weather_info(self):
    '''
      print the temp and the weather status
    ''' 
    print(self.l.get_name())
    print(self.w.get_detailed_status())
    print('in C: ' + str(self.w.get_temperature(unit='celsius')['temp']))
    print('in F: ' + str(self.w.get_temperature('fahrenheit')['temp']))
if __name__ == '__main__':
  w = ESGT_weather()
  print('test print_weather_info()')
  w.print_weather_info()
  print('test print_city_info()')
  w.print_city_info()
