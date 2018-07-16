from datetime import datetime, timedelta
import calendar
import requests
import re
import json
import config

from metar import Metar
from taf import Taf
from getter import Getter

class AviaWeather(object):
    Metar = None
    Taf = None

    def __init__(self, metar, taf):
        self.Metar = metar
        self.Taf = taf

    def raw_metar(self, airport_code):
        return self.Metar.Raw(airport_code)

    def raw_taf(self, airport_code):
        return self.Taf.Raw(airport_code)

    def encoded_metar(self, airport_code):
        return self.Metar.Encoded(airport_code)

    def encoded_taf(self, airport_code):
        return self.Taf.Encoded(airport_code)