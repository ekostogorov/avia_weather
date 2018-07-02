import re


class Taf(object):
    def __init__(self, message):
        self.raw_taf = message
        self.header = None
        self.weather_groups = []
        self.taf_response = None

    def get_header(self):  # getting time of compile
        header = re.findall(r"[A-Z]{4} \d{6}Z", self.raw_taf)
        return header

    def get_weather_groups(self):  # divide TAF to groups
        date_list = re.findall(r"\d{4}\/\d{4}", self.raw_taf)
        weather_groups_list = []
        for i in range(len(date_list)):
            text = "{0}".format(i)
            weather_groups_list.append(text)

        weather_groups_dict = {}
        for x in range(len(date_list)):
            k = weather_groups_list[x]
            v = [date_list[x]]
            weather_groups_dict[k] = v

        for k, v in weather_groups_dict.items():
            index = self.raw_taf.index(v[0])
            v.append(index)

        groups_list = []
        try:
            for i in range(len(weather_groups_dict)):
                if i < len(weather_groups_dict):
                    groups_list.append(self.raw_taf[weather_groups_dict[str(i)][1]: weather_groups_dict[str(i + 1)][1]])
        except KeyError:
            groups_list.append(self.raw_taf[weather_groups_dict[str(len(weather_groups_dict) - 1)][1]:])

        self.weather_groups = groups_list
        return groups_list

    def parse_groups(self):  # parsing each weather group
        returning_dict = {}
        clouds_answer = None
        viz_answer = None
        wind_answer = None
        ww_answer = None
        rwy_answer = None
        cleaned_groups = []
        bad_weather_conditions = ['SQ', 'PO', 'FZFG', 'SHRA', 'SHSN', 'FZSHRA', 'FZDZ', 'PE', 'FLASHES', 'WS']
        very_bad_weather_conditions = ['TS', 'TSSN', 'TSRA', 'TSGR', 'TSGS', 'TSRAGR', 'TSDS', 'FC', 'GR', 'SQ', 'SS',
                                       'DS'
                                       ]
        for group in self.weather_groups:
            if len(group) != 0:
                cleaned_groups.append(group)
            else:
                pass

        for i in range(len(cleaned_groups)):
            response_list = []
            group_count = None

            header = re.findall(r"\d{4}\/\d{4}", cleaned_groups[i])

            # decoding clouds heigth in group
            try:
                clouds = re.findall(r"[FEW,SCT,BKN,OVC,SKG,NSC]+\d{3}", cleaned_groups[i])
                # clouds = cl_search.group(0)
                clouds_heigth = re.findall(r"\d+", str(clouds))
                # self.clouds = clouds_heigth
                for el in clouds_heigth:
                    if el >= "001" and el <= "007":
                        clouds_answer = "yellow"
                    elif el < "001":
                        clouds_answer = "red"
                    elif el > "007":
                        clouds_answer = "green"
                    else:
                        clouds_answer = "no cloud data"

            except:
                clouds_answer = "no cloud data"

            response_list.append(clouds_answer)

            try:
                viz_search = re.findall(r" \d+ ", cleaned_groups[i])
                for el in viz_search:
                    visibility = el.strip()

                if int(visibility) <= 1000 and int(visibility) > 200:
                    viz_answer = "yellow"
                elif int(visibility) < 200:
                    viz_answer = "red"
                elif int(visibility) > 1000:
                    viz_answer = "green"
                else:
                    viz_answer = "no visibility data"

            except:
                viz_answer = "no visibility data"

            response_list.append(viz_answer)

            try:
                header = re.findall(r"\d{4}\/\d{4}", cleaned_groups[i])
                wind_search = re.search(r"[\d\,VRB,G]+[MPS,KT]+", cleaned_groups[i])
                wind = wind_search.group(0)
                wind_speed_search = re.search(r"[\d]{2}[MPS,KT]+", wind)
                wind_speed = wind_speed_search.group(0)

                if "MPS" in wind_speed:
                    mps_w_speed_search = re.search(r"\d+", wind_speed)
                    mps_w_speed = int(mps_w_speed_search.group(0))
                    if mps_w_speed >= 14:
                        wind_answer = "yellow"
                    elif mps_w_speed >= 24:
                        wind_answer = "red"
                    elif mps_w_speed < 14:
                        wind_answer = "green"
                    else:
                        wind_answer = "no wind data"
                elif "KT" in wind_speed:
                    kt_wind_speed_search = re.search(r"\d+", wind_speed)
                    kt_wind_speed = int(kt_wind_speed_search.group(0))
                    if kt_wind_speed >= 28:
                        wind_answer = "yellow"
                    elif kt_wind_speed >= 48:
                        wind_answer = "red"
                    elif kt_wind_speed < 28:
                        wind_answer = "green"
                    else:
                        wind_answer = "no wind data"

                if "G" in wind_speed:
                    if "MPS" in wind_speed:
                        gusts_search = re.search(r"[G]{1}\d+", wind_speed)
                        gusts = gusts_search.group(0)
                        mps_gusts = re.findall(r"\d+", gusts)
                        if int(mps_gusts) >= 18:
                            wind_answer = "yellow"
                        elif int(mps_gusts) < 18:
                            wind_answer = "red"
                        else:
                            wind_answer = "no wind data"
            except:
                wind_answer = "no wind data"

            response_list.append(wind_answer)

            try:
                for b_cond in bad_weather_conditions:
                    if b_cond in cleaned_groups[i]:
                        ww_answer = "yellow"

                for vb_cond in very_bad_weather_conditions:
                    if vb_cond in cleaned_groups[i]:
                        ww_answer = "red"
            except:
                ww_answer = "no ww data"

            response_list.append(ww_answer)

            try:
                header = re.findall(r"\d{4}\/\d{4}", cleaned_groups[i])
                rwy_cond_search = re.search(r"[R]{1}[\d\L,R,C,/]+", cleaned_groups[i])
                rwy_cond = rwy_cond_search.group(0)
                rwy_cond_list = []
                for symbol in rwy_cond:
                    rwy_cond_list.append(symbol)
                clutch = int(rwy_cond_list[-2] + rwy_cond_list[-1])
                if clutch >= 30 and clutch <= 40 or clutch == "93":
                    rwy_answer = "yellow"
                elif clutch < 30 or clutch == "91" or clutch == "92":
                    rwy_answer = "red"
                else:
                    rwy_answer = "green"

            except:
                rwy_answer = "no rwy data"

            response_list.append(rwy_answer)

            if "red" in response_list:
                group_count = "100%"
            elif response_list.count("yellow") > 2:
                group_count = "50%"
            else:
                group_count = "0%"

            returning_dict[header[0]] = group_count

        self.taf_response = returning_dict  # output as {date : weather_response}
        return returning_dict