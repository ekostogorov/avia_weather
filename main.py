from datetime import datetime, timedelta
import calendar
import requests
import re
import json
import config

from metar import Metar
from taf import Taf

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


def metar_output(metar_object):
    date = metar_object.get_header()
    metar_object.analyze_metar()
    delay_risk = metar_object.count_delay_risk() # getting METAR risk of delay

    output = "Сейчас риск задержки вылета {0} (на основе метеоданных от {1})".format(delay_risk, date)
    return {"output" : output, "delay" : delay_risk}



def taf_output(taf_object):
    groups_output_text_list = []
    taf_object.get_weather_groups()
    parsed_groups = taf_object.parse_groups()  # getting parsed weather groups

    now = datetime.now()
    curr_month = now.strftime("%B")  # getting current month
    curr_day = now.strftime("%d")  # getting current day
    curr_month_days = calendar.monthrange(now.year, now.month)[1]

    for header, delay_risk in parsed_groups.items():
        start_date_str = re.findall(r"\d{4}\/", header)
        end_date_str = re.findall(r"/\d{4}", header)
        start_hour = start_date_str[0][-3: -1]
        start_day = start_date_str[0][0: 2]
        end_hour = end_date_str[0][-2:]
        end_day = end_date_str[0][1: 3]

        if curr_day == curr_month_days and end_day == "01":  # check if today is the last day of month
            curr_month = (datetime.now() + timedelta(days=30)).strftime("%B")  # replace curr month => next month
        else:
            pass

        groups_output_text_list.append(group_output)

    return groups_output_text_list

# extra function for JSON outut of METAR + TAF
def taf_output_json(taf_object):
    returning_list = []
    taf_object.get_weather_groups()
    parsed_groups = taf_object.parse_groups()  # getting parsed weather groups

    now = datetime.now()
    curr_month = now.strftime("%m")  # getting current month
    curr_day = now.strftime("%d")  # getting current day
    curr_month_days = calendar.monthrange(now.year, now.month)[1]
    curr_year = now.strftime("%Y")

    count = 0
    for header, delay_risk in parsed_groups.items():
        count += 1
        start_date_str = re.findall(r"\d{4}\/", header)
        end_date_str = re.findall(r"/\d{4}", header)
        start_hour = start_date_str[0][-3: -1]
        start_day = start_date_str[0][0: 2]
        end_hour = end_date_str[0][-2:]
        end_day = end_date_str[0][1: 3]

        if curr_day == curr_month_days and end_day == "01":  # check if today is the last day of month
            curr_month = (datetime.now() + timedelta(days=30)).strftime("%B")  # replace curr month => next month
        else:
            pass

        group_output = {"id" : str(count), "start": curr_year + "-" + curr_month + "-" + start_day + "T" + start_hour +
                     ":00:00", "end": curr_year + "-" + curr_month + "-" + end_day + "T" +
                                      end_hour + ":00:00", "content": delay_risk, "className" : "green"}
        returning_list.append(group_output)

    return json.dumps(returning_list)