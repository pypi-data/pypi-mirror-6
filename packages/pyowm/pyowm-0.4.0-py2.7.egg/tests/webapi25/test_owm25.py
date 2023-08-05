#!/usr/bin/env python

"""
Test case for owm.py module.
Here we don't use mock objects because we don't want to rely on exeternal
mocking libraries; we use monkey patching instead.
Monkey patching pattern:
  1. Keep a reference to the original function to be patched
  2. Replace the original function with the mock version
  3. Call function and get results
  4. Restore the original function (if possible, before unittest assertions 
     because they might fail)
"""

import unittest
import time
from json_test_responses import OBSERVATION_JSON, SEARCH_RESULTS_JSON, \
    THREE_HOURS_FORECAST_JSON, DAILY_FORECAST_JSON, CITY_WEATHER_HISTORY_JSON, \
    STATION_TICK_WEATHER_HISTORY_JSON, STATION_WEATHER_HISTORY_JSON
from pyowm.webapi25.owm25 import OWM25
from pyowm.constants import OWM_API_VERSION, PYOWM_VERSION
from pyowm.utils import httputils
from pyowm.webapi25.forecast import Forecast
from pyowm.webapi25.observation import Observation
from pyowm.webapi25.weather import Weather
from pyowm.webapi25.location import Location
from pyowm.webapi25.forecaster import Forecaster
from pyowm.webapi25.stationhistory import StationHistory

class TestOWM25(unittest.TestCase):
    
    __test_instance = OWM25('test_API_key')
    
    # Mock functions
    def mock_httputils_call_API_returning_single_obs(self, API_subset_URL, 
                                                     params_dict, API_key):
        return OBSERVATION_JSON
    
    def mock_httputils_call_API_returning_multiple_obs(self, API_subset_URL, 
                                                     params_dict, API_key):
        return SEARCH_RESULTS_JSON
    
    def mock_httputils_call_API_returning_3h_forecast(self, API_subset_URL, 
                                                     params_dict, API_key):
        return THREE_HOURS_FORECAST_JSON
    
    def mock_httputils_call_API_returning_daily_forecast(self, API_subset_URL, 
                                                     params_dict, API_key):
        return DAILY_FORECAST_JSON
    
    def mock_httputils_call_API_returning_city_weather_history(self, 
                                                       API_subset_URL,
                                                       params_dict, API_key):
        return CITY_WEATHER_HISTORY_JSON

    def mock_httputils_call_API_returning_station_tick_weather_history(self, 
                                                       API_subset_URL,
                                                       params_dict, API_key):
        return STATION_TICK_WEATHER_HISTORY_JSON
    
    def mock_httputils_call_API_returning_station_hour_weather_history(self,
                                                       API_subset_URL,
                                                       params_dict, API_key):
        return STATION_WEATHER_HISTORY_JSON
    
    def mock_httputils_call_API_returning_station_day_weather_history(self,
                                                       API_subset_URL,
                                                       params_dict, API_key):
        return STATION_WEATHER_HISTORY_JSON
    
    # Tests
    def test_API_key_accessors(self):
        test_API_key = 'G097IueS-9xN712E'
        owm = OWM25()
        self.assertFalse(owm.get_API_key())
        owm.set_API_key(test_API_key)
        self.assertEqual(owm.get_API_key(), test_API_key)
        
    def test_get_API_version(self):
        self.assertEquals(OWM_API_VERSION, self.__test_instance.get_API_version())
        
    def test_get_version(self):
        self.assertEquals(PYOWM_VERSION, self.__test_instance.get_version())

    def test_weather_at(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_single_obs
        result = self.__test_instance.weather_at("London,uk")
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, Observation))
        self.assertTrue(result.get_reception_time())
        self.assertTrue(result.get_location())
        self.assertNotIn(None, result.get_location().__dict__.values())
        self.assertTrue(result.get_weather())
        self.assertNotIn(None, result.get_weather().__dict__.values())
    
    def test_weather_at_coords(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_single_obs
        result = self.__test_instance.weather_at_coords(-2.15,57.0)
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, Observation))
        self.assertTrue(result.get_reception_time())
        self.assertTrue(result.get_location())
        self.assertNotIn(None, result.get_location().__dict__.values())
        self.assertTrue(result.get_weather())
        self.assertNotIn(None, result.get_weather().__dict__.values())

    def test_weather_at_coords_fails_when_coordinates_out_of_bounds(self):
        """
        Test failure when providing: lon < -180, lon > 180, lat < -90, lat > 90
        """
        self.assertRaises(ValueError, OWM25.weather_at_coords, \
                          self.__test_instance, -200.0, 43.7)
        self.assertRaises(ValueError, OWM25.weather_at_coords, \
                          self.__test_instance, 200.0, 43.7)
        self.assertRaises(ValueError, OWM25.weather_at_coords, \
                          self.__test_instance, 2.5, -200)
        self.assertRaises(ValueError, OWM25.weather_at_coords, \
                          self.__test_instance, 2.5, 200)
        
    def test_find_weather_by_name(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_multiple_obs
        result = self.__test_instance.find_weather_by_name("London","accurate")
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, list))
        self.assertEqual(2, len(result))
        for item in result:
            self.assertTrue(item)
            self.assertTrue(item.get_reception_time())
            self.assertTrue(item.get_location())
            self.assertNotIn(None, item.get_location().__dict__.values())
            self.assertTrue(item.get_weather())
            self.assertNotIn(None, item.get_weather().__dict__.values())
        
    def test_find_weather_by_name_fails_with_wrong_params(self):
        self.assertRaises(ValueError, OWM25.find_weather_by_name, \
                          self.__test_instance, "London", "x")
        self.assertRaises(ValueError, OWM25.find_weather_by_name, \
                          self.__test_instance, "London", "accurate", -5)

    def test_find_weather_by_coords(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_multiple_obs
        result = self.__test_instance.find_weather_by_coords(-2.15,57.0)
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, list))
        for item in result:
            self.assertTrue(item)
            self.assertTrue(item.get_reception_time())
            self.assertTrue(item.get_location())
            self.assertNotIn(None, item.get_location().__dict__.values())
            self.assertTrue(item.get_weather())
            self.assertNotIn(None, item.get_weather().__dict__.values())
        
    def test_find_weather_by_coords_fails_when_coordinates_out_of_bounds(self):
        """
        Test failure when providing: lon < -180, lon > 180, lat < -90, lat > 90
        """
        self.assertRaises(ValueError, OWM25.find_weather_by_coords, \
                          self.__test_instance, -200.0, 43.7)
        self.assertRaises(ValueError, OWM25.find_weather_by_coords, \
                          self.__test_instance, 200.0, 43.7)
        self.assertRaises(ValueError, OWM25.find_weather_by_coords, \
                          self.__test_instance, 2.5, -200)
        self.assertRaises(ValueError, OWM25.find_weather_by_coords, \
                          self.__test_instance, 2.5, 200)
        
    def test_find_weather_by_coords_fails_with_wrong_params(self):
        self.assertRaises(ValueError, OWM25.find_weather_by_coords, \
                          self.__test_instance, 20.0, 43.7, -3)

    def test_three_hours_forecast(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_3h_forecast
        result = self.__test_instance.three_hours_forecast("London,uk")
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, Forecaster))        
        forecast = result.get_forecast()
        self.assertTrue(isinstance(forecast, Forecast))
        self.assertTrue(forecast.get_interval())
        self.assertTrue(forecast.get_reception_time())
        self.assertTrue(isinstance(forecast.get_location(), Location))
        self.assertEqual(1, len(forecast))
        for weather in forecast:
            self.assertTrue(isinstance(weather, Weather))
            self.assertNotIn(None, weather.__dict__.values())
            
    def test_daily_forecast(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_daily_forecast
        result = self.__test_instance.daily_forecast("London,uk")
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, Forecaster))
        forecast = result.get_forecast()
        self.assertTrue(isinstance(forecast, Forecast))
        self.assertTrue(forecast.get_interval())
        self.assertTrue(forecast.get_reception_time())
        self.assertTrue(isinstance(forecast.get_location(), Location))
        self.assertEqual(1, len(forecast))
        for weather in forecast:
            self.assertTrue(isinstance(weather, Weather))
            self.assertNotIn(None, weather.__dict__.values())
            
    def test_daily_forecast_fails_with_wrong_params(self):
        self.assertRaises(ValueError, OWM25.daily_forecast, self.__test_instance, \
                          "London,uk", -3)
        
    def test_weather_history(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_city_weather_history
        result = self.__test_instance.weather_history("London,uk")
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, list))
        for weather in result:
            self.assertTrue(isinstance(weather, Weather))
            self.assertNotIn(None, weather.__dict__.values())
        
    def test_weather_history_fails_with_unordered_time_boundaries(self):
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                          "London,uk", "2013-09-06 20:26:40+00", 
                          "2013-09-06 09:20:00+00")
        
    def test_weather_history_fails_with_time_boundaries_in_the_future(self):
        current_time = long(time.time())
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                          "London,uk", current_time + 1000L, 
                          current_time + 2000L)
        
    def test_weather_history_fails_with_wrong_time_boundaries(self):        
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                          "London,uk", None, 1234567L)
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                          "London,uk", 1234567L, None )
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                          "London,uk", 1234567L, None )
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                          "London,uk", -1234567L, None )
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                  "London,uk", None, -1234567L)
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                  "London,uk", -999L, -888L)
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                  "London,uk", "test", 1234567L)
        self.assertRaises(ValueError, OWM25.weather_history, self.__test_instance, \
                  "London,uk", 1234567L, "test")
        
    def test_station_tick_history(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_station_tick_weather_history
        result = self.__test_instance.station_tick_history(1234, limit=4)
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, StationHistory))
        self.assertTrue(isinstance(result.get_measurements(), dict))
        
    def test_station_tick_history_fails_with_wrong_params(self):
        self.assertRaises(ValueError, OWM25.station_tick_history, self.__test_instance, \
                          1234, -3)
        
    def test_station_hour_history(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_station_hour_weather_history
        result = self.__test_instance.station_hour_history(1234, limit=4)
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, StationHistory))
        self.assertTrue(isinstance(result.get_measurements(), dict))
        
    def test_station_hour_history_fails_with_wrong_params(self):
        self.assertRaises(ValueError, OWM25.station_hour_history, self.__test_instance, \
                          1234, -3)
        
    def test_station_day_history(self):
        ref_to_original_call_API = httputils.call_API
        httputils.call_API = self.mock_httputils_call_API_returning_station_day_weather_history
        result = self.__test_instance.station_day_history(1234, limit=4)
        httputils.call_API = ref_to_original_call_API
        self.assertTrue(isinstance(result, StationHistory))
        self.assertTrue(isinstance(result.get_measurements(), dict))
        
    def test_station_day_history_fails_with_wrong_params(self):
        self.assertRaises(ValueError, OWM25.station_day_history, self.__test_instance, \
                          1234, -3)
 
if __name__ == "__main__":
    unittest.main()