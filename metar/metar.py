import re
from datetime import datetime

class Metar(object):
    def __init__(self, message):
        self.raw_metar = message
        self.metar_header = None
        self.visibility = None
        self.wind = None
        self.temperature = None
        self.slp = None
        self.rwy_condition = None
        self.clouds = None
        self.ww = None
        self.conditions_list = []

    def cavok(self):
        if "CAVOK" in self.raw_metar:
            self.conditions_list.append("green")
            return "green"
        else:
            return "no cavok"

    def translate_month(self, month): # translator for
        months_dict = {"january": "января",
                       "february": "февраля",
                       "march": "марта",
                       "april": "апреля",
                       "may": "мая",
                       "june": "июня",
                       "july": "июля",
                       "august": "августа",
                       "septemper": "сентября",
                       "october": "октября",
                       "november": "ноября",
                       "december": "декабря"}

        if month.lower() in months_dict:
            return months_dict[month.lower()]
        else:
            return month


    def get_header(self):
        header = re.findall(r"\d{6}Z", self.raw_metar)
        day = header[0][0: 2]
        hour = header[0][2: 4]
        minutes = header[0][-3: -1]
        now = datetime.now()
        curr_month = now.strftime("%B") # getting current month

        header_output = day + " " + self.translate_month(curr_month) + " " + hour + ":" + minutes
        return header_output

    def clouds_heigth_check(self):
        try:
            cl_search = re.search(r"[FEW,SCT,BKN,OVC,SKG,NSC]+\d{3}", self.raw_metar)
            clouds = cl_search.group(0)
            clouds_heigth = re.findall(r"\d+", clouds)
            self.clouds = clouds_heigth
            for el in clouds_heigth:
                if el >= "001" and el <= "007":
                    self.conditions_list.append("yellow")
                    return "yellow"
                elif el < "001":
                    self.conditions_list.append("red")
                    return "red"
                else:
                    self.conditions_list.append("green")
                    return "green"
        except:
            self.conditions_list.append("no clouds heigth data")
            return "no clouds heigth data"

    def visibility_check(self):

        visibility = None
        try:
            viz_search = re.findall(r" \d+ ", self.raw_metar)
            for el in viz_search:
                visibility = el.strip()
                print(visibility)
            if int(visibility) < 1000 and int(visibility) > 200:
                self.conditions_list.append("yellow")
                return "yellow"
            elif int(visibility) < 200:
                self.conditions_list.append("red")
                return "red"
            else:
                self.conditions_list.append("green")
                return "green"
        except:
            self.conditions_list.append("no wind data")
            return "no wind data"

    def wind_check(self):
        try:
            wind_search = re.search(r"[\d\,VRB,G]+[MPS,KT]+", self.raw_metar)
            wind = wind_search.group(0)
            wind_speed_search = re.search(r"[\d]{2}[MPS,KT]+", wind)
            wind_speed = wind_speed_search.group(0)
            self.wind = wind_speed

            if "MPS" in wind_speed:
                mps_w_speed_search = re.search(r"\d+", wind_speed)
                mps_w_speed = int(mps_w_speed_search.group(0))
                if mps_w_speed >= 14 and mps_w_speed < 24:
                    self.conditions_list.append("yellow")
                    return "yellow"
                elif mps_w_speed >= 24:
                    self.conditions_list.append("red")
                    return "red"
                else:
                    self.conditions_list.append("green")
                    return "green"

            elif "KT" in wind_speed:
                kt_wind_speed_search = re.search(r"\d+", wind_speed)
                kt_wind_speed = int(kt_wind_speed_search.group(0))
                if kt_wind_speed >= 28 and kt_wind_speed < 48:
                    self.conditions_list.append("yellow")
                    return "yellow"
                elif kt_wind_speed >= 48:
                    self.conditions_list.append("red")
                    return "red"
                else:
                    self.conditions_list.append("green")
                    return "green"

            if "G" in wind_speed:
                if "MPS" in wind_speed:
                    gusts_search = re.search(r"[G]{1}\d+", wind_speed)
                    gusts = gusts_search.group(0)
                    mps_gusts = re.findall(r"\d+", gusts)
                    if int(mps_gusts) >= 18:
                        self.conditions_list.append("yellow")
                        return "yellow"
                    else:
                        self.conditions_list.append("green")
                        return "green"

                if "KT" in wind_speed:
                    gusts_search = re.search(r"[G]{1}\d+", wind_speed)
                    gusts = gusts_search.group(0)
                    kt_gusts = re.findall(r"\d+", gusts)
                    if int(kt_gusts) >= 35:
                        self.conditions_list.append("yellow")
                        return "yellow"
                    else:
                        self.conditions_list.append("green")
                        return "green"

        except:
            self.conditions_list.append("no wind data")
            return "no wind data"

    def ww_check(self):
        bad_weather_conditions = ['SQ', 'PO', 'FZFG', 'SHRA', 'SHSN', 'FZSHRA', 'FZDZ', 'PE', 'FLASHES', 'WS']
        very_bad_weather_conditions = ['TS', 'TSSN', 'TSRA', 'TSGR', 'TSGS', 'TSRAGR', 'TSDS', 'FC', 'GR', 'SQ', 'SS',
                                       'DS'
                                       ]
        try:
            for b_cond in bad_weather_conditions:
                for vb_cond in very_bad_weather_conditions:
                    if b_cond in self.raw_metar:
                        self.conditions_list.append("yellow")
                        return "yellow"
                    elif vb_cond in self.raw_metar:
                        self.conditions_list.append("red")
                        return "red"
                    else:
                        self.conditions_list.append("green")
                        return "green"
        except:
            self.conditions_list.append("no ww data")
            return "no ww data"

    def rwy_check(self):
        try:
            rwy_cond_search = re.search(r"[R]{1}[\d\L,R,C,/]+", self.raw_metar)
            rwy_cond = rwy_cond_search.group(0)
            rwy_cond_list = []
            for symbol in rwy_cond:
                rwy_cond_list.append(symbol)
            clutch = int(rwy_cond_list[-2] + rwy_cond_list[-1])
            self.rwy_condition = clutch
            if clutch >= 30 and clutch <= 40 or clutch == "93":
                self.conditions_list.append("yellow")
                return "yellow"
            elif clutch < 30 or clutch == "91" or clutch == "92":
                self.conditions_list.append("red")
                return "red"
            else:
                self.conditions_list.append("green")
                return "green"
        except:
            self.conditions_list.append("no rwy data")
            return "no rwy data"

    def analyze_metar(self):
        self.clouds_heigth_check()
        self.visibility_check()
        self.wind_check()
        self.ww_check()
        # self.rwy_check()
        return "finished"

    def count_delay_risk(self):
        if self.cavok == "green":  # check if CAVOK in metar code => return no delay
            return "0%"
        else:
            if "red" in self.conditions_list:
                return "100%"
            else:
                if self.conditions_list.count("yellow") >= 2:
                    return "30%"
                elif self.conditions_list.count("yellow") >= 4:
                    return "60%"
                else:
                    return "0%"