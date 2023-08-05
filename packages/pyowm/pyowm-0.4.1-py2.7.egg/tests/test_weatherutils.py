#!/usr/bin/env python

"""
Test case for weatherutils.py module
"""

import unittest
from pyowm.weather import Weather
from pyowm.utils import weatherutils
from pyowm.exceptions.not_found_error import NotFoundError

class TestWeatherUtils(unittest.TestCase):
    
    __test_time_low = 1379090800L
    __test_time_low_iso = "2013-09-13 16:46:40+00"
    __test_time_high = 1379361400L
    __test_time_high_iso = "2013-09-16 19:56:40+00"

    __test_weather_rainsnow = Weather(__test_time_low, 1378496400, 1378449600, 67, 
            {"all": 30}, {"all": 0}, {"deg": 252.002, "speed": 4.100}, 57, 
            {"press": 1030.119, "sea_level": 1038.589},
            {"temp": 294.199, "temp_kf": -1.899, "temp_max": 296.098, 
                "temp_min": 294.199
            },
            u"Rain", u"Light rain", 500, u"10d")
    __test_weather_sun = Weather(__test_time_high, 1378496480, 1378449510, 5, 
            {"all": 0}, {"all": 0}, {"deg": 103.4, "speed": 1.2}, 12, 
            {"press": 1090.119, "sea_level": 1078.589},
            {"temp": 299.199, "temp_kf": -1.899, "temp_max": 301.0, 
             "temp_min": 297.6
             },
            u"Clear", u"Sky is clear", 800, u"01d")
    __test_weathers = [__test_weather_rainsnow, __test_weather_sun]

    def test_status_matches_any(self):
        self.assertTrue(weatherutils.status_matches_any(['rain'],
                                                    self.__test_weather_rainsnow))
        self.assertFalse(weatherutils.status_matches_any(['sunnyday'],
                                                    self.__test_weather_rainsnow))

    def test_statuses_match_any(self):
        self.assertTrue(weatherutils.statuses_match_any(['rain'],
                                                    self.__test_weathers))
        self.assertFalse(weatherutils.statuses_match_any(['sandstorm'],
                                                    self.__test_weathers))

    def test_filter_by_matching_statuses(self):
        self.assertEqual([self.__test_weather_rainsnow], 
             weatherutils.filter_by_matching_statuses(['rain'],
                                          self.__test_weathers))
        self.assertEqual([self.__test_weather_sun], 
             weatherutils.filter_by_matching_statuses(['clear'],
                                          self.__test_weathers))
        self.assertFalse(weatherutils.filter_by_matching_statuses(['test'],
                                          self.__test_weathers))

    def test_find_closest_weather(self):
        self.assertEqual(self.__test_weather_rainsnow, 
                         weatherutils.find_closest_weather(self.__test_weathers,
                                                   self.__test_time_low + 200L))
        self.assertEqual(self.__test_weather_sun, 
                         weatherutils.find_closest_weather(self.__test_weathers,
                                                   self.__test_time_high - 200L))
        
    def test_find_closest_weather_with_empty_list(self):
        self.assertFalse(weatherutils.find_closest_weather([],
                                                   self.__test_time_low + 200L))
        
    def test_find_closest_fails_when_unixtime_not_in_coverage(self):
        self.assertRaises(NotFoundError, weatherutils.find_closest_weather,
                          self.__test_weathers, self.__test_time_high + 200L) 

    def test_is_in_coverage(self):
        self.assertTrue(weatherutils.is_in_coverage(self.__test_time_low + 200L,
                                                    self.__test_weathers))
        self.assertTrue(weatherutils.is_in_coverage(self.__test_time_high - 200L,
                                                    self.__test_weathers))
        self.assertTrue(weatherutils.is_in_coverage(self.__test_time_low,
                                                    self.__test_weathers))
        self.assertTrue(weatherutils.is_in_coverage(self.__test_time_high,
                                                    self.__test_weathers))
        self.assertFalse(weatherutils.is_in_coverage(self.__test_time_low - 200L,
                                                    self.__test_weathers))
        self.assertFalse(weatherutils.is_in_coverage(self.__test_time_high + 200L,
                                                    self.__test_weathers))
    
    def test_is_in_coverage_with_empty_list(self):
        self.assertFalse(weatherutils.is_in_coverage(1234567L, []))

if __name__ == "__main__":
    unittest.main()