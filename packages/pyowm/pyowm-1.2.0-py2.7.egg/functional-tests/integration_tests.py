'''
Functional tests for the PyOWM library
These are "live" executions, that of course need the OWM web API to be up
and running
'''
import unittest
from datetime import datetime
from pyowm import OWM
from xmlrpclib import DateTime

class IntegrationTest(unittest.TestCase):
    
    __API_key = 'b02f5370dfd0f398b5746e1a976021a0'
    __owm = OWM(__API_key)

    def test_weather_at(self):
        """
        Test feature: get currently observed weather at specific location
        """
        o1 = self.__owm.weather_at('London,uk')
        o2 = self.__owm.weather_at('Kiev')
        o3 = self.__owm.weather_at('QmFoPIlbf')  #Shall be None
        self.assertTrue(o1, "")
        self.assertTrue(o1.get_reception_time())
        self.assertTrue(o1.get_location())
        self.assertNotIn(None, o1.get_location().__dict__.values())
        self.assertTrue(o1.get_weather())
        self.assertNotIn(None, o1.get_weather().__dict__.values())
        self.assertTrue(o2)
        self.assertTrue(o2.get_reception_time())
        self.assertTrue(o2.get_location(), "")
        self.assertNotIn(None, o2.get_location().__dict__.values())
        self.assertTrue(o2.get_weather(), "")
        self.assertNotIn(None, o2.get_weather().__dict__.values())
        self.assertFalse(o3)

    def test_weather_at_coords(self):
        """
        Test feature: get currently observed weather at specific coordinates
        """
        o1 = self.__owm.weather_at_coords(12.484589, 41.896144)  #Rome
        o2 = self.__owm.weather_at_coords(18.503723,-33.936524)  #Cape Town
        self.assertTrue(o1)
        self.assertTrue(o1.get_reception_time())
        self.assertTrue(o1.get_location())
        self.assertNotIn(None, o1.get_location().__dict__.values())
        self.assertTrue(o1.get_weather())
        self.assertNotIn(None, o1.get_weather().__dict__.values())
        self.assertTrue(o2)
        self.assertTrue(o2.get_reception_time())
        self.assertTrue(o2.get_location())
        self.assertNotIn(None, o2.get_location().__dict__.values())
        self.assertTrue(o2.get_weather())
        self.assertNotIn(None, o2.get_weather().__dict__.values())
        
    def test_find_weather_by_name(self):
        """
        Test feature: find currently observed weather for locations matching
        the specified text search pattern
        """
        # Test using searchtype=accurate
        o1 = self.__owm.find_weather_by_name("London", "accurate")
        o2 = self.__owm.find_weather_by_name("Paris", "accurate", 2)
        self.assertTrue(isinstance(o1, list))
        for item in o1:
            self.assertTrue(item)
            self.assertTrue(item.get_reception_time())
            self.assertTrue(item.get_location())
            self.assertNotIn(None, item.get_location().__dict__.values())
            self.assertTrue(item.get_weather())
            self.assertNotIn(None, item.get_weather().__dict__.values())
        self.assertTrue(isinstance(o2, list))
        self.assertFalse(len(o2) > 2)
        for item in o2:
            self.assertTrue(item)
            self.assertTrue(item.get_reception_time())
            self.assertTrue(item.get_location())
            self.assertNotIn(None, item.get_location().__dict__.values())
            self.assertTrue(item.get_weather())
            self.assertNotIn(None, item.get_weather().__dict__.values())

        # Test using searchtype=like
        o3 = self.__owm.find_weather_by_name("London", "like")
        o4 = self.__owm.find_weather_by_name("Paris", "like", 2)
        self.assertTrue(isinstance(o3, list))
        for item in o3:
            self.assertTrue(item)
            self.assertTrue(item.get_reception_time())
            self.assertTrue(item.get_location())
            self.assertNotIn(None, item.get_location().__dict__.values())
            self.assertTrue(item.get_weather())
            self.assertNotIn(None, item.get_weather().__dict__.values())
        self.assertTrue(isinstance(o4, list))
        self.assertFalse(len(o4) > 2)
        for item in o4:
            self.assertTrue(item)
            self.assertTrue(item.get_reception_time())
            self.assertTrue(item.get_location())
            self.assertNotIn(None, item.get_location().__dict__.values())
            self.assertTrue(item.get_weather())
            self.assertNotIn(None, item.get_weather().__dict__.values())

    def test_find_weather_by_coords(self):
        """
        Test feature: find currently observed weather for locations that are 
        nearby the specified coordinates
        """
        o2 = self.__owm.find_weather_by_coords(-2.15, 57.0)  # Scotland
        self.assertTrue(isinstance(o2, list))
        for item in o2:
            self.assertTrue(item, "")
            self.assertTrue(item.get_reception_time())
            self.assertTrue(item.get_location())
            self.assertNotIn(None, item.get_location().__dict__.values())
            self.assertTrue(item.get_weather())
            self.assertNotIn(None, item.get_weather().__dict__.values())   
        o1 = self.__owm.find_weather_by_coords(-2.15, 57.0, 2)  # Scotland
        self.assertTrue(isinstance(o1, list))
        self.assertEqual(2, len(o1))
        for item in o1:
            self.assertTrue(item)
            self.assertTrue(item.get_reception_time())
            self.assertTrue(item.get_location())
            self.assertNotIn(None, item.get_location().__dict__.values())
            self.assertTrue(item.get_weather())
            self.assertNotIn(None, item.get_weather().__dict__.values())
        
    def test_three_hours_forecast(self):
        """
        Test feature: get 3 hours forecast for a specific location
        """
        fc1 = self.__owm.three_hours_forecast("London,uk")
        fc2 = self.__owm.three_hours_forecast('Kiev')
        fc3 = self.__owm.three_hours_forecast('QmFoPIlbf')  #Shall be None
        self.assertTrue(fc1)
        f1 = fc1.get_forecast()
        self.assertTrue(f1)
        self.assertFalse(f1.get_reception_time() is None)
        self.assertTrue(f1.get_location())
        self.assertNotIn(None, f1.get_location().__dict__.values())
        for weather in f1:
            self.assertTrue(weather)
            self.assertNotIn(None, weather.__dict__.values())
        self.assertTrue(fc2)
        f2 = fc2.get_forecast()
        self.assertTrue(f2)
        self.assertFalse(f2.get_reception_time() is None)
        self.assertTrue(f2.get_location())
        self.assertNotIn(None, f2.get_location().__dict__.values())
        for weather in f2:
            self.assertTrue(weather)
            self.assertNotIn(None, weather.__dict__.values())
        self.assertFalse(fc3)
        
    def test_daily_forecast(self):
        """
        Test feature: get daily forecast for a specific location
        """
        fc1 = self.__owm.daily_forecast("London,uk")
        fc2 = self.__owm.daily_forecast('Kiev')
        fc3 = self.__owm.daily_forecast('QmFoPIlbf')  #Shall be None
        self.assertTrue(fc1)
        f1 = fc1.get_forecast()
        self.assertTrue(f1)
        self.assertFalse(f1.get_reception_time() is None)
        self.assertTrue(f1.get_location())
        self.assertNotIn(None, f1.get_location().__dict__.values())
        for weather in f1:
            self.assertTrue(weather)
            self.assertNotIn(None, weather.__dict__.values())
        self.assertTrue(fc2)
        f2 = fc2.get_forecast()
        self.assertTrue(f2)
        self.assertFalse(f2.get_reception_time() is None)
        self.assertTrue(f2.get_location())
        self.assertNotIn(None, f2.get_location().__dict__.values())
        for weather in f2:
            self.assertTrue(weather)
            self.assertNotIn(None, weather.__dict__.values())
        self.assertFalse(fc3)
        
    def test_weather_history(self):
        """
        Test feature: get weather history for a specific location
        """
        start_iso = "2013-09-06 09:20:00+00"
        start_unix = 1378459200L
        start_date = datetime(2013, 9, 6, 9, 20, 0)
        end_iso = "2013-09-06 20:26:40+00"
        end_unix = 1378499200L
        end_date = datetime(2013, 9, 6, 20, 26, 40)
        l1 = self.__owm.weather_history("London")
        self.assertTrue(l1)
        for weather in l1:
            self.assertTrue(weather)
            self.assertNotIn(None, weather.__dict__.values())
        l2 = self.__owm.weather_history('Kiev', start_unix, end_unix)
        self.assertTrue(l2)
        for weather in l2:
            self.assertTrue(weather)
            self.assertNotIn(None, weather.__dict__.values())
        l3 = self.__owm.weather_history('Rome', start_iso, end_iso)
        self.assertTrue(l3)
        for weather in l3:
            self.assertTrue(weather)
            self.assertNotIn(None, weather.__dict__.values())
        l4 = self.__owm.weather_history('Berlin', start_date, end_date)
        self.assertTrue(l4)
        for weather in l4:
            self.assertTrue(weather)
            self.assertNotIn(None, weather.__dict__.values())
        l5 = self.__owm.weather_history('QmFoPIlbf')  #Shall be None
        self.assertFalse(l5)

    def test_station_tick_history(self):
        """
        Test feature: get station tick weather history for a specific meteostation
        """
        sh1 = self.__owm.station_tick_history(39276)
        self.assertTrue(sh1)
        data1 = sh1.get_measurements()
        self.assertTrue(data1)
        self.assertFalse(0, len(data1))
        sh2 = self.__owm.station_tick_history(39276, limit=2)
        data2 = sh2.get_measurements()
        self.assertTrue(data2)
        self.assertFalse(len(data2) > 2)        
        sh3 = self.__owm.station_tick_history(987654) #Shall be None
        self.assertFalse(sh3)
        
    def test_station_hour_history(self):
        """
        Test feature: get station hour weather history for a specific meteostation
        """
        sh1 = self.__owm.station_hour_history(123)
        self.assertTrue(sh1)
        data1 = sh1.get_measurements()
        self.assertTrue(data1)
        self.assertFalse(0, len(data1))
        sh2 = self.__owm.station_hour_history(123, limit=2)
        data2 = sh2.get_measurements()
        self.assertTrue(data2)
        self.assertFalse(len(data2) > 2)        
        sh3 = self.__owm.station_hour_history(987654) #Shall be None
        self.assertFalse(sh3)
        
    def test_station_day_history(self):
        """
        Test feature: get station hour weather history for a specific meteostation
        """
        sh1 = self.__owm.station_day_history(123)
        self.assertTrue(sh1)
        data1 = sh1.get_measurements()
        self.assertTrue(data1)
        self.assertFalse(0, len(data1))
        sh2 = self.__owm.station_day_history(123, limit=2)
        data2 = sh2.get_measurements()
        self.assertTrue(data2)
        self.assertFalse(len(data2) > 2)        
        sh3 = self.__owm.station_day_history(987654) #Shall be None
        self.assertFalse(sh3)
        
if __name__ == "__main__":
    unittest.main()
